# Copyright (c) 2010-2015, GEM Foundation.
#
# NRML is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# NRML is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with NRML.  If not, see <http://www.gnu.org/licenses/>.


"""These parsers read NRML XML files and produce object representations of the
data.

"""

from collections import OrderedDict
from collections import namedtuple
from lxml import etree

NAMESPACE = 'http://openquake.org/xmlns/nrml/0.5'
GML_NAMESPACE = 'http://www.opengis.net/gml'

HazardCurveData = namedtuple('HazardCurveData', 'location poes')
Location = namedtuple('Location', 'x y')


def iterparse_tree(source, events=('start', 'end')):
    tree = etree.iterparse(source, events=events)
    return tree


class HazardCurveModel(object):
    """
    Simple container for hazard curve objects. The accepted arguments
    are::

        * investigation_time
        * imt
        * imls
        * statistics
        * quantile_value
        * sa_period
        * sa_damping
        * data_iter (optional), an iterable returning pairs with the form
          (poes_array, location).
    """

    def __init__(self, **metadata):
        self._data_iter = metadata.pop('data_iter', ())
        self.metadata = metadata
        vars(self).update(metadata)

    def __iter__(self):
        return self._data_iter


class GMFScenarioParser(object):

    _GMF_TAG = '{%s}gmf' % NAMESPACE
    _NODE_TAG = '{%s}node' % NAMESPACE

    def __init__(self, source):
        self.source = source

    def parse(self):
        """
        Parse the source XML content for a GMF scenario.
        :returns:
            an iterable over triples (imt, gmvs, location)
        """
        tree = iterparse_tree(self.source, events=('end',))
        gmf = OrderedDict()  # (imt, location) -> gmvs
        point_value_list = []
        for _, element in tree:
            a = element.attrib
            if element.tag == self._NODE_TAG:
                point_value_list.append(
                    ['POINT(%(lon)s %(lat)s)' % a, a['gmv']])
            elif element.tag == self._GMF_TAG:
                imt = a['IMT']
                try:
                    imt += '(%s)' % a['saPeriod']
                except KeyError:
                    pass
                for point, value in point_value_list:
                    try:
                        values = gmf[point, imt]
                    except KeyError:
                        gmf[point, imt] = [value]
                    else:
                        values.append(value)
                point_value_list = []
        for (location, imt), gmvs in gmf.iteritems():
            yield imt, '{%s}' % ','.join(gmvs), location


class HazardCurveXMLParser(object):
    _CURVES_TAG = '{%s}hazardCurves' % NAMESPACE
    _CURVE_TAG = '{%s}hazardCurve' % NAMESPACE

    def __init__(self, source):
        self.source = source

    def parse(self):
        """
        Parse the source XML content for a hazard curve.
        :returns:
            Populated :class:`HazardCurveModel` object
        """
        tree = iterparse_tree(self.source)
        hc_iter = self._parse(tree)
        header = hc_iter.next()
        return HazardCurveModel(data_iter=hc_iter, **header)

    def _parse(self, tree):
        header = OrderedDict()
        for event, element in tree:
            if element.tag == self._CURVES_TAG and event == 'start':
                a = element.attrib
                header['statistics'] = a.get('statistics')
                header['quantile_value'] = a.get('quantileValue')
                header['smlt_path'] = a.get('sourceModelTreePath')
                header['gsimlt_path'] = a.get('gsimTreePath')
                header['imt'] = a['IMT']
                header['investigation_time'] = a['investigationTime']
                header['sa_period'] = a.get('saPeriod')
                header['sa_damping'] = a.get('saDamping')
                header['imls'] = map(float, element[0].text.split())
                yield header
            elif element.tag == self._CURVE_TAG and event == 'end':
                point, poes = element
                x, y = [float(v) for v in point[0].text.split()]
                location = Location(x, y)
                poes_array = map(float, poes.text.split())
                yield HazardCurveData(location, poes_array)
