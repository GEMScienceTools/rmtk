# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

"""
Created on Wed May 21 18:16:53 2014

@author: chiaracasotto
"""
import matplotlib.pyplot as plt

def spo2ida_spo(mc,a,ac,r,mf,plotflag,linew,fontsize):
    spocm = [0]
    spocr = [0]
    # End of Elasticity points
    spocm.append(1)
    spocr.append(1)
    # End of hardening points
    spocm.append(min(mc,mf))
    spocr.append(1+(spocm[2]-1)*a)
    # End of softening points
    spocm.append(min(mf,spocm[2]-(r-spocr[2])/ac))
    if r == 0 and mf>spocm[3]:
        spocr.append(0)
    else:
        spocr.append(spocr[2]-(spocm[3]-spocm[2])*ac)
    # End of plateu point
    spocr.append(r)
    spocm.append(mf)

    spocr.append(0)
    spocm.append(mf)    
    # Get which regions have been defined
    # [pxx, mxx, rxx] = region2model(a, mc, ac, r, mf)
    
    # Now plot if plotflag = 1
    if plotflag == 1:
        plt.plot(spocm,spocr,linewidth = linew,label = 'SPO curve')
        plt.xlabel('ductility, mu = delta / delta(yield)',fontsize=fontsize)
        plt.ylabel('strength reduction factor, R = S_a / S_a(yield)',fontsize=fontsize)
        plt.suptitle('spo2ida', fontsize=fontsize)
        plt.legend(loc='upper left',frameon = False)
       
    return [spocm, spocr]

# <codecell>


# <codecell>


