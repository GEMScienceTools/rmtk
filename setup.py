# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
# Copyright (C) 2015-2017 GEM Foundation
#
# OpenQuake is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# OpenQuake is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with OpenQuake. If not, see <http://www.gnu.org/licenses/>.

from setuptools import setup, find_packages

url = "https://github.com/GEMScienceTools/rmtk"

README = """
Risk Modeller's Toolkit (RMTK)
The RMTK is a suite of tools developed by scientists working at the
Global Earthquake Model (GEM) Foundation. The main purpose
of the RMTK is to provide a suite of tools for the creation of seismic
risk input models and for the post-processing and visualisation of
OpenQuake risk results.
Copyright (C) 2015-2017 GEM Foundation
"""

setup(
    name='rmtk',
    version='1.0.0',
    description="""The main purpose of the RMTK is to provide a suite of tools
                 for the creation of seismic risk input models and for the
                 post-processing and visualisation of OpenQuake risk
                 results.
                """,
    long_description=README,
    url=url,
    packages=find_packages(exclude=['tests', 'tests.*']),
    install_requires=[
        # FIXME taken from the README, the list is incomplete
        'lxml',
        'numpy',
        'scipy',
        'shapely',
        'matplotlib'
    ],
    author='GEM Foundation',
    author_email='risk@globalquakemodel.org',
    maintainer='GEM Foundation',
    maintainer_email='risk@globalquakemodel.org',
    classifiers=(
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Topic :: Scientific/Engineering',
    ),
    keywords="seismic risk",
    license="AGPL3",
    platforms=["any"],
    package_data={"rmtk": [
        "README.md", "LICENSE"]},
    include_package_data=True,
    zip_safe=False,
)
