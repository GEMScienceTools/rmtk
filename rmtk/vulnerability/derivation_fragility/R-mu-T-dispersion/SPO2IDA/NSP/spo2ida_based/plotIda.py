# -*- coding: utf-8 -*-
"""
Created on Tue May 27 20:42:38 2014

@author: chiaracasotto
"""

import matplotlib.pyplot as plt
import numpy as np
import os

def plotIda(idacm,idacr,linew):
    cd = os.getcwd()
    colours = ['g','r','c']
    txt = ['84%','50%','16%']
    for q in range(0,3):
        plt.plot(idacm[q],idacr[q],color=colours[q],linewidth = linew,label=txt[q])
  
    plt.legend(loc='upper left',frameon = False)
    fig = plt.gcf()
    ax = fig.gca()
    ax.set_xticks(np.arange(0,np.max(idacm[0])+1,1))
    ax.set_yticks(np.arange(0,np.max(idacr[0])+1,1))
    plt.grid()
    plt.savefig(cd+'/outputs/IDA_curves.png')
    plt.show()
