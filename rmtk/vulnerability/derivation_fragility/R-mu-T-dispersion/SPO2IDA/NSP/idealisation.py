# -*- coding: utf-8 -*-
"""
Created on Wed May 28 15:23:24 2014

@author: chiaracasotto
"""
import numpy as np
import matplotlib.pyplot as plt

def bilinear(droof,Vb,flag,linew,fontsize,units, blg):
#   FEMA method
    droof = np.array(droof)
    Fy = np.max(Vb)
    du = np.max(droof)
    for index, item in enumerate(Vb):
        if item >= Fy:
            break   
    Ay = 0.6*Fy
    Ax = np.interp(Ay, Vb[0:index],droof[0:index])
    slp = Ay/Ax
    dy = Fy/slp
    
    if flag:
        # Plot pushover curve and bilinear curve
        plt.plot(droof,Vb,color='b',label='pushover input',linewidth=linew)
        x = np.array([0, dy,du])
        y = np.array([0, Fy, Fy])
        plt.plot(x,y,color='r',marker = 'o',linewidth=linew,label='bilinear idealisation')
        plt.xlabel('roof displacement, droof '+units[0],fontsize = fontsize)
        plt.ylabel('base shear, Vb '+units[1],fontsize = fontsize)
        plt.suptitle('Pushover curve - blg n.'+str(blg),fontsize = fontsize)
        plt.legend(loc='lower right',frameon = False)
        plt.show()
        
    return [dy,du,Fy]
    
def quadrilinear(droof,Vb,flag,linew,fontsize,units, blg):
    droof = np.array(droof)
    Fmax = np.max(Vb)
    for index, item in enumerate(Vb):
        if item >= Fmax:
            break
    fmax = index
    dmax = droof[index]
 
#   Yielding point:
#   Vulnerability guidelines method
#   Find yielding displacement with equal energy principle n the interval from 0 to Dmax
    Areas = np.array([(Vb[i+1]+Vb[i])/2 for i in range(0,fmax)])
    dd = np.array([droof[i+1]-droof[i] for i in range(0,fmax)])    
    Edmax = np.sum(dd*Areas) #Area under the pushover curve in the interval from 0 to Dmax         
    dy = 2*(dmax-Edmax/Fmax)
    Fy = Fmax
    
    #   Onset of plateu
    #   Find were slope of pushover curve before decreasing in the plateu
    Vb_norm = Vb[fmax::]/Fy
    d_norm = droof[fmax::]/dy
    slp = [(Vb_norm[i]-Vb_norm[i-1])/(d_norm[i]-d_norm[i-1]) for i in xrange(1,len(Vb_norm))]    
    indy_soft = np.nonzero(abs(np.array(slp))>0.3)   
    if len(indy_soft[0])>1:
        fmin = indy_soft[0][-1]+fmax
        Fmin = Vb[fmin]
        dmin = droof[fmin]
            #   Onset of softening
        #   Find yielding displacement with equal energy principle n the interval from Dmax to Dmin (onset of plateu)
        Areas = np.array([(Vb[i+1]+Vb[i])/2 for i in range(fmax,fmin)])
        dd = np.array([droof[i+1]-droof[i] for i in range(fmax,fmin)])
        Edmin = np.sum(dd*Areas)
        ds = 2/(Fmax-Fmin)*(Edmin - (dmin-dmax)*Fmax + 0.5*dmin*(Fmax-Fmin))
        du = np.max(droof)   
        if ds<dy: ds = dy
        if ds>du: ds=du        
        #   Residual Plateu
        if len(indy_soft[0])>0:
            Areas= np.array([(Vb[i+1]+Vb[i])/2 for i in range(fmin,len(Vb)-1)])
            dd = np.array([droof[i+1]-droof[i] for i in range(fmin,len(Vb)-1)])
            Edplat = np.sum(dd*Areas)
            Fres = Edplat/(droof[-1]-dmin)
            slp_soft = abs((Fmax-Fmin)/(ds-dmin))
            dmin = dmin+(Fmin-Fres)/slp_soft
            if dmin>du:
                dmin = du
                Fmin = Vb[-1]
            else:
                Fmin = Fres        
    else:
        fmin = len(Vb)-1
        Fmin = Fmax
        dmin = droof[fmin]
        ds = dmin
        du = dmin
    
    if flag:
        # Plot pushover curve and bilinear curve
        plt.plot(droof,Vb,color='b',linewidth=linew,label='pushover input')
        x = np.array([0, dy, ds, dmin, du])
        y = np.array([0, Fy, Fmax, Fmin, Fmin])
        plt.plot(x,y,color='r',marker = 'o', linewidth=linew, label='quadrilinear idealisation')
        plt.xlabel('roof displacement, droof '+units[0],fontsize = fontsize)
        plt.ylabel('base shear, Vb '+units[1],fontsize = fontsize)
        plt.suptitle('Pushover curve - blg n.'+str(blg),fontsize = fontsize)
        plt.legend(loc='lower right',frameon = False)
        plt.show()
    return [dy,ds,dmin,du,Fy,Fmax,Fmin]