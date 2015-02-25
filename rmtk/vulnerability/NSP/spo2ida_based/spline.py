# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import numpy as np

def spline(cp_mu,cp_R):
    
    N = [4, 6, 10, 18, 34]
    mu_d = []
    R_d = []
    # Interpolation for mu
    # Double the vector
    for j in range(0, len(N)):
        for ele in cp_mu:
            mu_d.append(ele)
            mu_d.append(ele)
        mu_d_av = np.array(mu_d)
        # First Average
        for i in range(1,len(mu_d)):
            mu_d_av[i] = (mu_d[i]+mu_d[i-1])/2
        mu_d_av2 = np.array(mu_d_av)
        # Second Average
        for i in range(1,len(mu_d_av)):
            mu_d_av2[i] = (mu_d_av[i]+mu_d_av[i-1])/2
        cp_mu = mu_d_av2[-N[j]:]
        mu_d = []
        
        # Interpolation for R

        for ele in cp_R:
            R_d.append(ele)
            R_d.append(ele)
        R_d_av = np.array(R_d)
        # First Average
        for i in range(1,len(R_d)):
            R_d_av[i] = (R_d[i]+R_d[i-1])/2
        R_d_av2 = np.array(R_d_av)
        # Second Average
        for i in range(1,len(R_d_av)):
            R_d_av2[i] = (R_d_av[i]+R_d_av[i-1])/2
        cp_R = R_d_av2[-N[j]:]
        R_d = []

    mu = np.exp(cp_mu)
    R = np.exp(cp_R)
    return [mu,R]



