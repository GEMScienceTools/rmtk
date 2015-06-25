# -*- coding: utf-8 -*-
"""
Created on Mon May 26 12:41:28 2014

@author: chiaracasotto
"""
import numpy as np

def spo2ida_get_pinch50_Rcap_pXXmXXcXXtXX(a,ac,T,meq,mpeak,Rmc):
    f_mXXtXX = np.matrix([[0.2391,    0.3846,    0.5834],
    [0.0517,    0.0887,    0.1351],
    [-1.2399,   -1.3531,   -1.4585],
    [-0.0976,   -0.1158,   -0.1317],
    [0.0971,    0.1124,    0.1100],
    [0.0641,    0.0501,    0.0422],
    [-0.0009,    0.0041,    0.0056],
    [0.0072,    0.0067,    0.0074]])
    
    f_p0mXXcXXtXX=np.matrix([[-0.2508,   -0.2762,   -0.2928],
    [-0.5517,   -0.1992,   -0.4394],
    [0.0941,   -0.0031,    0.0683],
    [0.0059,    0.0101,    0.0131],
    [0.1681,    0.2451,    0.1850],
    [0.1357,   -0.0199,    0.1783],
    [-0.0127,    0.0091,   -0.0305],
    [0.0010,   -0.0075,   -0.0066],
    [-0.1579,   -0.0135,    0.0027],
    [0.2551,   -0.0841,    0.0447],
    [-0.0602,    0.0222,   -0.0151],
    [0.0087,   -0.0003,   -0.0025]])

    ac=abs(ac);
    # After the final investigation on how backbones with same
    # meq,mpeak behave (while "a" changes), the conlcusion is that the
    # capacity is not exactly constant, but for all fractiles it
    # quickly travels from the p0-with-meq to the p100-with-mpeak
    # A further investigation has shown that the
    # Rfrac-pure-lag-fraction varies linearly from the Rfrac_p0mXXcXX
    # to the mpeak-value as a changes from 0 to 1 (again all systems
    # must have same meq,mpeak).
    # So this is what has been incorporated:

    # parameters are always mu-independent. That's how we fit them
    #  Rcap(mXX) = ac*exp( P3(logac) + P3(logac) * logT)
    
    # CAPACITY of mXX with same "ac"
    X = np.matrix([1,np.log(T),np.log(ac),np.log(ac)*np.log(T),np.power(np.log(ac),2), np.power(np.log(ac),2)*np.log(T),np.power(np.log(ac),3), np.power(np.log(ac),3)*np.log(T)])
    Rc_mXX =ac*np.exp(X*f_mXXtXX)
    # sort them from biggest to smallest, so they correspond to lines not caps!
    Rc_mXX = Rc_mXX.tolist()[0]
    Rc_mXX = Rc_mXX[::-1]
    # RATIO of the p0mXXcXX with mc=meq pure lag  over mXX pure lag. Always less than 1.
    X = np.matrix([np.log(meq),ac*np.log(meq),np.power(ac,2)*np.log(meq),np.power(ac,-1)*np.log(meq),np.log(meq)*np.log(T),ac*np.log(meq)*np.log(T),np.power(ac,2)*np.log(meq)*np.log(T),np.power(ac,-1)*np.log(meq)*np.log(T),np.log(meq)*np.power(np.log(T),2),ac*np.log(meq)*np.power(np.log(T),2),np.power(ac,2)*np.log(meq)*np.power(np.log(T),2),np.power(ac,-1)*np.log(meq)*np.power(np.log(T),2)])
    Rfrac_p0mXXcXX = np.exp(X*f_p0mXXcXXtXX)
    Rfrac_p0mXXcXX = Rfrac_p0mXXcXX.tolist()[0]
    Rfrac_p0mXXcXX = Rfrac_p0mXXcXX[::-1]
    # the pure-lag fraction varies linearly with "a", assuming mc is
    # such that both systems have same meq. 
    # RATIO of pXXmXXcXX with mc=meq pure lag  over mXX pure lag.
    # USUALLY higher than 1, especially if a>0.3
    Rfrac_pXXmXXcXX = np.array(Rfrac_p0mXXcXX) + a*(mpeak-np.array(Rfrac_p0mXXcXX))
    # so now Rcap is sorted also from largest value to smallest. 
    # So Rcap(1) is the 84% capacity that corresponds to 16% line.
    # Use the Rmc that corresponds to the pXX ending, NOT just p0
    # please!
    # CAPACITY of pXXmXXcXX
    Rcap = [Rmc[i] + (Rc_mXX[i] - 1)*Rfrac_pXXmXXcXX[i] for i in range(0,3)]
    #      ^^^    ^^^^^^^^^    ^^^^^^^^^^^^^
    #       |         |               |----> pure lag fraction
    #       |         |-----> pure lag of corresponding mXX
    #       |------->   end-of-hardening of corresponding pXX
    
    
    return [Rcap,Rc_mXX]
    
