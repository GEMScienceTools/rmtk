'''
Post-process damage calculation data to extract the damage distribution
for different taxonomies
'''

import os
import csv
import argparse
import numpy as np
from lxml import etree
from collections import OrderedDict

xmlNRML='{http://openquake.org/xmlns/nrml/0.4}'
xmlGML = '{http://www.opengis.net/gml}'

def parse_single_damage_dist(element):
    '''
    Reads the dmgDist element to return the longitude, latitude and 
    poes and losses
    '''
    taxonomy = ''
    damage_dist = {}
    for e in element.iter():
        if e.tag == '%staxonomy' % xmlNRML:
            taxonomy = str(e.text)
        elif e.tag == '%sdamage' % xmlNRML:
            ds = e.attrib.get('ds')
            mean = float(e.attrib.get('mean'))
            stddev = float(e.attrib.get('stddev'))
            damage_dist[ds] = (mean, stddev)
        else:
            continue
    return taxonomy, damage_dist

def parse_dmg_dist_total(element):
    '''
    Returns the list of damage states and statistics for each damage state
    '''
    damage_states = []
    damage_dist = {}
    for e in element.iter():
        if e.tag == '%sdamageStates' % xmlNRML:
            damage_states = str(e.text).split()
        elif e.tag == '%sdamage' % xmlNRML:
            ds = e.attrib.get('ds')
            mean = float(e.attrib.get('mean'))
            stddev = float(e.attrib.get('stddev'))
            damage_dist[ds] = (mean, stddev)
        else:
            continue
    return damage_states, damage_dist

def parse_dmg_dist_tax(element):
    taxonomies = []
    damage_states = []
    damage_dist_tax = {}
    for e in element.iter():
        if e.tag == '%sdamageStates' % xmlNRML:
            damage_states = str(e.text).split()
        elif e.tag == '%sDDNode' % xmlNRML:
            taxonomy, damage_dist = parse_single_damage_dist(e)
            taxonomies.append(taxonomy)
            damage_dist_tax[taxonomy] = damage_dist
        else:
            continue
    return taxonomies, damage_states, damage_dist_tax

def parse_damage_file(input_file):
    '''
    Reads an xml damage dist file and returns a dictionary with
    taxonomies as keys and (mean[ds], stddev[ds]) as values
    '''
    taxonomies = []
    damage_states = []
    damage_dist = {}
    damage_dist_tax = {}
    for _, element in etree.iterparse(input_file):
        if element.tag == '%stotalDmgDist' % xmlNRML:
            taxonomy = 'All taxonomies'
            taxonomies.append(taxonomy)
            damage_states, damage_dist = parse_dmg_dist_total(element)
            damage_dist_tax[taxonomy] = damage_dist
        elif element.tag == '%sdmgDistPerTaxonomy' % xmlNRML:
            taxonomies, damage_states, damage_dist_tax = parse_dmg_dist_tax(element)
        else:
            continue
    return taxonomies, damage_states, damage_dist_tax


def set_up_arg_parser():
    """
    Can run as executable. To do so, set up the command line parser
    """
    parser = argparse.ArgumentParser(
        description='Convert NRML damage distribution files'
            'to csv files. To run just type: python parse_damage_dists.py '
            '--input-file=PATH_TO_DAMAGE_DIST_NRML_FILE ', add_help=False)
    flags = parser.add_argument_group('flag arguments')
    flags.add_argument('-h', '--help', action='help')
    flags.add_argument('--input-file',
        help='path to damage distribution NRML file (Required)',
        default=None,
        required=True)

    return parser

if __name__ == "__main__":

    parser = set_up_arg_parser()
    args = parser.parse_args()

    if args.input_file:
        damage_states, taxonomies, damage_dists = parse_damage_file(args.input_file)