Risk Modeller's Toolkit (RMTK)
==============================

This is the web repository of the Risk Modeller's Toolkit (RMTK). 
The RMTK is a suite of tools developed by scientists working at the
Global Earthquake Model (GEM) Foundation. The main purpose
of the RMTK is to provide a suite of tools for the creation of seismic
fragility and vulnerability models.


### Vulnerability Tools

The toolkit contains the following functionalities for constructing 
seismic risk input models (please refer to the documentation and
tutorial for more information):

* Capacity Curve Modelling Methods:
    - ''DBELA'' method
    - ''SP-BELA'' method
    - Point Dispersion method

* MDOF → Equivalent SDOF Conversion Methods:
    - First mode approximation (Eurocode 8, 2004)
    - Adaptive approach (Casarotti and Pinho, 2007)

* Direct Nonlinear Static Methods:
    - ''R–μ–T'' relation (Dolšek and Fajfar, 2004)
    - ''SPO2IDA'' (Vamvatsikos and Cornell, 2006)
    - ''Cʀ–μ–T'' (Ruiz-García and Miranda, 2007)

* Record Based Nonlinear Static Methods:
    - Vidic and Fajfar (1994)
    - Lin and Miranda 2008
    - Miranda (2000) for firm soils
    - ''N2'' method (Eurocode 8, 2004)
    - Capacity spectrum method (FEMA, 2005)
    - ''DBELA'' method (Silva et al., 2013)

* Nonlinear Time-History Analysis of SDOF Oscillators




#### Dependencies

The main dependencies of the toolkit are the following:
* csv
* numpy
* scipy
* matplotlib

For the libraries part of the OpenQuake suite the reader can refer to:
http://github.com/gem


#### License

The Risk Modeller's Toolkit (RMTK) is free software: you can redistribute 
it and/or modify it under the terms of the GNU Affero General Public 
License as published by the Free Software Foundation, either version 
3 of the License, or (at your option) any later version.

Copyright © 2014-2017, GEM Foundation, Chiara Casotto, Anirudh Rao,
Vitor Silva, Mabé Villar.


#### Disclaimer

The software Risk Modeller's Toolkit (RMTK) provided herein 
is released as a prototype implementation on behalf of 
scientists and engineers working within the Global Earthquake Model 
(GEM) Foundation.

It is distributed for the purpose of open collaboration and in the 
hope that it will be useful to the scientific, engineering, disaster
risk and software design communities. 

The software is NOT distributed as part of GEM’s OpenQuake suite 
(http://www.globalquakemodel.org/openquake) and must be considered as a 
separate entity. The software provided herein is designed and implemented 
by scientific staff. It is not developed to the design standards, nor 
subject to same level of critical review by professional software 
developers, as GEM’s OpenQuake software suite.  

Feedback and contribution to the software is welcome, and can be 
directed to the risk scientific staff of the GEM Model Facility 
(risk@globalquakemodel.org). 

The Risk Modeller's Toolkit (RMTK) is therefore distributed WITHOUT 
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or 
FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License 
for more details.

The GEM Foundation, and the authors of the software, assume no 
liability for use of the software.
