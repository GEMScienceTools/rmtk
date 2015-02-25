# -*- coding: utf-8 -*-
"""
Created on Thu May 22 17:39:32 2014

@author: chiaracasotto
"""
import numpy as np
from spo2ida_get_ab_pXXtXX3 import spo2ida_get_ab_pXXtXX
from spo2ida_get_ab_pXXtXX3 import spo2ida_get_Rmc
from spo2ida_get_Rcap import spo2ida_get_Rcap_pXXmXXcXXtXX
from spo2ida_get_ab_mXXrXX import spo2ida_get_ab_mXXrXXtXX
from spline import spline

def model_pXX(idacm,idacr,a,mc,T,pw,N):
    "This function gives R of the ida curve corresponding to the hardening branch"
#    a = params[0]
#    mc = params[1]
#    T=params[2]
#    pw=params[3]
    # the full model for any of the three fractiles is:
    # lm = b0*lR + b1*lR^2 (1)
    # or  mu = exp ( b0*logR + b1*logR^2)
    
    # Step 1: get the b0 and b1 parameters of the regression
    # The coefficients bo and b1 are a function of a and T
    #   b0=P4(a) 
    #   b1=P4(a)

    # Step 2: calculate the "end-of-hardening-R" and the corresponding local tangent slope.
    # to find the R at mu=mc, we need to solve (1)
    #  NOTE : mc>1 so log(mc)>0 always
    # b1*logR^2 + b0*logR - log(mc) = 0
    #   Diakrinousa = sqrt(b0^2 + 4*b1*log(mc)) > 0 (always)
    #    logR(1) = ( -b0 + sqrt(Diakr) ) / 4*b1 
    #    logR(2) = ( -b0 - sqrt(Diakr) ) / 4*b1
    # so just pick the root that is greater than one.

    # Step 1:
    [b0,b1]=spo2ida_get_ab_pXXtXX(a,T,pw)
    # Step 2
    [Rmc,slmc] = spo2ida_get_Rmc(mc,b0,b1)

    for i in range(0,3):
        # the hardening part ends at m==mc
        # compute the R-values. Note that "1" is included though it
        # should not.
        RpXX=np.linspace(1,Rmc[i],N+1)
        # try not to repeat the end of the last segment (i.e. remove "1")!
        RpXX=RpXX[1:]

         # method 1: keep lower part of mXX and multiply by local Rmc
         # slope, if it is greater than one
        idacr[i]=idacm[i]+RpXX.tolist()
        newMu = np.exp(b0[i]*np.log(RpXX) + b1[i]*np.power(np.log(RpXX),2))
        idacm[i] = idacm[i]+newMu.tolist()
         
    return [idacm, idacr,Rmc,slmc]
    
def model_mXX(idacm,idacr,a,ac,mc,T,pw,mr,meq,mend,mpeak,mf,Rmc,slmc,filletstyle,N):
    [Rcap,Rcap_mXX]=spo2ida_get_Rcap_pXXmXXcXXtXX(a,ac,T,meq,mpeak,Rmc,pw)
    [b0,b1]=spo2ida_get_ab_pXXtXX(0,T,pw) #This b0 will be used if filletstyle = 3
    for i in range(0,3):
     # the softening part starts at m=mc and ends at m==mr
     # compute the R-values. Note that "mc" is included though it
     # should not.
     #keyboard
        if filletstyle==0 or filletstyle==1 or filletstyle==2:
            # don't do any cute tricks. Just extend the pXX linearly
            # following the final slmc slope.
            RmXX=np.linspace(Rmc[i],Rcap[i],N+1)
            # try not to repeat the end of the last segment
            RmXX=RmXX[1:]
            newMu = mc+(RmXX-Rmc[i])*slmc[i]
            # this is something that I (Chiara) added, check with Dimitrios if it's ok
            if newMu[-1]>mf:
                f = np.nonzero(newMu<=mf)
                RmXX=RmXX[f]
                newMu = mc+(RmXX-Rmc[i])*slmc[i]
                
            idacr[i]=idacr[i] + RmXX.tolist()
            idacm[i]=idacm[i] + newMu.tolist()
            
        else:
