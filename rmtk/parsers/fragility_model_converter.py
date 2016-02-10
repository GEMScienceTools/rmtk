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
import ConfigParser
import argparse
import pandas as pd
from lxml import etree
import numpy as np
from scipy.stats import lognorm
import matplotlib.pyplot as plt

NAMESPACE = 'http://openquake.org/xmlns/nrml/0.5'
GML_NAMESPACE = 'http://www.opengis.net/gml'
SERIALIZE_NS_MAP = {None: NAMESPACE, 'gml': GML_NAMESPACE}


def csv_to_xml(metadata_txt, output_xml):
    """
    Converts the CSV fragility model file to the NRML format
    """

    conf = ConfigParser.ConfigParser()
    conf.read(metadata_txt)
    metadata = conf._sections
    metadata['main']['limit_states'] = metadata['main']['limit_states'].split(', ')

    frag_function = dict()

    if metadata['main']['file_discrete']:
        metadata['main']['file_discrete'] = os.path.abspath(
            os.path.join(os.path.abspath(metadata_txt),
                         os.pardir,
                         metadata['main']['file_discrete']))
        try:
            data_discrete = pd.read_csv(metadata['main']['file_discrete'])
        except IOError:
            print '{} does not exist'.format(metadata['main']['file_discrete'])

        for taxonomy, group in data_discrete.groupby('taxonomy'):
            if taxonomy in metadata:
                frag_function[taxonomy] = group.to_dict('list')

    if metadata['main']['file_continuous']:
        metadata['main']['file_continuous'] = os.path.abspath(
            os.path.join(os.path.abspath(metadata_txt),
                         os.pardir,
                         metadata['main']['file_continuous']))
        try:
            data_continuous = pd.read_csv(metadata['main']['file_continuous'])
        except IOError:
            print '{} does not exist'.format(metadata['main']['file_continuous'])

        for taxonomy, group in data_continuous.groupby('taxonomy'):
            if taxonomy in metadata:
                for line in group.iterrows():
                    frag_function.setdefault(taxonomy, {})[line[1]['damagestate']] = (
                        line[1]['mean'], line[1]['stddev'])

    with open(output_xml, "w") as f:
        root = etree.Element('nrml', nsmap=SERIALIZE_NS_MAP)
        node_fm = etree.SubElement(root, "fragilityModel")
        node_fm.set("id", metadata['main']['id'])
        node_fm.set("assetCategory", metadata['main']['asset_category'])
        node_fm.set("lossCategory", metadata['main']['loss_category'])

        node_desc = etree.SubElement(node_fm, "description")
        node_desc.text = metadata['main']['description']
        node_ls = etree.SubElement(node_fm, "limitStates")
        node_ls.text = " ".join(map(str, metadata['main']['limit_states']))

        for taxonomy, value in frag_function.iteritems():

            node_ffs = etree.SubElement(node_fm, "fragilityFunction")
            node_ffs.set("id", taxonomy)
            node_ffs.set("format", metadata[taxonomy]['format'])

            if metadata[taxonomy]['format'] == 'continuous':
                node_ffs.set("shape", metadata[taxonomy]['shape'])
                node_imls = etree.SubElement(node_ffs, "imls")
                node_imls.set("imt", metadata[taxonomy]['imt'])
                node_imls.set("noDamageLimit", metadata[taxonomy]['nodamage_limit'])
                node_imls.set("minIML", metadata[taxonomy]['miniml'])
                node_imls.set("maxIML", metadata[taxonomy]['maximl'])

                for limit_state in metadata['main']['limit_states']:
                    node_params = etree.SubElement(node_ffs, "params")
                    node_params.set("ls", limit_state)
                    node_params.set("mean", str(value[limit_state][0]))
                    node_params.set("stddev", str(value[limit_state][1]))

            elif metadata[taxonomy]['format'] == 'discrete':

                node_imls = etree.SubElement(node_ffs, "imls")
                node_imls.set("imt", metadata[taxonomy]['imt'])
                node_imls.set("noDamageLimit", metadata[taxonomy]['nodamage_limit'])
                node_imls.text = " ".join(map(str, value['iml']))

                for limit_state in metadata['main']['limit_states']:
                    node_poes = etree.SubElement(node_ffs, "poes")
                    node_poes.set("ls", limit_state)
                    node_poes.text = " ".join(map(str, value[limit_state]))

        f.write(etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='UTF-8'))


