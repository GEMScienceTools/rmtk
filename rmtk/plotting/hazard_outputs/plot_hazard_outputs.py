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
import os
import numpy as np
from lxml import etree
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from matplotlib.colors import LogNorm, Normalize
from rmtk.parsers.hazard_parsers import HazardCurveXMLParser


NRML='{http://openquake.org/xmlns/nrml/0.4}'
GML='{http://www.opengis.net/gml}'


def _set_curves_matrix(hcm):
    """
    Store locations and poes in :class:`openquake.nrml.models.HazardCurveModel`
    in numpy array.
    """
    curves = []
    for loc, poes in hcm:
        row = [loc.x, loc.y]
        row.extend(poes)
        curves.append(row)

    return np.array(curves)

def _set_header(hcm):
    """
    Save metadata in :class:`openquake.nrml.models.HazardCurveModel`
    in a string to be used as header
    """
    header = ','.join(
        ['%s=%s' % (k,v) for k,v in hcm.metadata.items()
        if v is not None and k != 'imls']
    )
    header = '# ' + header
    header += '\nlon,lat,'+','.join([str(iml) for iml in hcm.metadata['imls']])

    return header


class HazardCurve(object):
    """
    Class to hold hazard curve information
    """
    def __init__(self, input_filename):
        """
        Read in the hazard curve from the filename
        """
        self.hcm = HazardCurveXMLParser(input_filename).parse()
        self.data = _set_curves_matrix(self.hcm)
        self.loc_list = ["{:.6f}|{:.6f}".format(row[0], row[1])
                         for row in self.data]

    def plot(self, idx, output_file=None, dpi=300, fmt="png", papertype="a4"):
        """
        Creates the hazard curve plot
        """
        if ("PGA" in self.hcm.metadata["imt"]) or\
            ("SA" in self.hcm.metadata["imt"]):
            imt_units = "g"
        else:
            imt_units = "cm/s"

        if isinstance(idx, int):
            longitude, latitude, curve = self._get_curve_from_id(idx)
        elif isinstance(idx, str):
            longitude, latitude, curve = self._get_curve_from_string(idx)
        else:
            raise ValueError("Index not recognised!")

        fig = plt.figure(figsize=(7, 5))
        #fig.set_tight_layout(True)
        plt.loglog(self.hcm.metadata["imls"], curve, 'bo-', linewidth=2.0)
        plt.xlabel("%s (%s)" %(self.hcm.metadata["imt"], imt_units),
                   fontsize=14)
        plt.ylabel("Probability of Being Exceeded in %s years" %
                   self.hcm.metadata["investigation_time"], fontsize=14)
        if longitude < 0.0:
            long_ind = "W"
        else:
            long_ind = "E"
        if latitude < 0.0:
            lat_ind = "S"
        else:
            lat_ind = "N"
        plt.title("Location: %12.6f %s, %12.6f %s" %(
            np.abs(longitude), long_ind, np.abs(latitude), lat_ind))
        if output_file:
            plt.savefig(output_file, dpi=dpi, format=fmt, papertype="a4")

    def _get_curve_from_id(self, idx):
        """
        Returns the curve based on the location in the array
        """
        return self.data[idx,0], self.data[idx, 1], self.data[idx, 2:]

    def _get_curve_from_string(self, idx):
        """
        Returns the curve based on the location defined by a string
        """
        if idx in self.loc_list:
            idx = self.loc_list.index(idx)
        else:
            raise ValueError("Location index %s not in curve list" % idx)
        return self.data[idx,0], self.data[idx, 1], self.data[idx, 2:]


def parse_nrml_uhs_curves(nrml_uhs_map):
    """
    Parse NRML uhs file.
    """
    metadata = {}
    periods = None
    values = []

    parse_args = dict(source=nrml_uhs_map)
    for _, element in etree.iterparse(**parse_args):
        if element.tag == '%suniformHazardSpectra' % NRML:
            a = element.attrib
            metadata['statistics'] = a.get('statistics')
            metadata['quantile_value'] = a.get('quantileValue')
            metadata['smlt_path'] = a.get('sourceModelTreePath')
            metadata['gsimlt_path'] = a.get('gsimTreePath')
            metadata['investigation_time'] = a['investigationTime']
            metadata['poe'] = a.get('poE')
        elif element.tag == '%speriods' % NRML:
            periods = map(float, element.text.split())
        elif element.tag == '%suhs' % NRML:
            lon, lat = map(
                float, element.find('%sPoint/%spos' % (GML, GML)).text.split()
            )
            imls = map(float, element.find('%sIMLs' % NRML).text.split())

            uhs = [lon, lat]
            uhs.extend(imls)
            values.append(uhs)

    return metadata, periods, np.array(values)


