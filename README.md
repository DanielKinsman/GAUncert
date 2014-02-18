GAUncert
========

Combined multi-objective optimisation and uncertainty analysis tool.

GAUncert allows you to run a computational model with many different stochastic input sets and collate the results. The model can then be optimized with a genetic algorithm to find optimal solutions, based on objectives and constraints calculated from the collated stochastic results.

GAUncert supports [eWater's Source EMS][1] water distrubtion models out of the box, but can of course be adapted for other computational models. The thousands of runs required are done in parallel using OpenMPI so  that a computing cluster can be used to reduce runtime.

This project is a quick and dirty proof of concept and is not thoroughly tested, polished, or user friendly, though it may prove useful.

[1]: http://www.ewater.com.au/products/ewater-source/

Cygwin, openmpi & mpi4py setup instructions
-------------------------------------------

* Dowload cygwin setup from http://cygwin.com/setup-x86.exe (make sure to get the 32bit version, not the 64bit version)
* run setup-x86.exe
* install the Devel/gcc package (bin)
* install the Libs/openmpi package (bin)
* install the Libs/libopenmpi package (bin)
* install the Libs/libopenmpi-devel package (bin)
* install the Net/openssh package (bin)
* install the Net/rsh package (bin)
* install the Interpreters/python package (bin)
* install the Python/python-numpy package (bin)
* install the Web/wget package (bin)
* open the cygwin terminal (cygwin.bat)
* download mpi4py, enter: `wget http://mpi4py.googlecode.com/files/mpi4py-1.3.tar.gz`
* extract the zip. enter: `tar -xzvf mpi4py-1.3.tar.gz`
* `cd mpi4py-1.3`
* `python setup.py build`
* `python setup.py install`

### Symbolic links in cygwin

Symbolic links seem to break when running off of a network drive. Never run cygwin off of a network drive, else you will have to reinstall it. Always copy it to a local folder (e.g. 'c:\temp' first).

### Fork errors when running cygwin

You may occasionally get forking errors when running gauncert under cygwin. The error messages may mention `child_info_fork::abort` and `address space needed
... is already occupied`. In this case you will have to "rebase" cygwin. Instructions on this can be found [here](http://cygwin.wikia.com/wiki/Rebaseall).

Running GAUncert
----------------

Running GAUncert by itself allows you to perform uncertainty analysis. Running it in combination with NSGA-II allows you to combine multi-objective optimisation and uncertainty analysis.

You will need to configure several variables before running GAUncert. These can be found in the python code:

* `main.py` to configure stochastic input directories and output directories
* `results.py` to configure objective function and constraint calculation
* `sourcerun.py` to configure eWater's Source EMS location and settings

The comments in those files should direct you what to change. Once you've set everything up, change directory to where these files (main.py etc) are installed, e.g

	cd /cygdrive/C/Users/yourname/GAUncert

then run `main.py`:

    python main.py

To run using 4 processors at once (via mpi), do the following:

    mpiexec -n 4 python main.py

When running on a cluster environment (i.e. through HPC Job Manager) you should not need to pass the `-n X' argument, as it should automatically use the correct number of processors to distribute the load.

To run with NSGA-II, refer to the NSGA readme (`nsga2-readme.md`).

Copyright and Licence
---------------------

Copyright 2013 CSIRO

This file is part of GAUncert.

GAUncert is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

GAUncert is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with GAUncert.  If not, see <http://www.gnu.org/licenses/>.

Contact
-------

* danielkinsman@riseup.net
* shiroma.maheepala@csiro.au
* enquiries@csiro.au
* http://www.csiro.au/Portals/Contact.aspx