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
Post-process risk calculation data to convert loss maps into different
formats
'''

import os
import csv
import argparse
import numpy as np
from lxml import etree

xmlNRML='{http://openquake.org/xmlns/nrml/0.4}'
xmlGML = '{http://www.opengis.net/gml}'

def fragilityModelParser(input_file):

    taxonomies = []

    for _, element in etree.iterparse(input_file):
        if element.tag == '%staxonomy' % xmlNRML:
			taxonomies.append(element.text)
        else:
            continue
    
    return taxonomies
    
def extractTaxonomies(nrml_fragility_model,save_flag):
	'''
	Extracts the taxonomies fro ma fragility model and save
	to a text file if save_flag
	'''
	taxonomies = fragilityModelParser(nrml_fragility_model)      
  
	if save_flag:
		output_file = open(nrml_fragility_model.replace('xml','.txt'),'w')
		for taxonomy in taxonomies:
			output_file.write(taxonomy+'\n')
		output_file.close()

	return taxonomies


def set_up_arg_parser():
    """
    Can run as executable. To do so, set up the command line parser
    """
    parser = argparse.ArgumentParser(
        description='Extract list of taxonomies from NRML fragility models file'
            ' .txt files. Inside the specified output directory, create a .txt '
            'file for each stochastic event set.'
            'To run just type: python parse_fragility.py '
            '--input-file=PATH_TO_FRAGILITY_MODEL_NRML_FILE ', add_help=False)
    flags = parser.add_argument_group('flag arguments')
    flags.add_argument('-h', '--help', action='help')
    flags.add_argument('--input-file',
        help='path to fragility model NRML file (Required)',
        default=None,
        required=True)
    flags.add_argument('--save', action="store_true",
        help='Save taxonomies to a text file',
        default=None,
        required=False)

    return parser


if __name__ == "__main__":

    parser = set_up_arg_parser()
    args = parser.parse_args()

    if args.input_file:
        extractTaxonomies(args.input_file,args.save)
