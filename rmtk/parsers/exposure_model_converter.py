#!/usr/bin/env python
# LICENSE
#
# Copyright (c) 2014, GEM Foundation, Anirudh Rao
#
# The rmtk is free software: you can redistribute
# it and/or modify it under the terms of the GNU Affero General Public
# License as published by the Free Software Foundation, either version
# 3 of the License, or (at your option) any later version.
#
# You should have received a copy of the GNU Affero General Public License
# along with OpenQuake. If not, see <http://www.gnu.org/licenses/>
#
# DISCLAIMER
#
# The software rmtk provided herein is released as a prototype
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
# directed to the risk scientific staff of the GEM Model Facility
# (risk@globalquakemodel.org).
#
# The nrml_converters is therefore distributed WITHOUT ANY WARRANTY; without
# even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
# PURPOSE. See the GNU General Public License for more details.
#
# The GEM Foundation, and the authors of the software, assume no liability for
# use of the software.
"""
Convert exposure model csv files to xml.
"""

import os
import csv
import math
import argparse
import pandas as pd
from lxml import etree

NAMESPACE = 'http://openquake.org/xmlns/nrml/0.4'
GML_NAMESPACE = 'http://www.opengis.net/gml'
SERIALIZE_NS_MAP = {None: NAMESPACE, 'gml': GML_NAMESPACE}

def csv_to_xml(input_csv, metadata_csv, output_xml):
    """
    Converts the CSV exposure model file to the NRML format
    """
    metadata = {}
    data = pd.io.parsers.read_csv(input_csv)
    with open(metadata_csv, 'rU') as f:
        reader = csv.reader(f)
        for row in reader:
            metadata[row[0]] = row[1]

    with open(output_xml, "w") as f:
        root = etree.Element('nrml', nsmap=SERIALIZE_NS_MAP)
        node_em = etree.SubElement(root, "exposureModel")
        node_em.set("id", metadata['id'])
        node_em.set("category", metadata['category'])
        node_em.set("taxonomySource", metadata['taxonomy_source'])

        node_desc = etree.SubElement(node_em, "description")
        node_desc.text = metadata['description']

        node_conv = etree.SubElement(node_em, "conversions")
        node_cost_types = etree.SubElement(node_conv, "costTypes")

        node_cost_type_s = etree.SubElement(node_cost_types, "costType")
        node_cost_type_s.set("name", "structural")
        node_cost_type_s.set("type", metadata['structural_cost_aggregation_type'])
        node_cost_type_s.set("unit", metadata['structural_cost_currency'])

        if metadata['nonstructural_cost_aggregation_type']:
            node_cost_type_ns = etree.SubElement(node_cost_types, "costType")
            node_cost_type_ns.set("name", "nonstructural")
            node_cost_type_ns.set("type", metadata['nonstructural_cost_aggregation_type'])
            node_cost_type_ns.set("unit", metadata['nonstructural_cost_currency'])
        if metadata['contents_cost_aggregation_type']:
            node_cost_type_c = etree.SubElement(node_cost_types, "costType")
            node_cost_type_c.set("name", "contents")
            node_cost_type_c.set("type", metadata['contents_cost_aggregation_type'])
            node_cost_type_c.set("unit", metadata['contents_cost_currency'])

        if metadata['insurance_deductible_is_absolute']:
            node_deductible = etree.SubElement(node_conv, "deductible")
            node_deductible.set("isAbsolute", metadata['insurance_deductible_is_absolute'].lower())
        if metadata['insurance_limit_is_absolute']:
            node_limit= etree.SubElement(node_conv, "insuranceLimit")
            node_limit.set("isAbsolute", metadata['insurance_limit_is_absolute'].lower())

        node_assets = etree.SubElement(node_em, "assets")
        for row_index, row in data.iterrows():
            node_asset = etree.SubElement(node_assets, "asset")
            node_asset.set("id", str(row['asset_id']))
            node_asset.set("number", str(row['num_buildings']))
            node_asset.set("area", str(row['built_up_area']))
            node_asset.set("taxonomy", str(row['taxonomy']))

            node_location = etree.SubElement(node_asset, "location")
            node_location.set("lon", str(row['longitude']))
            node_location.set("lat", str(row['latitude']))

            node_costs = etree.SubElement(node_asset, "costs")

            if not math.isnan(row['structural_replacement_cost']):
                node_cost_s = etree.SubElement(node_costs, "cost")
                node_cost_s.set("type", 'structural')
                node_cost_s.set("value", str(row['structural_replacement_cost']))
            if not math.isnan(row['structural_insurance_deductible']):
                node_cost_s.set("deductible", str(row['structural_insurance_deductible']))
            if not math.isnan(row['structural_insurance_limit']):
                node_cost_s.set("insuranceLimit", str(row['structural_insurance_limit']))
            if not math.isnan(row['structural_retrofit_cost']):
                node_cost_s.set("retrofitted", str(row['structural_retrofit_cost']))

            if not math.isnan(row['nonstructural_replacement_cost']):
                node_cost_ns = etree.SubElement(node_costs, "cost")
                node_cost_ns.set("type", 'nonstructural')
                node_cost_ns.set("value", str(row['nonstructural_replacement_cost']))
            if not math.isnan(row['nonstructural_insurance_deductible']):
                node_cost_ns.set("deductible", str(row['nonstructural_insurance_deductible']))
            if not math.isnan(row['nonstructural_insurance_limit']):
                node_cost_ns.set("insuranceLimit", str(row['nonstructural_insurance_limit']))
            if not math.isnan(row['nonstructural_retrofit_cost']):
                node_cost_ns.set("retrofitted", str(row['nonstructural_retrofit_cost']))

            if not math.isnan(row['contents_replacement_cost']):
                node_cost_c = etree.SubElement(node_costs, "cost")
                node_cost_c.set("type", 'contents')
                node_cost_c.set("value", str(row['contents_replacement_cost']))
            if not math.isnan(row['contents_insurance_deductible']):
                node_cost_c.set("deductible", str(row['contents_insurance_deductible']))
            if not math.isnan(row['contents_insurance_limit']):
                node_cost_c.set("insuranceLimit", str(row['contents_insurance_limit']))
            if not math.isnan(row['contents_retrofit_cost']):
                node_cost_c.set("retrofitted", str(row['contents_retrofit_cost']))

            if not math.isnan(row['downtime_cost']):
                node_cost_d = etree.SubElement(node_costs, "cost")
                node_cost_d.set("type", 'downtime')
                node_cost_d.set("value", str(row['downtime_cost']))
            if not math.isnan(row['downtime_insurance_deductible']):
                node_cost_d.set("deductible", str(row['downtime_insurance_deductible']))
            if not math.isnan(row['downtime_insurance_limit']):
                node_cost_d.set("insuranceLimit", str(row['downtime_insurance_limit']))

            if not math.isnan(row['day_occupants']) or math.isnan(row['night_occupants']) or math.isnan(row['transit_occupants']):
                node_occupancies = etree.SubElement(node_asset, "occupancies")

                if not math.isnan(row['day_occupants']):
                    node_occ_day = etree.SubElement(node_occupancies, "occupancy")
                    node_occ_day.set("period", 'day')
                    node_occ_day.set("occupants", str(row['day_occupants']))

                if not math.isnan(row['night_occupants']):
                    node_occ_night = etree.SubElement(node_occupancies, "occupancy")
                    node_occ_night.set("period", 'night')
                    node_occ_night.set("occupants", str(row['night_occupants']))

                if not math.isnan(row['transit_occupants']):
                    node_occ_transit = etree.SubElement(node_occupancies, "occupancy")
                    node_occ_transit.set("period", 'transit')
                    node_occ_transit.set("occupants", str(row['transit_occupants']))

        f.write(etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='UTF-8'))


