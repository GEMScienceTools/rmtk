# -*- coding: utf-8 -*-
import os

def read_capacity_curves(folder):
    # This function converts capacity curves in csv to the RMTK format

    setSa = []
    setSd = []
    setSay = []
    setSdy = []
    
    for capacity_curve in os.listdir(folder):
        if capacity_curve.endswith(".csv"):
            Sa = []
            Sd = []
            Say = []
            Sdy = []
            file=open(folder+'/'+capacity_curve)
            lines=file.readlines()
            for line in lines:
                line = line.split(',')
                Sd.append(float(line[0]))
                Sa.append(float(line[1]))
            Sdy = Sd[1]
            Say = Sa[1]
            setSa.append(Sa)
            setSd.append(Sd)
            setSay.append(Say)
            setSdy.append(Sdy)
            
    out_file = open(folder+'/all_curves.csv','w')
    out_file.write('Vb-droof,FALSE\n')
    out_file.write('Vb-dfloor,FALSE\n')
    out_file.write('Sd-Sa,TRUE\n')
    periods = 'Periods [s]'
    heights = 'Heigths [m]'
    gammas = 'Gamma participation factors'
    Sdys = 'Sdy'
    Says = 'Say'
    for icc in range(len(setSa)):
        periods = periods+',0.62'
        heights = heights+',6.0'
        gammas = gammas+',1.24'
        Sdys = Sdys+','+str(setSdy[icc])
        Says = Says+','+str(setSay[icc])
        
    out_file.write(periods+'\n')
    out_file.write(heights+'\n')
    out_file.write(gammas+'\n')
    out_file.write(Sdys+'\n')
    out_file.write(Says+'\n')

    for icc in range(len(setSa)): 
        Sds = 'Sd'+str(icc+1)
        Sas = 'Sa'+str(icc+1)       
        for i in range(len(setSa[icc])):
            Sds = Sds+','+str(setSd[icc][i])
            Sas = Sas+','+str(setSa[icc][i])
        out_file.write(Sds+'\n')
        out_file.write(Sas+'\n')
    out_file.close()
            
read_capacity_curves('capacity_curves')