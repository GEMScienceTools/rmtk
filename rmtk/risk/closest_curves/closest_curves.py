#!/usr/bin/env python

import os
import argparse
import operator
import numpy as np
import glob
from rmtk.parsers.hazard_parsers import HazardCurveXMLParser


def rmse(predictions, targets):
    difference = abs(predictions - targets)
    relative_difference = np.divide(difference, predictions)
    return np.sqrt((relative_difference** 2).mean())


def get_curves_matrix(hcm):
    """
    Store locations and poes in :class:`openquake.nrml.models.HazardCurveModel`
    in numpy array.
    """
    curves = []
    for loc, poes in hcm:
        curves.append(poes)
    return np.array(curves)


def get_header(hcm):
    """
    Obtain metadata in :class:`openquake.nrml.models.HazardCurveModel`
    in a string to be used as header
    """
    header = ','.join(
        ['%s=%s' % (k,v) for k,v in hcm.metadata.items()
        if v is not None and (k != 'imls' and k != 'imt' and k != 'investigation_time')]
    )
    return header


def get_time(hcm):
    """
    Obtain investigation time from :class:`openquake.nrml.models.HazardCurveModel`
    """
    for k,v in hcm.metadata.items():
        if k == 'investigation_time':
            time = '%s' % v
    return float(time)


def parse_hazard_curves(input_dir):
    """
    Read hazard curves in `input_dir` and save to .csv file
    with root name `file_name_root`
    """
    search_string = input_dir + '/*.xml'
    nrml_files = glob.glob(search_string)

    mean_poes = []
    branch_poes = {}
    time = 1.0

    for hc_file in nrml_files:
        file_name_root = os.path.splitext(hc_file)[0]
        output_file = '%s.csv' % file_name_root
        hcm = HazardCurveXMLParser(hc_file).parse()

        curves = get_curves_matrix(hcm)
        header = get_header(hcm)
        time = get_time(hcm)

        if header == 'statistics=mean':
            mean_poes = curves
        else:
            branch_poes[header] = curves

    return time, mean_poes, branch_poes


def poes_to_rates(time, poes):
    """
    Convert probabilities of exceedance to annual rates of exceedance
    """
    eps = 1.0e-7
    rates = -np.log(1.0 + eps - np.array(poes))
    rates = np.array(rates)/time
    return rates


def sort_closest_curves(distance):
    max_distance = max(distance.iteritems(), key=operator.itemgetter(1))[1]
    for branch_name in sorted(distance, key=distance.get, reverse=False):
        print branch_name, distance[branch_name]/max_distance


def compute_curves_distance(mean_rates, branch_rates):
    distance = rmse(mean_rates, branch_rates)
    return distance


def list_closest_curves(input_dir):
    time, mean_poes, branch_poes = parse_hazard_curves(input_dir)
    mean_rates = poes_to_rates(time, mean_poes)
    distance = {}
    for name, poes in branch_poes.iteritems():
        branch_rates = poes_to_rates(time, poes)
        distance[name] = compute_curves_distance(mean_rates, branch_rates)

    sort_closest_curves(distance)


def set_up_arg_parser():
    """
    Can run as executable. To do so, set up the command line parser
    """
    parser = argparse.ArgumentParser(
        description = 'List the logic-tree branches in descending order of '
            'branch hazard curve distance to mean hazard curve.'
            'To run type: python closest_curves.py '
            '--input-dir = PATH_TO_NRML_HAZARD_CURVES_DIRECTORY', add_help = False)
    flags = parser.add_argument_group('flag arguments')
    flags.add_argument('-h', '--help', action = 'help')
    flags.add_argument('--input-dir',
        help = 'path to NRML hazard curves directory (Required)',
        default = None,
        required = True)
    return parser


if __name__ == "__main__":

    parser = set_up_arg_parser()
    args = parser.parse_args()

    if args.input_dir:
        list_closest_curves(args.input_dir)
    else:
        parser.print_usage()
