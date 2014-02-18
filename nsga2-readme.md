Building nsga ii on cygwin
--------------------------

* Dowload cygwin setup from http://cygwin.com/setup.exe
* run setup.exe
* install the Web/wget package
* install the Devel/make package
* install the Graphics/gnuplot package (optional)
* open the cygwin terminal (cygwin.bat)
* cd to the directory where GAUncert lives
* `wget http://www.iitk.ac.in/kangal/codes/nsga2/nsga2-gnuplot-v1.1.6.tar.gz`
* `tar -xzvf nsga2-gnuplot-v1.1.6.tar.gz`
* `mv nsga2-gnuplot-v1.1.6 nsga2-gnuplot`
* `mv problemdef.c nsga2-gnuplot`
* `cd nsga2-gnuplot`
* `make`
* `cd ..`
* `ln -s nsga2-gnuplot/nsga2r.exe nsga2r`

Running nsga ii in combination with GAUncert
--------------------------------------------

If you have built NSGA-II as above it will call GAUncert automatically. Simply run NSGA as follows from a cygwin prompt (after `cd`ing into the GAuncert directory):

    ./nsga2r 0.5

Choose whatever random seed you desire, in this case we have chosen 0.5. You will be prompted to enter the GA configuration. To automate this process, pipe the input of a text file to `nsga2r` as follows:

    ./nsga2r 0.5 < nsga.input

An example nsga.input file should be provided with GAUncert. Basically it should contain the answers to the prompts given by `nsga2r`, one line per answer.

For long runs it is useful to run the program in the background, and log it's output (and any errors) to a file. Here is a typical example, read more about unix shells, piping and background/foreground processes to understand exactly how it works.

    ./nsga2r 0.5 < nsga.input > run.log 2>&1

Typical defaults for NSGA-II
----------------------------

Inital random seed value 0.0-1.0, pick whatever you like.
200 population size
200 generations
0.9 probability of crossover of real variable
0.5 probablity of mutation of real variables
5.0 distribution index for crossover
10.0 distribution index for mutation
0.9 probability of crossover of binary variable
0.5 probability of mutation of binary variables
0.9 probability of crossover for integer variables
0.5 probability of crossover for integer variables