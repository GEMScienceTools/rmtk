# -*- coding: utf-8 -*-
"""
Created on Thu May 22 16:29:32 2014

@author: chiaracasotto
"""

def regions2model(a,mc,ac,r, mf, mr):
    if (mc>1) and (mf>1):
        pxx = 1 
    else:
        pxx = 0
    if (ac!=0) and (mf>mc) and (mr>mc):
        mxx = 1  
    else: 
        mxx = 0
    if (r!=0) and (mf>mr):
        rxx = 1 
    else:
        rxx = 0
    return [pxx, mxx, rxx]