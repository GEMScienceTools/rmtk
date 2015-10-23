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
Parse a number of event loss tables and stored all the losses
in a single csv file 
'''

import os
import argparse
import numpy as np

def parse_single_elt(singleELT):

	elt = []

	file = open(singleELT)
	lines = file.readlines()
	for line in lines: 
		elt.append(line.strip().strip().split(','))
	
	del elt[0]
	return elt

def parse_elt(folder_ses,save_flag):
	'''
	Writes the evebt loss tables to csv
	'''
	elt = []

	elt_files = [x for x in os.listdir(folder_ses) if x[-4:] == '.csv']

	for singleFile in elt_files:
		subELT = parse_single_elt(folder_ses+'/'+singleFile)
		for ele in subELT:
			elt.append(ele)

	if save_flag:
		output_file = open(folder_ses+'ELT'+'.csv','w')        
		for subELT in elt:
			line = ''
			for ele in subELT:
				line = line+ele+','
			output_file.write(line[0:-1]+'\n')
		output_file.close()

	return np.array(elt)

def set_up_arg_parser():
    """
    Can run as executable. To do so, set up the command line parser
    """
    parser = argparse.ArgumentParser(
        description='Convert NRML ses file to a comma separated value file'
            'Inside the specified output directory put all of the'
            'files for each stochastic event set.'
            'To run just type: python parse_ses.py '
            '--input-folder=PATH_TO_FOLDER_WITH_SES '
			'include --save if you wish to save ses into csv format' , add_help=False)
    flags = parser.add_argument_group('flag arguments')
    flags = parser.add_argument_group('flag arguments')
    flags.add_argument('-h', '--help', action='help')
    flags.add_argument('--input-folder',
        help='path to loss map NRML file (Required)',
        default=None,
        required=True)
    flags.add_argument('--save', action="store_true",
        help='saves values into csv',
        required=False)

    return parser

if __name__ == "__main__":

    parser = set_up_arg_parser()
    args = parser.parse_args()

    if args.input_folder:
        parse_elt(args.input_folder,args.save)
