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
Convert fragility model csv files to xml.
"""

import os
import csv
import argparse
import pandas as pd
from lxml import etree

NAMESPACE = 'http://openquake.org/xmlns/nrml/0.4'
GML_NAMESPACE = 'http://www.opengis.net/gml'
SERIALIZE_NS_MAP = {None: NAMESPACE, 'gml': GML_NAMESPACE}

def csv_to_xml(input_csv, metadata_csv, output_xml):
    """
    Converts the CSV fragility model file to the NRML format
    """
    metadata = {}
    with open(metadata_csv, 'rU') as f:
        reader = csv.reader(f)
        for row in reader:
            metadata[row[0]] = row[1]
    metadata['limitStates'] = metadata['limitStates'].split('; ')

    data = pd.io.parsers.read_csv(input_csv)
    grouped_by_tax = data.groupby('taxonomy')
    frag_model = {}

    for taxonomy, group in grouped_by_tax:
        frag_model[taxonomy] = {}
        frag_model[taxonomy]['noDamageLimit'] = str(group['noDamageLimit'].tolist()[0])
        frag_model[taxonomy]['iml_unit'] = group['iml_unit'].tolist()[0]
        frag_model[taxonomy]['imt'] = group['imt'].tolist()[0]
        frag_model[taxonomy]['iml'] = group['iml'].tolist()

        frag_func = {}
        for ls in metadata['limitStates']:
            frag_func[ls] = group[ls].tolist()

        frag_model[taxonomy]['function'] = frag_func

        with open(output_xml, "w") as f:
            root = etree.Element('nrml', nsmap=SERIALIZE_NS_MAP)
            node_fm = etree.SubElement(root, "fragilityModel")
            node_desc = etree.SubElement(node_fm, "description")
            node_desc.text = metadata['description']
            node_ls = etree.SubElement(node_fm, "limitStates")
            node_ls.text = " ".join(map(str, metadata['limitStates']))

            for taxonomy, frag_func_set in frag_model.iteritems():
                node_ffs = etree.SubElement(node_fm, "ffs")
                node_ffs.set("noDamageLimit", frag_func_set['noDamageLimit'])
                node_tax = etree.SubElement(node_ffs, "taxonomy")
                node_tax.text = taxonomy
                node_iml = etree.SubElement(node_ffs, "IML")
                node_iml.set("IMT", frag_func_set['imt'])
                node_iml.set("iml_unit", frag_func_set['iml_unit'])
                node_iml.text = " ".join(map(str, frag_func_set['iml']))

                frag_func = frag_func_set['function']
                for ls in metadata['limitStates']:
                    node_ffd = etree.SubElement(node_ffs, "ffd")
                    node_ffd.set("ls", ls)
                    node_poes = etree.SubElement(node_ffd, "poEs")
                    node_poes.text = " ".join(map(str, frag_func[ls]))

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

    description = ('Convert a Fragility Model from CSV to XML and '
                   'vice versa.\n\nTo convert from CSV to XML: '
                   '\npython fragility_model_converter.py '
                   '--input-csv-file PATH_TO_FRAGILITY_MODEL_CSV_FILE '
                   '--metadata-csv-file PATH_TO_FRAGILITY_METADATA_CSV_FILE '
                   '--output-xml-file PATH_TO_OUTPUT_XML_FILE'
                   '\n\nTo convert from XML to CSV type: '
                   '\npython fragility_model_converter.py '
                   '--input-xml-file PATH_TO_FRAGILITY_MODEL_XML_FILE '
                   '--output-csv-file PATH_TO_OUTPUT_CSV_FILE')

    parser = argparse.ArgumentParser(description=description, formatter_class=argparse.RawTextHelpFormatter)
    flags = parser.add_argument_group('flag arguments')

    group_input = flags.add_argument_group('input files')
    group_input_choice = group_input.add_mutually_exclusive_group(required=True)
    group_input_choice.add_argument('--input-xml-file',
                       help='path to fragility model XML file',
                       default=None)
    group_input_choice.add_argument('--input-csv-file',
                       help='path to fragility model CSV file',
                       default=None)
    group_input.add_argument('--metadata-csv-file',
                       help='path to fragility metadata CSV file',
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