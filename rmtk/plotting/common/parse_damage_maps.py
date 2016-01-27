#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4
# LICENSE
#
# Copyright (c) 2010-2014, GEM Foundation, V. Silva
#
# The Risk Modellers Toolkit is free software: you can redistribute
# it and/or modify it under the terms of the GNU Affero General Public
# License as published by the Free Software Foundation, either version
# 3 of the License, or (at your option) any later version.
#
# You should have received a copy of the GNU Affero General Public License
# along with OpenQuake. If not, see <http://www.gnu.org/licenses/>
#
# DISCLAIMER
#
# The software Risk Modellers Toolkit (rmtk) provided herein
# is released as a prototype implementation on behalf of
# scientists and engineers working within the GEM Foundation (Global
# Earthquake Model).
#
# It is distributed for the purpose of open collaboration and in the
# hope that it will be useful to the scientific, engineering, disaster
# risk and software design communities.
#
# The software is NOT distributed as part of GEMs OpenQuake suite
# (http://www.globalquakemodel.org/openquake) and must be considered as a
# separate entity. The software provided herein is designed and implemented
# by scientific staff. It is not developed to the design standards, nor
# subject to same level of critical review by professional software
# developers, as GEMs OpenQuake software suite.
#
# Feedback and contribution to the software is welcome, and can be
# directed to the risk scientific staff of the GEM Model Facility
# (risk@globalquakemodel.org).
#
# The Risk Modellers Toolkit (rmtk) is therefore distributed WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License
# for more details.
#
# The GEM Foundation, and the authors of the software, assume no
# liability for use of the software.
# -*- coding: utf-8 -*-
'''
Post-process damage calculation data to convert damage maps into different
formats
'''

import argparse
from lxml import etree
import pandas as pd

xmlNRML = '{http://openquake.org/xmlns/nrml/0.5}'
xmlGML = '{http://www.opengis.net/gml}'


def parse_single_damage_node(element, id_node):
    '''
    Reads the damage map node element to return the longitude, latitude and
    asset ref and damages
    '''
    values = []
    for e in element.iter():
        if e.tag == '%spos' % xmlGML:
            coords = str(e.text).split()
            lon = float(coords[0])
            lat = float(coords[1])
        elif e.tag == '%sasset' % xmlNRML:
            ref = e.attrib.get('assetRef')
            mean_list = [id_node, ref, lon, lat]
            for sub in e.getchildren():
                mean_list.append(float(sub.attrib.get('mean')))
            values.append(mean_list)
    return values


def damage_map_parser(input_file):

    id_node = 0
    for _, element in etree.iterparse(input_file):
        if element.tag == '%sdamageStates' % xmlNRML:
            damage_states = element.text.split()
            column_list = ['node', 'asset', 'lon', 'lat']
            [column_list.append(x) for x in damage_states]

        elif element.tag == '%sDDNode' % xmlNRML:
            subValues = parse_single_damage_node(element, id_node)
            df_subValues = pd.DataFrame(subValues, columns=column_list)
            try:
                df_values = df_values.append(df_subValues, ignore_index=True)
            except NameError:
                df_values = df_subValues.copy()
            id_node += 1

    return df_values


def agg_damage_map(df_values):

    uniqueLocations = df_values.groupby('node')['lon', 'lat'].mean()
    aggdamages = df_values.groupby('node').sum()
    aggdamages.update(uniqueLocations)
    return aggdamages


def parse_damage_maps(nrml_damage_map, agg_damages, save_flag):
    '''
    Writes the damage map set to csv
    '''
    df_values = damage_map_parser(nrml_damage_map)

    if save_flag:
        output_file = nrml_damage_map.replace('xml', 'csv')
        df_values.to_csv(output_file, index=False)

    agg_values = None
    if agg_damages:
        agg_values = agg_damage_map(df_values)
        if save_flag:
            agg_output_file = nrml_damage_map.replace('xml', '_agg.csv')
            agg_values.to_csv(agg_output_file, index=False)

    return df_values, agg_values


def set_up_arg_parser():
    """
    Can run as executable. To do so, set up the command line parser
    """
    parser = argparse.ArgumentParser(
        description='Convert NRML damage maps file to comma delimited '
        ' .txt files.'
        'To run just type: python parse_damage_maps.py '
        '--input-file=PATH_TO_damage_MAP_NRML_FILE '
        'include --agg-damages if you wish to aggregate the damages per location '
        'include --save if you wish to save values into csv format', add_help=False)
    flags = parser.add_argument_group('flag arguments')
    flags = parser.add_argument_group('flag arguments')
    flags.add_argument('-h', '--help', action='help')
    flags.add_argument(
        '--input-file',
        help='path to damage map NRML file (Required)',
        default=None,
        required=True)
    flags.add_argument(
        '--agg-damages',
        action="store_true",
        help='aggregates the damages per location',
        required=False)
    flags.add_argument(
        '--save',
        action="store_true",
        help='saves values into csv',
        required=False)

    return parser

if __name__ == "__main__":

    parser = set_up_arg_parser()
    args = parser.parse_args()

    if args.input_file:
        parse_damage_maps(args.input_file, args.agg_damages, args.save)