def xml_to_csv (input_xml, output_csv):
    """
    Converts the XML fragility model file to the CSV format
    """
    print('This feature will be implemented in a future release.')


class FragilityModel(object):
    '''
    class for a fragility model which is a collection of fragility functions
    '''

    def parse_xml(self, input_file=None):

        if not os.path.exists(input_file):
            print('file {} not found'.format(input_file))
            sys.exit(1)

        self.input_file = input_file

        for _, element in etree.iterparse(input_file):

            if 'fragilityModel' in element.tag:

                self.metadata = dict()
                self.metadata['asset_category'] = element.attrib['assetCategory']
                self.metadata['id'] = element.attrib['id']
                self.metadata['loss_category'] = element.attrib['lossCategory']

                self.frag = dict()
                for item in element.getchildren():

                    if 'description' in item.tag:
                        self.metadata['description'] = item.text.strip()
                    elif 'limitStates' in item.tag:
                        self.metadata['limit_states'] = item.text.split()
                    elif 'fragilityFunction' in item.tag:
                        taxonomy = item.attrib['id']
                        self.frag[taxonomy] = FragilityFunction(item, self.metadata)

    def plot_fragility(self, im_range):
        for bldg, bldg_frag in self.frag.iteritems():
            bldg_frag.plot_fragility(im_range)

class FragilityFunction(object):

    def __init__(self, element, metadata):

        self.metadata = metadata
        self.taxonomy = element.attrib['id']
        self.frag_format = element.attrib['format']
        children = element.getchildren()

        if self.frag_format == 'continuous':
            self.shape = element.attrib['shape']
            self.continuousfragilityModelParser(children)
        else:
            self.discretefragilityModelParser(children)

    def plot_fragility(self, im_range):

        self.est_poes = self.compute_poes(im_range)

        plt.figure()
        for state in self.metadata['limit_states']:
            plt.plot(im_range, self.est_poes[state], label=state)
        plt.legend()
        plt.grid(1)
        plt.xlabel(self.imt)
        plt.ylabel('Prob. of exceedance')
        plt.title(self.taxonomy)

    def compute_poes(self, im_range):

        if self.frag_format == 'continuous':
            est_poes = dict()
            for state, (mean_, std_) in self.params.iteritems():
                values = lognorm.cdf(im_range, std_, scale=mean_)
                values[im_range <= self.noDamageLimit] = 0.0
                est_poes[state] = values
        else:
            est_poes = dict()
            for state, poe_values in self.poes.iteritems():
                values = np.interp(im_range, self.iml, poe_values,
                                   left=0.0, right=1.0)
                values[im_range <= self.noDamageLimit] = 0.0
                est_poes[state] = values

        return est_poes

    def continuousfragilityModelParser(self, children):

        self.params = dict()
        for item in children:

            if 'imls' in item.tag:
                self.imt = item.attrib['imt']
                self.noDamageLimit = float(item.attrib['noDamageLimit'])
                self.iml = (float(item.attrib['minIML']),
                            float(item.attrib['maxIML']))
            elif 'params' in item.tag:
                limit_state = item.attrib['ls']
                self.params[limit_state] = (float(item.attrib['mean']),
                                            float(item.attrib['stddev']))

    def discretefragilityModelParser(self, children):

        self.poes = dict()
        for item in children:

            if 'imls' in item.tag:
                self.imt = item.attrib['imt']
                self.noDamageLimit = float(item.attrib['noDamageLimit'])
                self.iml = [float(x) for x in item.text.split()]

            elif 'poes' in item.tag:
                limit_state = item.attrib['ls']
                self.poes[limit_state] = [float(x) for x in item.text.split()]


def set_up_arg_parser():
    """
    Can run as executable. To do so, set up the command line parser
    """

    description = ('Convert a Fragility Model from CSV to XML and '
                   'vice versa.\n\nTo convert from CSV to XML: '
                   '\npython fragility_model_converter.py '
                   '--metadata-txt-file PATH_TO_FRAGILITY_METADATA_TXT_FILE '
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
    group_input_choice.add_argument('--metadata-txt-file',
                                    help='path to fragility metadata TXT file',
                                    default=None)

    group_output = flags.add_argument_group('output files')
    group_output.add_argument('--output-xml-file',
                              help='path to output XML file',
                              default=None,
                              required=True)
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
