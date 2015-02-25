# -*- coding: utf-8 -*-
"""
Created on Mon Jun  9 16:10:16 2014

@author: chiaracasotto
"""
import numpy as np
import os
import csv

def read_data(in_type):
    cd = os.getcwd()
    if in_type == 0:
        # Importing Damage Count Matrix from csv file
        input = cd+'/NDP/inputs/dcm.csv'
        with open(input, 'rb') as f:
            reader = csv.reader(f)
            newlist = [row for row in reader]
        newlist = newlist[1:]
        fdata = np.matrix(newlist, dtype = float)
        dcm = fdata[:,2:]
        im = fdata[:,1]
        totblg = np.sum(dcm[0])
        noLS = dcm.shape[1]-1
    else:
        input = cd+'/NDP/inputs/edp.csv'
        input2 = cd+'/NDP/inputs/limits.csv'
        with open(input, 'rb') as f:
            reader = csv.reader(f)
            newlist = [row for row in reader]
        newlist = newlist[1:]
        fdata = np.matrix(newlist, dtype = float)
        rec = fdata[:,0] # Vector of the numbers of Records
        im = fdata[:,1] # Vector of Intensity Measure of each record
        edp = fdata[:,2:] # Matrix of Engineering Demand Parameters for each building for each record
        totblg = edp.shape[1] # Number of buildings analysed
        # Reading limit states for each building
        with open(input2, 'rb') as f:
            reader = csv.reader(f)
            newlist = [row for row in reader]
        newlist = newlist[1:]
        newdata = np.matrix(newlist, dtype = float)
        newdata = newdata[:,1:]
        limits =  newdata.astype(np.float)
        noLS = limits.shape[1]
        # Create a matrix of limits for each building if limits is a vector
        if limits.shape[0]==1:
            limits = limits.repeat(edp.shape[1], axis=0) 

        # Assign damage state to each analysis          
        ds = np.matrix(np.empty(edp.shape))
        for blg in range(0,ds.shape[1]):
            a = np.matrix.nonzero(abs(edp[:,blg])<limits[blg,0])
            ds[a[0],blg] = 0
            for ls in range(0,limits.shape[1]):
                a = np.matrix.nonzero(abs(edp[:,blg])>limits[blg,ls])
                ds[a[0],blg] = ls+1

        # Damage Probability Matrix
        dcm = np.matrix(np.empty([len(ds),limits.shape[1]+1]))

        for line in range(0,len(ds)):
            for ls in range(0,limits.shape[1]+1):
                riga = ds[line]
                lriga = riga.tolist()
                cnt = len([j for j in lriga[0] if j == ls])
                dcm[line,ls] = cnt
                     
    return [dcm,totblg,im,noLS]