def xml_to_csv (input_xml, output_csv):
    """
    Converts the XML fragility model file to the CSV format
    """
    print('This feature will be implemented in a future release.')


def set_up_arg_parser():
    """
    Can run as executable. To do so, set up the command line parser
    """

    description = ('Convert an Exposure Model from CSV to XML and '
                   'vice versa.\n\nTo convert from CSV to XML: '
                   '\npython exposure_model_converter.py '
                   '--input-csv-file PATH_TO_EXPOSURE_MODEL_CSV_FILE '
                   '--metadata-csv-file PATH_TO_EXPOSURE_METADATA_CSV_FILE '
                   '--output-xml-file PATH_TO_OUTPUT_XML_FILE'
                   '\n\nTo convert from XML to CSV type: '
                   '\npython exposure_model_converter.py '
                   '--input-xml-file PATH_TO_EXPOSURE_MODEL_XML_FILE '
                   '--output-csv-file PATH_TO_OUTPUT_CSV_FILE')

    parser = argparse.ArgumentParser(description=description, formatter_class=argparse.RawTextHelpFormatter)
    flags = parser.add_argument_group('flag arguments')

    group_input = flags.add_argument_group('input files')
    group_input_choice = group_input.add_mutually_exclusive_group(required=True)
    group_input_choice.add_argument('--input-xml-file',
                       help='path to exposure model XML file',
                       default=None)
    group_input_choice.add_argument('--input-csv-file',
                       help='path to exposure model CSV file',
                       default=None)
    group_input.add_argument('--metadata-csv-file',
                       help='path to exposure metadata CSV file',
                       default=None,
                       required=True)

    group_output = flags.add_argument_group('output files')
    group_output.add_argument('--output-xml-file',
                              help='path to output XML file',
                              default=None,
                              required=False)
    return parser


if __name__ == "__main__":

    parser = set_up_arg_parser()
    args = parser.parse_args()
    if args.input_csv_file:
        if args.output_xml_file:
            output_file = args.output_xml_file
        else:
            (filename, ext) = os.path.splitext(args.input_csv_file)
            output_file = filename + '.xml'
        csv_to_xml(args.input_csv_file, args.metadata_csv_file, output_file)
    elif args.input_xml_file:
        if args.output_csv_file:
            output_file = args.output_csv_file
        else:
            (filename, ext) = os.path.splitext(args.input_xml_file)
            output_file = filename + '.csv'
        xml_to_csv(args.input_xml_file, output_file)
    else:
        parser.print_usage()