'''
Post-process damage calculation outputs to plot damage distibution charts
'''

import os
import csv
import argparse
import numpy as np
from collections import OrderedDict
from matplotlib import pyplot
from mpl_toolkits.mplot3d import Axes3D
import parse_damage_dist as parsedd

xmlNRML = '{http://openquake.org/xmlns/nrml/0.4}'
xmlGML = '{http://www.opengis.net/gml}'

def parse_taxonomy_file(taxonomy_file):
    '''
    Reads a txt file with a list of taxonomies and returns an array
    '''
    taxonomy_list = []
    file = open(assets_file,'r')
    taxonomy_list = file.read().split(',')
    file.close()
    return taxonomy_list

def plot_damage_dist(damage_file, taxonomy_list=[], plot_3d=False, export_png=False):
    '''
    Plots the damage distribution for the specified taxonomies
    '''
    taxonomies, damage_states, damage_dist_tax = parsedd.parse_damage_file(damage_file)
    print damage_states
    if taxonomy_list:
        taxonomies = taxonomy_list

    indX = np.arange(len(damage_states))  # the x locations for the groups
    indZ = np.arange(len(taxonomies))  # the y locations for the groups
    error_config = {'ecolor': '0.3', 'linewidth': '2'}
    bar_width = 0.3
    padding_left = 0

    if plot_3d:
        fig = pyplot.figure(figsize = (16, 9))
        ax = fig.add_subplot(111, projection='3d')
        bar_width = 0.5
        z = 0
        for tax in taxonomies:
            z = z + 1
            means = []
            damage_dist = damage_dist_tax[tax]
            for ds in damage_states:
                dd = damage_dist[ds]
                means.append(dd[0])
            xs = indX
            ys = [x / sum(means) for x in means]
            zs = z

            ax.bar(indX, height=ys, zs=z, zdir='y', width=bar_width, color='IndianRed', linewidth=1.5, alpha=0.6)

        ax.set_xticks(indX+padding_left+bar_width/2, minor=False)
        ax.set_xticklabels(damage_states)
        ax.set_xlabel('Damage States', fontsize = 16)

        ax.set_yticks(indZ+1, minor=False)
        ax.set_yticklabels(taxonomies)
        ax.set_ylabel('Taxonomies', fontsize = 16)

        ax.set_zlabel('Damage Fractions', fontsize = 16)

        if export_png:
            pyplot.savefig('damage_dist_3d', format = 'png')
        pyplot.show()
        pyplot.clf()
    else:
        for tax in taxonomies:
            means = []
            stddevs = []
            damage_dist = damage_dist_tax[tax]
            for ds in damage_states:
                dd = damage_dist[ds]
                means.append(dd[0])
                stddevs.append(dd[1])
            fig = pyplot.figure(figsize = (16, 9))

            pyplot.bar(indX+padding_left, height=means, width=bar_width, yerr=stddevs, error_kw=error_config, color='IndianRed', linewidth=1.5)
            pyplot.title('Damage distribution (' + tax + ')', fontsize = 20)
            pyplot.xlabel('Damage state', fontsize = 16)
            pyplot.ylabel('Number of assets in damage state', fontsize = 16)
            pyplot.xticks(indX+padding_left+bar_width/2., damage_states)
            pyplot.margins(.25,0)
            if export_png:
                pyplot.savefig(tax, format = 'png')
            pyplot.show()
            pyplot.clf()

def set_up_arg_parser():
    """
    Can run as executable. To do so, set up the command line parser
    """
    parser = argparse.ArgumentParser(
        description = 'Convert NRML loss curves file to tab delimited '
            ' .txt files. Inside the specified output directory, create a .txt '
            'file for each stochastic event set.'
            'To run type: python plot_damage_dist.py '
            '--input-file = PATH_TO_LOSS_CURVE_NRML_FILE '
            '--taxonomy_list = LIST_OF_ASSETS ', add_help = False)
    flags = parser.add_argument_group('flag arguments')
    flags.add_argument('-h', '--help', action = 'help')
    flags.add_argument('--input-file',
        help = 'path to loss curves NRML file (Required)',
        default = None,
        required = True)
    flags.add_argument('--assets-list',
        help = 'path to loss curves NRML file (Required)',
        default = [],
        required = False)
    return parser

if __name__ ==  "__main__":

    parser = set_up_arg_parser()
    args = parser.parse_args()

    if args.input_file:
        if args.taxonomy_list:
            plot_damage_dist(args.input_file, taxonomy_list, log_scale_x=True, log_scale_y=True, export_png=False)
        else:
            plot_damage_dist(args.input_file, taxonomy_list, log_scale_x=True, log_scale_y=True, export_png=False)
    else:
        parser.print_usage()