#            # use a repeated midpoint insertion and a control polygon with spcrv to get the desired filleting.
#            # intersection of flatline and the tangent at end of pXX
            xi=(np.log(Rcap[i])-np.log(Rmc[i]))*slmc[i] + np.log(mc)
            # Controlling Polygon cp:
            cp_mu = [2*np.log(mc)-xi, xi, 2*np.log(mend)-xi]
            cp_R = [2*np.log(Rmc[i])-np.log(Rcap[i]), np.log(Rcap[i]), np.log(Rcap[i])]
            [newcx,newcy] = spline(cp_mu,cp_R)
            x_mc = np.nonzero(newcx>mc)[0]
            indy = [ele for ele in x_mc if newcx[ele]<=mr]
#            # add a "final point" right on mr. The filleting will  never do that by default, so make sure it happens!
#            # this is especially critical if the real mr > mf, so we are supplied a mr==mf here. So capacity really depends on us
#            # providing this point.
            m_rXX = mr
            if len(indy) == 0:
#            # then probably mc slightly less than mr. Then just interpolate between the closest values 
#            # surrounding "mc" (or "mr" they are actually the same values since mc,mr are so close).
                i1=np.max(np.nonzero(newcx<=mc))
                i2=i1+1
            else:
                if indy[-1]==len(newcx)-1:
#                # Linear extrapolation. Just so that you get a point right on the "mf" and capacity gets displayed correctly
                    i1=indy[-2] 
                    i2=indy[-1] 
                else:
#                # Interpolation between indy(end) and the indy(end)+1 point (if it has been calculated).
                    i1=indy[-1]
                    i2=indy[-1]+1
            
            R_rXX = newcy[i2]+(newcy[i2]-newcy[i1])/(newcx[i2]-newcx[i1])*(mr-newcx[i2])
            
            idacm[i]=idacm[i] + newcx[indy].tolist() + [m_rXX]
            idacr[i]=idacr[i] + newcy[indy].tolist() + [R_rXX]
                    
    return [idacm,idacr]

# This has to be checked   
def model_rXX(idacm,idacr,a,ac,mc,mr,mf,r,req,T,pw,filletstyle,N):
    [b0,b1]=spo2ida_get_ab_mXXrXXtXX(ac,req,T,pw)
    for i in range(0,3): 
        Rmr = idacr[i][-1]
        # if intersection of rXX "secant" with flatline is earlier
        # than mr, calculate only points beyond mr. This situation
        # should be extremely rare, unless r very close to 1. Also
        # notice that if mi > mf, then rXX is not present in THIS
        # fractile. This is a very usual situation for 84%-line.
        real_mi=max( np.exp(b0[i] + np.log(Rmr)*b1[i]), mr)
        # We will still use "real_mi" for our spline filleting, so
        # that the filleting will be independent of "mf".
        mi = min( mf, real_mi)
        if filletstyle == 0:
            # keyboard
            m_rXX = np.linspace(mi,mf,N+1);
            # the residual part starts at mr and ends at m==mf
            if mi<mf:
            # method 1: Don't do anything fancy, just extend the
            # "flatline" that almost got through at mr (this will be at
            # a height slightly less than the flatline that would have
            # appeared without the rXX) all the way to the intersection
            # with  the  "secant" of rXX. 
                R_rXX = np.exp((np.log(m_rXX)-b0[i])/b1[i])
            else: 
            # mf has chopped us off before the secant can manifest itself
                R_rXX = np.repeat(Rmr,len(m_rXX))
            
            idacr[i]=idacr[i]+R_rXX.tolist()
            idacm[i]=idacm[i]+m_rXX.tolist()
        else:
            # Use a spline curve to connect the different branches of the IDA curves
            if round(np.log(idacr[i][-1])-np.log(idacr[i][-2]),3)!= 0: # how much precision??
                slope_mXXend = (np.log(idacm[i][-1])-np.log(idacm[i][-2]))/(np.log(idacr[i][-1])-np.log(idacr[i][-2]))
                
                if slope_mXXend == b1[i]:
