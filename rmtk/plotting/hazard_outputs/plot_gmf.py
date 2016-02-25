#!/usr/bin/env python
# LICENSE
#
# Copyright (c) 2015, GEM Foundation.
#
# The nrml_convertes is free software: you can redistribute
# it and/or modify it under the terms of the GNU Affero General Public
# License as published by the Free Software Foundation, either version
# 3 of the License, or (at your option) any later version.
#
# You should have received a copy of the GNU Affero General Public License
# along with OpenQuake. If not, see <http://www.gnu.org/licenses/>
#
# DISCLAIMER
#
# The software nrml_convertes provided herein is released as a prototype
# implementation on behalf of scientists and engineers working within the GEM
# Foundation (Global Earthquake Model).
#
# It is distributed for the purpose of open collaboration and in the
# hope that it will be useful to the scientific, engineering, disaster
# risk and software design communities.
#
# The software is NOT distributed as part of GEM's OpenQuake suite
# (http://www.globalquakemodel.org/openquake) and must be considered as a
# separate entity. The software provided herein is designed and implemented
# by scientific staff. It is not developed to the design standards, nor
# subject to same level of critical review by professional software
# developers, as GEM's OpenQuake software suite.
#
# Feedback and contribution to the software is welcome, and can be
# directed to the hazard scientific staff of the GEM Model Facility
# (hazard@globalquakemodel.org).
#
# The nrml_convertes is therefore distributed WITHOUT ANY WARRANTY; without
# even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
# PURPOSE. See the GNU General Public License for more details.
#
# The GEM Foundation, and the authors of the software, assume no liability for
# use of the software.
"""
RMTK Tools for the parsing and visualisation of hazard data
"""

import numpy as np
from scipy.stats import gmean
from collections import OrderedDict
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from matplotlib.colors import LogNorm, Normalize
from rmtk.parsers.hazard_parsers import iterparse_tree

NRML = 'http://openquake.org/xmlns/nrml/0.5'
GML = 'http://www.opengis.net/gml'

GMF_TAG = '{%s}gmf' % NRML
NODE_TAG = '{%s}node' % NRML


def parse_nrml_gmf_map(nrml_gmf_map):
    """
    Parse the source XML content for a GMF scenario.
    :returns:
        an iterable over triples (imt, gmvs, location)
    """

    tree = iterparse_tree(nrml_gmf_map, events=('end',))
    gmf = OrderedDict()
    point_value_list = []

    for _, element in tree:
        a = element.attrib

        if element.tag == NODE_TAG:
            point_value_list.append(
                ['POINT(%(lon)s %(lat)s)' % a, a['gmv']])
        elif element.tag == GMF_TAG:
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

    gmf_by_imt = dict()
    for (location, imt), gmvs in gmf.iteritems():
        if imt not in gmf_by_imt:
            gmf_by_imt[imt] = []

        location_str = location.lstrip('POINT(').rstrip(')').split(' ')
        [location_str.append(x) for x in gmvs]
        gmf_by_imt[imt].append(np.array(location_str, dtype=float))

    return gmf_by_imt


class GMFMap(object):
    """
    Class to hold and plot gmf map information
    """
    def __init__(self, input_filename, gmf_index=None):
        """
        Instantiate and parse input file
        """
        self.gmf_by_imt = parse_nrml_gmf_map(input_filename)
        self.no_sites = len(self.gmf_by_imt[self.gmf_by_imt.keys()[0]])
        self.data = dict()

        if not gmf_index:  # median
            for imt, values in self.gmf_by_imt.iteritems():
                self.data[imt] = np.zeros((self.no_sites, 3))
                for i, site in enumerate(values):
                    lon, lat = site[:2]
                    gmv = gmean(site[2:])
                    self.data[imt][i, :] = [lon, lat, gmv]
        else:
            for imt, values in self.gmf_by_imt.iteritems():
                self.data[imt] = np.zeros((self.no_sites, 3))
                for i, site in enumerate(values):
                    lon, lat = site[:2]
                    gmv = site[2:][gmf_index-1]  # strarting from 1
                    self.data[imt][i, :] = [lon, lat, gmv]

        self.box = dict()
        self.box["lon_1"] = min(self.data[imt][:, 0])
        self.box["lon_2"] = max(self.data[imt][:, 0])
        self.box["lat_1"] = min(self.data[imt][:, 1])
        self.box["lat_2"] = max(self.data[imt][:, 1])
        self.box["lat_length"] = abs(self.box["lat_2"] - self.box["lat_1"])
        self.box["lon_length"] = abs(self.box["lon_2"] - self.box["lon_1"])

    def plot(self, log_scale=False, marker_size=20,
             output_file=None, dpi=300, fmt="png", papertype="a4"):
        """

        """
        for imt, values in self.data.iteritems():
            self.plot_by_imt(self.box, values, imt, log_scale, marker_size, output_file, dpi, fmt, papertype)

    @staticmethod
    def plot_by_imt(box, values, imt, log_scale, marker_size, output_file, dpi, fmt, papertype):

        plt.figure(figsize=(8, 6), dpi=300, facecolor='w',
                   edgecolor='k')
        map_func = Basemap(llcrnrlon=box["lon_1"],
                           llcrnrlat=box["lat_1"],
                           urcrnrlon=box["lon_2"],
                           urcrnrlat=box["lat_2"],
                           projection='mill',
                           resolution='i')
        x, y = map_func(values[:, 0], values[:, 1])
        #map_func.shadedrelief()
        map_func.drawcoastlines(linewidth=0.25, color="gray")
        map_func.drawcountries(linewidth=1.00, color="gray")
        map_func.drawstates(linewidth=0.25, color="gray")
        map_func.drawmapboundary(fill_color='lightblue')
        map_func.fillcontinents(color='white', lake_color='lightblue')
        if log_scale:
            scale = LogNorm()
        else:
            scale = Normalize()

        plt.scatter(x, y, s=marker_size, c=values[:, 2], zorder=4, cmap='bwr', edgecolor='None', norm=scale)

        cbar = map_func.colorbar(location='right', pad="5%")
        if imt == "PGV":
            imt_units = "cm/s"
        else:
            imt_units = "g"
        cbar.set_label("{:s} ({:s})".format(imt, imt_units))

        if box["lat_length"] < 2:
            parallels = np.arange(0., 81, 0.25)
        else:
            parallels = np.arange(0., 81, 1.00)
        # labels = [left,right,top,bottom]
        map_func.drawparallels(parallels, labels=[True, False, True, False])
        if box["lon_length"] < 2:
            meridians = np.arange(0., 360, 0.25)
        else:
            meridians = np.arange(0., 360, 1.00)
        map_func.drawmeridians(meridians, labels=[True, False, False, True])

        title_string = "Ground motion field"
        plt.title(title_string, fontsize=16)

        plt.show()
        if output_file:
            plt.savefig(output_file, dpi=dpi, format=fmt, papertype="a4")