class UniformHazardSpectra(HazardCurve):
    """
    Class to hold and plot uniform hazard spectra information
    """
    def __init__(self, input_filename):
        """
        Instantiation and parsing
        """
        self.metadata, self.periods, self.data = parse_nrml_uhs_curves(
            input_filename)
        self.loc_list = ["{:.6f}|{:.6f}".format(row[0], row[1])
                         for row in self.data]


    def plot(self, idx, output_file=None, dpi=300, fmt="png",
            papertype="a4"):
        """
        Creates the UHS plot
        """
        if not self.metadata["statistics"]:
            self.metadata["statistics"] = ""
        if isinstance(idx, int):
            longitude, latitude, spectrum = self._get_curve_from_id(idx)
        elif isinstance(idx, str):
            longitude, latitude, spectrum = self._get_curve_from_string(idx)
        else:
            raise ValueError("Index not recognised!")

        fig = plt.figure(figsize=(7, 5))
        #fig.set_tight_layout(True)
        plt.plot(self.periods, spectrum, 'bo-', linewidth=2.0)
        plt.xlabel("Period (s)", fontsize=14)
        plt.ylabel("Spectral Acceleration (g)", fontsize=14)
        plt.grid(b=True, color='0.66', linestyle="--")

        if longitude < 0.0:
            long_ind = "W"
        else:
            long_ind = "E"
        if latitude < 0.0:
            lat_ind = "S"
        else:
            lat_ind = "N"
        title_string_upper = "{:s} UHS with a {:s} PoE in {:s} Years\n".format(
             self.metadata["statistics"],
             self.metadata["poe"],
             self.metadata["investigation_time"])
        title_string_lower = "Location: {:.6f}{:s}, {:.6f}{:s}".format(
            np.abs(longitude), long_ind, np.abs(latitude), lat_ind)
        plt.title(title_string_upper + title_string_lower, fontsize=16)
        if output_file:
            plt.savefig(output_file, dpi=dpi, format=fmt, papertype="a4")


def parse_nrml_hazard_map(nrml_hazard_map):
    """
    Parse NRML hazard map file.
    """
    metadata = {}
    values = []

    parse_args = dict(source=nrml_hazard_map)
    for _, element in etree.iterparse(**parse_args):
        if element.tag == '%shazardMap' % NRML:
            a = element.attrib
            metadata['smlt_path'] = a.get('sourceModelTreePath')
            metadata['gsimlt_path'] = a.get('gsimTreePath')
            metadata['imt'] = a['IMT']
            metadata['investigation_time'] = a['investigationTime']
            metadata['poe'] = a.get('poE')
            metadata['sa_period'] = a.get('saPeriod')
            metadata['sa_damping'] = a.get('saDamping')
            metadata['statistics'] = a.get('statistics')
            metadata['quantile_value'] = a.get('quantileValue')
        elif element.tag == '%snode' % NRML:
            a = element.attrib
            values.append(
                map(float, [a.get('lon'), a.get('lat'), a.get('iml')])
            )

    return metadata, np.array(values)


class HazardMap(object):
    """
    Class to hold and plot hazard map information
    """
    def __init__(self, input_filename):
        """
        Instantiate and parse input file
        """
        self.metadata, self.data = parse_nrml_hazard_map(input_filename)
        self.box = {}
        self.box["lon_1"] = min(self.data[:,0])
        self.box["lon_2"] = max(self.data[:,0])
        self.box["lat_1"] = min(self.data[:,1])
        self.box["lat_2"] = max(self.data[:,1])
        self.box["lat_length"] = abs(self.box["lat_2"] - self.box["lat_1"])
        self.box["lon_length"] = abs(self.box["lon_2"] - self.box["lon_1"])

    def plot(self, log_scale=False, marker_size=20,
            output_file=None, dpi=300, fmt="png", papertype="a4"):
        """

        """
        plt.figure(figsize=(8, 6), dpi=300, facecolor='w',
                   edgecolor='k')
        map = Basemap(llcrnrlon=self.box["lon_1"], llcrnrlat=self.box["lat_1"],
            urcrnrlon=self.box["lon_2"], urcrnrlat=self.box["lat_2"], projection='mill',
            resolution='i')
        x, y = map(self.data[:, 0], self.data[:, 1])
        #map.shadedrelief()
        map.drawcoastlines(linewidth=0.25)
        map.drawcountries(linewidth=0.25)
        map.drawstates(linewidth=0.25)
        map.drawmapboundary(fill_color='aqua')
        map.fillcontinents(color='white',lake_color='aqua')
        if log_scale:
            scale = LogNorm()
        else:
            scale  = Normalize()

        plt.scatter(x, y , s=marker_size, c=self.data[:, 2], zorder=4,
            cmap='bwr',edgecolor='None',norm = scale)

        cbar = map.colorbar(location='right',pad="5%")
        if self.metadata["imt"] == "PGV":
            imt_units = "cm/s"
        else:
            imt_units = "g"
        cbar.set_label("{:s} ({:s})".format(
                       self.metadata["imt"],
                       imt_units))

        if self.box["lat_length"] < 2:
            parallels = np.arange(0.,81,0.25)
        else:
            parallels = np.arange(0.,81,1.0)
        # labels = [left,right,top,bottom]
        map.drawparallels(parallels,labels=[True,False,True,False])
        if self.box["lon_length"] < 2:
            meridians = np.arange(0.,360,0.25)
        else:
            meridians = np.arange(0.,360,1.0)
        map.drawmeridians(meridians,labels=[True,False,False,True])

        title_string = "Hazard Map with a {:s} PoE in {:s} Years\n".format(
             self.metadata["poe"],
             self.metadata["investigation_time"])
        plt.title(title_string, fontsize=16)

        plt.show()
        if output_file:
            plt.savefig(output_file, dpi=dpi, format=fmt, papertype="a4")
