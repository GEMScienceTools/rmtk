# -*- coding: utf-8 -*-
"""
Created on Fri May 23 15:48:20 2014

@author: chiaracasotto
"""

import numpy as np
def spo2ida_get_pinch50_ab_pXXtXX(a,T):
    fb0_pXXtXX=np.matrix([[-0.9309,  0.0288,  0.2987],
    [ 0.43  , -0.1718,  0.0438],
    [-0.2934,  0.1189, -0.1008],
    [ 0.3409, -0.0986, -0.0267],
    [ 0.7201,  0.8073,  0.0962],
    [ 0.3105, -0.2548,  0.3569],
    [-0.3343, -0.0561, -0.4138],
    [ 0.0778, -0.343 , -0.151 ],
    [ 0.1358, -0.85  , -0.4004],
    [-0.7301,  0.4165, -0.3644],
    [ 0.6055, -0.0806,  0.4698],
    [-0.4094,  0.4322,  0.1895]])
    
    fb1_pXXtXX=np.matrix([[0.1151, -0.4671, -0.5994],
    [-0.0940,    0.4071,    0.2858],	   
    [ 0.0539,   -0.2373,   -0.1310],
    [ 0.0073,    0.4093,    0.4984],
    [-0.4092,   -1.0761,   -0.9235],
    [ 0.1534,    0.7899,    0.5074],
    [ 0.0216,   -0.2518,   -0.0910],
    [ 0.1651,    0.6914,    0.7160],
    [ 0.2733,    1.5106,    1.5379],
    [-0.0338,   -1.1673,   -0.7999],
    [-0.0801,    0.4927,    0.2387],
    [-0.1586,   -1.0815,   -1.2277]])
    
    X=np.matrix([1, np.log(T), np.power(np.log(T),2), np.power(np.log(T+1),-1),a, a*np.log(T), a*np.power(np.log(T),2), a*np.power(np.log(T+1),-1),np.sqrt(a),np.sqrt(a)*np.log(T),np.sqrt(a)*np.power(np.log(T),2),np.sqrt(a)*np.power(np.log(T+1),-1)])

    b0 = np.exp(X*fb0_pXXtXX)
    b1 = np.exp(X*fb1_pXXtXX)-1       
    return [b0,b1]
    
def spo2ida_get_mclough_ab_pXXtXX(a,T):
    fb0_pXXtXX=np.matrix([[-0.6157,   -0.1842,    0.2155],
    [0.0260,   -0.0027,    0.0760],
    [0.0140,    0.0215,   -0.1458],
    [0.8605,    0.4986,    0.1693],
    [0.2264,    0.2026,    0.4712],
    [-0.3041,   -0.3542,   -0.7131],
    [-0.3316,   -0.3536,   -0.3827],
    [-0.2613,   -0.2011,   -0.5240],
    [0.2689,    0.3055,    0.8093]])
        
    fb1_pXXtXX=np.matrix([[0.1433,    0.0882,    0.0552],
    [-0.1074,   -0.1635,   -0.3562],
    [0.0538,    0.1062,    0.2745],
    [-0.1705,   -0.1486,   -0.1009],
    [-0.0813,   -0.1489,   -0.3903],
    [0.1661,   0.2618,    0.5810],
    [0.0313,    0.0587,    0.0363],
    [0.1957,    0.3185,    0.7552],
    [-0.2086,   -0.3550,   -0.8369]])
        
    X=np.matrix([1, np.log(T), np.power(np.log(T),2),a, a*np.log(T),a*np.power(np.log(T),2),np.sqrt(a),np.sqrt(a)*np.log(T),np.sqrt(a)*np.power(np.log(T),2)])
    
    b0 = np.exp(X*fb0_pXXtXX)
    b1 = np.exp(X*fb1_pXXtXX)-1        
    return [b0,b1]
        
def spo2ida_get_ab_pXXtXX(a,T,pw):      
    [pb0,pb1]=spo2ida_get_pinch50_ab_pXXtXX(a,T);
    [mb0,mb1]=spo2ida_get_mclough_ab_pXXtXX(a,T);

    # Now average out the b0,b1 results from the two possible models.
    b0 = pw*pb0 + (1-pw)*mb0;
    b1 = pw*pb1 + (1-pw)*mb1;
    b0 = b0.tolist()[0] # converting matrix into list
    b1 = b1.tolist()[0]
    return [b0,b1]
    
def spo2ida_get_Rmc(mc,b0,b1):
    # Given the b0,b1 parameters of all the fractile IDA curves 
    # (calculated using the spo2ida_get_ab_pXX(a)) we also calculate
    # the R-value and local tangent slope at any given ductility "m"
    # along the 3 IDAs. In all cases we are actually interested in
    # getting the R-value at "end-of-hardening"
    b0 = np.array(b0) #converting list in array to multiply vectors by scalars
    b1 = np.array(b1)
    # solution 1 
    Rmc = []
    slmc = []
    for i in range(0,3):
        if b1[i]!=0:
            # Solution of 2nd order polynomial
            Delta = np.power(b0[i],2) + 4*b1[i]*np.log(mc)
            lRmc1=(np.divide(-b0[i] + np.sqrt(Delta),2*b1[i]))
        else:
            # solution of 1st order polynomial
            lRmc1=(np.divide(np.log(mc),b0[i]))
            
        Rmc.append(np.exp(lRmc1))
        slmc.append(b0[i] + b1[i]*2*lRmc1)
       
    return [Rmc,slmc]