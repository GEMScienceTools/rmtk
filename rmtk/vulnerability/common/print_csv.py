# -*- coding: utf-8 -*-
"""
Created on Thu Sep 25 16:21:11 2014

@author: chiaracasotto
"""
import csv

def print_outputs(output_file,header,n_lines,col_data):
    outfile = open(output_file, 'wt')
    writer = csv.writer(outfile, delimiter=',')
    writer.writerow(header)
    for j in range(0, n_lines):
        dat = [ele[j] for ele in col_data]
        writer.writerow(dat)
    outfile.close()