#                   if this causes the secant and the tangent to intercept lower than Rmr, the next "if" will fix it.
#                   actually I don't expect this piece of code to ever need to run. It will be a wild case indeed!
                    slope_mXXend = b1[i] + 0.05
                
                int_mXXend = np.log(mr) - slope_mXXend * np.log(Rmr)
                lRmi = (int_mXXend-b0[i])/(b1[i]-slope_mXXend)

            else:
#                The end of the mXX is indeed flat! so the secant and the flat, intersect at the Rmr height! No need for fancy
#                interpolation or intersection searching!
                lRmi = np.log(Rmr)

#            Prevent pathologies of the fitting process that can cause the secant and the tangent to meet at Rmi < Rmr. There are
#            two such cases. Also, sometimes the tangent is parallel to the secant. Improbable but keep it in mind.   
            
            if lRmi < np.log(Rmr):
#           This may happen for very large r-values. The two lines are intersecting lower that Rmr, or they are parallel
                if b1[i]>=slope_mXXend:
#               secant is softer and lower than the tangent."soften" the tangent to reach the secant.
                    slope_mXXend = b1[i] + 0.05
                else:
#               "secant" is harder and above the tangent. "Harden" the tangent to reach the secant.
                    slope_mXXend = b1[i] - 0.05
 
                int_mXXend = np.log(mr) - slope_mXXend * np.log(Rmr)
                lRmi = (int_mXXend-b0[i])/(b1[i]-slope_mXXend)
            
            new_Rmi = np.exp(lRmi)
            lmmi = b0[i]+b1[i]*lRmi
            new_mmi = np.exp(lmmi)
            
            # Control points for spline fitting
            cp_mu = [2*np.log(mr)-lmmi, lmmi, 3*lmmi] 
            cp_R = [2*np.log(Rmr) - lRmi, lRmi, (3*lmmi-b0[i])/b1[i]]
#           the control polygon stops at 3*mi, so points will be produced up to 2*mi? At least that is where the filleting
#           spline should touch the secant (smoothly)
            [newcx,newcy] = spline(cp_mu,cp_R)
#            sometimes, when mf is very close to mc or mr, the spline fitting will not generate any points within the 
#            interval (mc,mf) or (mr,mf). The trick is to get the closest point that spcrv generates plus the point 
#           AT mc or mr and linearly interpolate (although adding the flatline there should be ok in most cases! 
            x_mc = np.nonzero(newcx>mr)[0]
            indy = [ele for ele in x_mc if newcx[ele]<=mf]
            
#            add some more points along the "secant" if mf is larger than the filleting length. The filleting is supposed to
#            stop at the midpoint of the last segment, so about mu=2*mi. Actually, now with the new fitting it is
#            exp(3*lmmi-lmmi)=new_mmi^2
            
            if mf > np.power(new_mmi,2):
                m_rXX = np.linspace(new_mmi^2,mf,N+1)
                m_rXX = m_rXX
                R_rXX = np.exp((np.log(m_rXX)-b0[i])/b1[i])
            else:
                # add a "flatline point" right on mf. The filleting will never do that by default, so make sure it happens!
                m_rXX = mf
                if len(indy) == 0:
                # then probably mr slightly less than mf (could be just round-off error sometimes). Then just interpolate
                # between the closest values surrounding "mr" (or "mf" they are actually the same values since mr,mf are so close).
                    i1 = np.max(np.nonzero(newcx<=mr))
                    i2 = i1+1
                else:
                    if indy[-1]==len(newcx)-1:
                    # a linear extrapolation. Just so that you get a point right on the "mf" and capacity gets displayed
                    # correctly
                        i1=indy[-2]
                        i2=indy[-1]
                    else:
                    # Better to interpolate between indy(end) and the indy(end)+1 point (if it has been calculated).
                        i1=indy[-1]
                        i2=indy[-1]+1
                        
            R_rXX = newcy[i2]+(newcy[i2]-newcy[i1])/(newcx[i2]-newcx[i1])*(mf-newcx[i2]) 

            idacm[i]=idacm[i] + newcx[indy].tolist() + [m_rXX]
            idacr[i]=idacr[i] + newcy[indy].tolist() + [R_rXX]
     
    return [idacm,idacr]

