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
Parse a number of SES stored in NRML and store them in CSV
'''

import os
import argparse
import numpy as np
from lxml import etree

xmlNRML = '{http://openquake.org/xmlns/nrml/0.5}'
xmlGML = '{http://www.opengis.net/gml}'


def parsePlanarSurface(element):
    '''
    Parses the planar surface of a rupture
    '''
    topLeft = 0
    topRight = 0
    bottomLeft = 0
    bottomRight = 0

    for e in element.iter():
        if e.tag == '%stopLeft' % xmlNRML:
            topLeft = [e.attrib.get('lon'), e.attrib.get('lat'), e.attrib.get('depth')]
        elif e.tag == '%stopRight' % xmlNRML:
            topRight = [e.attrib.get('lon'), e.attrib.get('lat'), e.attrib.get('depth')]
        elif e.tag == '%sbottomLeft' % xmlNRML:
            bottomLeft = [e.attrib.get('lon'), e.attrib.get('lat'), e.attrib.get('depth')]
        elif e.tag == '%sbottomRight' % xmlNRML:
            bottomRight = [e.attrib.get('lon'), e.attrib.get('lat'), e.attrib.get('depth')]

    return topLeft, topRight, bottomLeft, bottomRight


def parseMeshRupture(element):
    '''
    Parses the mesh rupture
    '''

    lon = []
    lat = []
    depth = []

    for e in element.iter():

        if e.tag == '%snode' % xmlNRML:
            lon.append(float(e.attrib.get('lon')))
            lat.append(float(e.attrib.get('lat')))
            depth.append(float(e.attrib.get('depth')))

    left = np.argmin(lon)
    right = np.argmax(lon)

    topLeft = [lon[left],lat[left],np.max(depth)]
    topRight = [lon[right],lat[right],np.max(depth)]
    bottomLeft = [lon[left],lat[left],np.min(depth)]
    bottomRight = [lon[right],lat[right],np.min(depth)]
    return topLeft, topRight, bottomLeft, bottomRight


def parse_ses_single_file(singleFile):

    ses = []
    investigationTime = 0.0

    for _, element in etree.iterparse(singleFile):
#        print element.tag

        if element.tag == '%sstochasticEventSetCollection' % xmlNRML:
            SESColletion = element
            for subElement in SESColletion.iter():
                if subElement.tag == '%sstochasticEventSet' % xmlNRML:
                    SESSet = subElement
                    investigationTime += float(SESSet.attrib.get('investigationTime'))
                    for subSubElement in SESSet.iter():
                        if subSubElement.tag == '%srupture' % xmlNRML:
                            rupture = subSubElement
                            rupId = rupture.attrib.get('id')
                            mag = rupture.attrib.get('magnitude')
                            strike = rupture.attrib.get('strike')
                            dip = rupture.attrib.get('dip')
                            rake = rupture.attrib.get('rake')
                            tectonicRegion = rupture.attrib.get('tectonicRegion')
                            for geometry in rupture:
                                if geometry.tag == '%splanarSurface' % xmlNRML:
                                    planarSurface = geometry
                                    topLeft, topRight, bottomLeft, bottomRight = parsePlanarSurface(planarSurface)
                                if geometry.tag == '%smesh' % xmlNRML:
                                    mesh = geometry
                                    topLeft, topRight, bottomLeft, bottomRight = parseMeshRupture(mesh)

                            ses.append([rupId,
                                        mag,
                                        strike,
                                        dip,
                                        rake,
                                        tectonicRegion,
                                        topLeft[0],
                                        topLeft[1],
                                        topLeft[2],
                                        topRight[0],
                                        topRight[1],
                                        topRight[2],
                                        bottomLeft[0],
                                        bottomLeft[1],
                                        bottomLeft[2],
                                        bottomRight[0],
                                        bottomRight[1],
                                        bottomRight[2]])

    return investigationTime, ses


def parse_ses(folder_ses, save_flag):
    '''
    Writes the ses to csv
    '''
    ses = []
    investigationTime = 0.0

    ses_files = [x for x in os.listdir(folder_ses) if x[-4:] == '.xml' and 'ses' in x]

    for singleFile in ses_files:
        time, subSetSES = parse_ses_single_file(folder_ses+'/'+singleFile)
        for setSES in subSetSES:
            ses.append(setSES)
        investigationTime += float(time)

    if save_flag:
        output_file = open(folder_ses+'_SES'+'.csv', 'w')
        for subSES in ses:
            line = ''
            for ele in subSES:
                line = line+str(ele)+','
            output_file.write(line[0:-1]+'\n')
        output_file.close()

    return investigationTime, np.array(ses)

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
        parse_ses(args.input_folder,args.save)
