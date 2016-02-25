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
import ConfigParser
import argparse
import pandas as pd
from lxml import etree

NAMESPACE = 'http://openquake.org/xmlns/nrml/0.4'
GML_NAMESPACE = 'http://www.opengis.net/gml'
SERIALIZE_NS_MAP = {None: NAMESPACE, 'gml': GML_NAMESPACE}


def split_strip(value):
    return [x.strip() for x in value.split(',')]


def csv_to_xml(metadata_txt, output_xml):
    """
    Converts the CSV exposure model file to the NRML format
    """

    conf = ConfigParser.ConfigParser()
    conf.read(metadata_txt)
    metadata = conf._sections
    metadata['main']['csv_file'] = os.path.abspath(
        os.path.join(os.path.abspath(metadata_txt),
                     os.pardir,
                     metadata['main']['csv_file']))

    key_less = metadata.keys()
    key_less.remove('main')

    for key in key_less:
        for item, value in metadata[key].iteritems():
            if ',' in value:
                metadata[key][item] = split_strip(value)

    # for key, value in metadata['cost'].iteritems():
    #     metadata['cost'][key] = value.split(', ')
    # metadata['occupants']['period'] = split_strip(metadata['occupants']['period'])
    # metadata['mapping']['cost'] = split_strip(metadata['mapping']['cost'])
    # metadata['mapping']['occupants'] = split_strip(metadata['mapping']['occupants'])
    # metadata['mapping']['deductible'] = split_strip(metadata['mapping']['deductible'])
    # metadata['mapping']['insurance_limit'] = split_strip(metadata['mapping']['insurance_limit'])
    # metadata['mapping']['insurance_limit'] = split_strip(metadata['mapping']['insurance_limit'])

    data = pd.read_csv(metadata['main']['csv_file'])

    with open(output_xml, "w") as f:
        root = etree.Element('nrml', nsmap=SERIALIZE_NS_MAP)
        node_em = etree.SubElement(root, "exposureModel")
        node_em.set("id", metadata['main']['id'])
        node_em.set("category", metadata['main']['category'])
        node_em.set("taxonomySource", metadata['main']['taxonomy_source'])

        node_desc = etree.SubElement(node_em, "description")
        node_desc.text = metadata['main']['description']

        node_conv = etree.SubElement(node_em, "conversions")

        if 'per_area' in metadata['cost']['cost_type']:
            node_area = etree.SubElement(node_conv, "area")
            node_area.set("type", metadata['area']['area_type'])
            node_area.set("unit", metadata['area']['area_unit'])

        node_cost_types = etree.SubElement(node_conv, "costTypes")
        for name_, type_, unit_ in zip(metadata['cost']['cost_name'],
                                       metadata['cost']['cost_type'],
                                       metadata['cost']['cost_unit']):
            node_cost_type_s = etree.SubElement(node_cost_types, "costType")
            node_cost_type_s.set("name", name_)
            node_cost_type_s.set("type", type_)
            node_cost_type_s.set("unit", unit_)

        if metadata['insurance']['deductible_absolute'] in ['true', 'false']:
            node_deductible = etree.SubElement(node_conv, "deductible")
            node_deductible.set("isAbsolute", metadata['insurance']['deductible_absolute'])

        if metadata['insurance']['limit_absolute'] in ['true', 'false']:
            node_limit = etree.SubElement(node_conv, "insuranceLimit")
            node_limit.set("isAbsolute", metadata['insurance']['limit_absolute'])

        node_assets = etree.SubElement(node_em, "assets")

        for _, row in data.iterrows():

            node_asset = etree.SubElement(node_assets, "asset")

            node_location = etree.SubElement(node_asset, "location")
            node_location.set("lon", str(row[metadata['mapping']['lon']]))
            node_location.set("lat", str(row[metadata['mapping']['lat']]))

            node_asset.set("id", str(row[metadata['mapping']['id']]))
            node_asset.set("number", str(row[metadata['mapping']['number']]))
            node_asset.set("taxonomy", str(row[metadata['mapping']['taxonomy']]))

            if 'per_area' in metadata['cost']['cost_type']:
                node_asset.set("area", str(row[metadata['mapping']['area']]))

            node_costs = etree.SubElement(node_asset, "costs")
            for name_, value_, limit_, deduct_, retro_ in \
                zip(metadata['cost']['cost_name'],
                    metadata['mapping']['cost'],
                    metadata['mapping']['insurance_limit'],
                    metadata['mapping']['deductible'],
                    metadata['mapping']['retrofit']):

                node_cost_s = etree.SubElement(node_costs, "cost")
                node_cost_s.set("type", name_)
                node_cost_s.set("value", str(row[value_]))

                if limit_ != 'None':
                    node_cost_s.set("insuranceLimit", str(row[limit_]))

                if deduct_ != 'None':
                    node_cost_s.set("deductible", str(row[deduct_]))

                if retro_ != 'None':
                    node_cost_s.set("retrofit", str(row[retro_]))

            node_occupancies = etree.SubElement(node_asset, "occupancies")

            for name_, mapping_ in zip(metadata['occupants']['period'],
                                       metadata['mapping']['occupants']):
                node_occ = etree.SubElement(node_occupancies, "occupancy")
                node_occ.set("occupants", str(row[mapping_]))
                node_occ.set("period", name_)

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
                   '--metadata_txt-file PATH_TO_EXPOSURE_METADATA_TXT_FILE '
                   '--output-xml-file PATH_TO_OUTPUT_XML_FILE'
                   '\n\nTo convert from XML to CSV type: '
                   '\npython exposure_model_converter.py '
                   '--input-xml-file PATH_TO_EXPOSURE_MODEL_XML_FILE '
                   '--output-csv-file PATH_TO_OUTPUT_CSV_FILE')

    parser = argparse.ArgumentParser(description=description, formatter_class=argparse.RawTextHelpFormatter)
    flags = parser.add_argument_group('flag arguments')

    group_input = flags.add_mutually_exclusive_group(required=True)

    group_input.add_argument('--metadata-txt-file',
                             help='path to exposure metadata TXT file',
                             default=None)
    group_input.add_argument('--input-csv-file',
                             help='path to exposure model CSV file',
                             default=None)

    group_output = flags.add_mutually_exclusive_group()
    group_output.add_argument('--output-xml-file',
                              help='path to output XML file',
                              default=None)
    group_output.add_argument('--output-csv-file',
                              help='path to output CSV file',
                              default=None,
                              required=False)

    return parser

if __name__ == "__main__":

    parser = set_up_arg_parser()
    args = parser.parse_args()
    if args.metadata_txt_file:
        csv_to_xml(args.metadata_txt_file, args.output_xml_file)
    elif args.input_xml_file:
        if args.output_csv_file:
            output_file = args.output_csv_file
        else:
            (filename, ext) = os.path.splitext(args.input_xml_file)
            output_file = filename + '.csv'
        xml_to_csv(args.input_xml_file, output_file)
    else:
        parser.print_usage()
