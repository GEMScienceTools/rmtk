'''
Post-process risk calculation data to convert loss curves into different
formats
'''

import argparse
import numpy as np
from lxml import etree

xmlNRML = '{http://openquake.org/xmlns/nrml/0.5}'
xmlGML = '{http://www.opengis.net/gml}'


def parse_single_loss_curve(element):
    '''
    Reads the loss curve element to return the longitude, latitude and
    poes and losses
    '''
    for e in element.iter():
        ref = element.attrib.get('assetRef')
        if e.tag == '%spos' % xmlGML:
            coords = str(e.text).split()
            lon = float(coords[0])
            lat = float(coords[1])
        elif e.tag == '%spoEs' % xmlNRML:
            poes = str(e.text).split()
            poes = map(float, poes)
        elif e.tag == '%slosses' % xmlNRML:
            losses = str(e.text).split()
            losses = map(float, losses)
        else:
            continue
    return lon, lat, ref, poes, losses


def parse_metadata(element):
    '''
    Returns the statistics
    '''
    metadata = {}
    metadata['statistics'] = element.attrib.get('statistics')
    metadata['quantile_value'] = element.attrib.get('quantileValue')
    metadata['investigationTime'] = element.attrib.get('investigationTime')
    metadata['unit'] = element.attrib.get('unit')
    metadata['lossType'] = element.attrib.get('lossType')
    return metadata


def LossCurveParser(input_file):

    refs = []
    longitude = []
    latitude = []
    losses = []
    poes = []
    metadata = {}

    for _, element in etree.iterparse(input_file):
        if element.tag == '%slossCurves' % xmlNRML:
            metadata = parse_metadata(element)
        elif element.tag == '%slossCurve' % xmlNRML:
            lon, lat, ref, poe, loss = parse_single_loss_curve(element)
            longitude.append(lon)
            latitude.append(lat)
            refs.append(ref)
            poes.append(poe)
            losses.append(loss)
        else:
            continue
    longitude = np.array(longitude)
    latitude = np.array(latitude)

    return refs, longitude, latitude, poes, losses


def parse_loss_file(input_file):
    '''
    Reads an xml loss curves file and returns a dictionary with
    asset (refs) as keys and (lon,lat,poe,loss) as values
    '''
    loss_curves = {}
    asset_refs = []
    for _, element in etree.iterparse(input_file):
        if element.tag == '%slossCurves' % xmlNRML:
            metadata = parse_metadata(element)
        elif element.tag == '%slossCurve' % xmlNRML:
            lon, lat, ref, poe, loss = parse_single_loss_curve(element)
            asset_refs.append(ref)
            loss_curves[ref] = loss, poe
        else:
            continue
    return metadata, asset_refs, loss_curves


def LossCurves2Csv(nrml_loss_curves):
    '''
    Writes the Loss curve set to csv
    '''
    refs, longitude, latitude, poes, losses = LossCurveParser(nrml_loss_curves)
    output_file = open(nrml_loss_curves.replace('xml', 'csv'), 'w')
    for iloc in range(len(refs)):
        print len(poes)
        poes_list = ','.join(map(str, poes[iloc]))
        losses_list = ','.join(map(str, losses[iloc]))
        output_file.write(str(refs[iloc])+','+str(longitude[iloc])+','+str(latitude[iloc])+','+poes_list+','+losses_list+'\n')
    output_file.close()


def set_up_arg_parser():
    """
    Can run as executable. To do so, set up the command line parser
    """
    parser = argparse.ArgumentParser(
        description='Convert NRML loss curves file to tab delimited '
        ' .txt files. Inside the specified output directory, create a .txt '
        'file for each stochastic event set.'
        'To run just type: python parse_loss_curves.py '
        '--input-file=PATH_TO_LOSS_CURVE_NRML_FILE ', add_help=False)
    flags = parser.add_argument_group('flag arguments')
    flags.add_argument('-h', '--help', action='help')
    flags.add_argument('--input-file',
                       help='path to loss curves NRML file (Required)',
                       default=None,
                       required=True)

    return parser

if __name__ == "__main__":

    parser = set_up_arg_parser()
    args = parser.parse_args()

    if args.input_file:
        metadata, asset_refs, loss_curves = parse_loss_file(args.input_file)
