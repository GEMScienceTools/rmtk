# -*- coding: utf-8 -*-
"""
Spyder Editor

This temporary script file is located here:
/Users/chiaracasotto/.spyder2-27/.temp.py
"""

import numpy as np
# Import functions
from spo2ida_spo import spo2ida_spo
from regions import regions2model
from models import model_pXX
from models import model_mXX
from models import model_rXX
from plotIda import plotIda
      
def spo2ida_allT(mc,a,ac,r,mf,T,pw,plotflag,filletstyle,N,linew,fontsize):
    "A vary general routine aimed at moving from an SPo to an IDA for SDOF systems"
    
    # Input for the moment is event-drifts and corresponding
    # slopes on SPO. Here we assume you approximate your backbone with linear segments  
    # 
    # INPUT 
    #  mc      : mu of end of hardening slope
    #  a       : hardening slope in [0,1]
    #  ac      : negative (capping) slope in [0.02, 4]
    #  r       : Residual plateau height, a fraction of Fy
    #  mf      : fracturing mu (end of SPO)
    #  T       : period (sec)
    #  pw      : pinching model weight.
    # plotflag : if non-zero, plot the SPO plus 3 fractile IDA curves, 
    #             otherwise not. If it is a 4-component vector, each
    #             element corresponds to one of the following curves:
    #             SPO, 16%,50%,84%.
    #             Also, in all cases use figure(plotflag(i)) for the
    #             plotting of i-th line (e.g., plotflag==[2,0,2,0], 
    #             plots the SPO and the 50%-IDA in figure 2.
    #  N       : number of points per segment. For a full SPO (pXXmXXrXX)
    #             we have 3 segments???
    # linew    : line width for plots
    # fontsize : fontsize used for labels, graphs etc. 
    # OUTPUT
    #  spocm, spocr : The SPO curve points in normalized m,f coords
    #  idacm, idacr : same as above for the IDA. The three
    #                             arrays are the 16,50,84 curves (demand-wise) 
    #-------------------------------------------------------
    ac=abs(ac);
    
    # Compute and plot the SPO curve
    [spocm, spocr]=spo2ida_spo(mc,a,ac,r,mf,plotflag,linew,fontsize)

# <codecell>

    # Get missing parameters of spo curve
    mr = mc+(1+(mc-1)*a-r)/ac # get_mr(a,ac,mc,r)
    rpeak = 1 + a*(mc-1) # get_rpeak
    mend=mc + rpeak/abs(ac) # get mend(a,ac,mc)
    meq=mend - 1/abs(ac) # get meq(a,ac,mc)
    Rpeak = 1 + min(a,0.05)*(mc-1)
    req = r/Rpeak # get req(a,mc,r)
    mpeak=mend*abs(ac)/(1+abs(ac)) # get mpeak(a,ac,mc)

    # Branches present in the spo curve? for each region (hardening, softening, residual) a flag is given back by the function 
    [pxx, mxx, rxx] = regions2model(a,mc,ac,r, mf, mr)
    # if mf is really small it may influence some of the above since mc denotes end of pXX fitting, reduce it if mf is smaller
    mc = min(mc,mf)
    # since mr denotes the end of mXX region, if mf is smaller, reduce it.
    mr = min(mr,mf)
    
    # Set elastic part
    idacm = [np.linspace(0,1,N+1).tolist()]*3
    idacr = [np.linspace(0,1,N+1).tolist()]*3
    
    if pxx: # set hardening part
        [idacm,idacr,Rmc,slmc]=model_pXX(idacm,idacr,a,mc,T,pw,N)
    else:
        # This is not a good idea
        Rmc=[1,1,1]
        slmc=[1,1,1]

    if mxx: # set the mXX part
        [idacm,idacr]=model_mXX(idacm,idacr,a,ac,mc,T,pw,mr,meq,mend,mpeak,mf,Rmc,slmc,filletstyle,N)

    if rxx: # set the rXX part
        [idacm,idacr]=model_rXX(idacm,idacr,a,ac,mc,mr,mf,r,req,T,pw,filletstyle,N)

    for i in range(0,3):
        #add a flatline at fracture
        idacr[i]=idacr[i]+[idacr[i][-1]]+[idacr[i][-1]]
        idacm[i]=idacm[i]+[mf,mf+2]
    
    if plotflag == 1:
        plotIda(idacm,idacr,linew)
    
    return [idacm, idacr]