def spo2ida_get_mclough_Rcap_pXXmXXcXXtXX(a,ac,T,meq,mpeak,Rmc):
    f_mXXtXX = np.matrix([[0.2573,    0.3821,    0.5449],
    [0.0496,    0.0753,    0.0977],
    [-1.2305,  -1.3289,   -1.4270],
    [-0.0739, -0.0894,   -0.1035],
    [0.0780,    0.0929,    0.1060],
    [0.0452,    0.0392,    0.0467],
    [-0.0038,   -0.0005,    0.0039],
    [0.0019,    0.0027,    0.0058]])

    f_p0mXXcXX = np.matrix([[-0.5111,   -0.3817,   -0.4118],
    [-0.6194,   -0.3599,   -0.2610],
    [0.0928,  -0.0019,   -0.0070],
    [0.0163,  0.0186,    0.0158]])
    
    ac=abs(ac)
    
    X = np.matrix([1,np.log(T),np.log(ac),np.log(ac)*np.log(T),np.power(np.log(ac),2), np.power(np.log(ac),2)*np.log(T),np.power(np.log(ac),3), np.power(np.log(ac),3)*np.log(T)])
    Rc_mXX =ac*np.exp(X*f_mXXtXX)
    # sort them from biggest to smallest, so they correspond to lines not caps!
    Rc_mXX = Rc_mXX.tolist()[0]
    Rc_mXX = Rc_mXX[::-1]
    X = np.matrix([np.log(meq),ac*np.log(meq),np.power(ac,2)*np.log(meq),np.power(ac,-1)*np.log(meq)])
    Rfrac_p0mXXcXX = np.exp(X*f_p0mXXcXX)
    Rfrac_p0mXXcXX = Rfrac_p0mXXcXX.tolist()[0]
    Rfrac_p0mXXcXX = Rfrac_p0mXXcXX[::-1]
    
    Rfrac_pXXmXXcXX = np.array(Rfrac_p0mXXcXX) + a*(mpeak-np.array(Rfrac_p0mXXcXX))
    Rcap = [Rmc[i] + (Rc_mXX[i] - 1)*Rfrac_pXXmXXcXX[i] for i in range(0,3)]    
    return [Rcap,Rc_mXX]
    
def spo2ida_get_Rcap_pXXmXXcXXtXX(a,ac,T,meq,mpeak,Rmc,pw):
    [pRcap,pRc_mXX]=spo2ida_get_pinch50_Rcap_pXXmXXcXXtXX(a,ac,T,meq,mpeak,Rmc)
    [mRcap,mRc_mXX]=spo2ida_get_mclough_Rcap_pXXmXXcXXtXX(a,ac,T,meq,mpeak,Rmc)
    # Now average out the b0,b1 results from the two possible models.
    Rcap = pw*pRcap + (1-pw)*mRcap
    Rc_mXX = pw*pRc_mXX + (1-pw)*mRc_mXX
    return [Rcap,Rc_mXX]