# -*- coding: utf-8 -*-
"""
Created on Mon May 26 17:40:04 2014

@author: chiaracasotto
"""
import numpy as np
def spo2ida_get_ab_mXXrXXtXX(ac,req,T,pw):
    fb0_mXXrXX=np.matrix([[-0.2226,    0.1401,    0.7604],
    [-0.0992,   -0.0817,   -0.1035],
    [-0.4537,   -0.5091,   -0.5235],
    [-0.0398,   -0.0236,   -0.0287],
    [0.0829,   -0.0364,   -0.0174],
    [0.0193,   -0.0126,   -0.0118],
    [-0.1831,   -0.2732,   -0.5651],
    [-0.0319,    0.0015,    0.0437],
    [0.1461,    0.1101,    0.0841],
    [-0.0227,   -0.0045,    0.0159],
    [-0.0108,    0.0333,    0.0033],
    [-0.0081,   -0.0000,    0.0033],
    [0.1660,    0.1967,    0.0929],
    [-0.0124,   -0.0304,    0.0130],
    [0.0273,    0.0396,    0.0580],
    [-0.0167,   -0.0209,   -0.0144],
    [-0.0182,    0.0311,    0.0221],
    [-0.0097,   -0.0047,    0.0007]])
    
    fb1_mXXrXX=np.matrix([[1.0595,    1.0635,    1.0005],
    [0.0236,    0.0177,    0.0283],
    [0.1237,    0.1466,    0.1607],
    [0.0111,    0.0048,   -0.0004],
    [-0.0023,    0.0102,    0.0021],
    [0.0008,    0.0019,    0.0035],
    [-0.0881,   -0.1044,   -0.1276],
    [-0.0077,   -0.0137,   -0.0413],
    [-0.0239,   -0.0090,   -0.0085],
    [0.0025,   -0.0014,   -0.0198],
    [0.0082,   -0.0003,    0.0037],
    [0.0007,   -0.0013,   -0.0043],
    [0.0317,    0.0038,    0.0673],
    [0.0006,    0.0065,    0.0074],
    [-0.0173,   -0.0484,   -0.0737],
    [0.0056,    0.0068,    0.0255],
    [0.0007,   -0.0112,   -0.0073],
    [0.0004,    0.0008,    0.0005]])
    
    # the full model for any of the three fractiles is:
    # lm = b0 + b1*lR (1)
    # or  mu = b0 * R^b1
    #   b0=P1(log(ac))*P(-1;1)(logR)*P2(logT)   b1= (same)

    # No matter what, this fuction only supports pinching model because I don't have the data for mclough.
    X=np.matrix([1,np.log(ac),np.log(r),np.log(ac)*np.log(r),np.power(np.log(r),-1),np.log(ac)*np.power(np.log(r),-1),np.log(T),np.log(ac)*np.log(T),np.log(r)*np.log(T),np.log(ac)*np.log(r)*np.log(T),np.power(np.log(r),-1)*np.log(T),np.log(ac)*np.power(np.log(r),-1)*np.log(T),np.power(np.log(T),2),np.log(ac)*np.power(np.log(T),2),np.log(r)*np.power(np.log(T),2),np.log(ac)*np.log(r)*np.power(np.log(T),2),np.power(np.log(r),-1)*np.power(np.log(T),2),np.log(ac)*np.power(np.log(r),-1)*np.power(np.log(T),2)])

    b0 = X*fb0_mXXrXX
    b1 = X*fb1_mXXrXX
    return [b0, b1]