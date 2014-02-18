#!/usr/bin/env python

# GAUncert - Combined multi-objective optimisation and uncertainty analysis tool
# Copyright 2013 CSIRO

# This file is part of GAUncert.
# 
# GAUncert is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# GAUncert is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with GAUncert.  If not, see <http://www.gnu.org/licenses/>.

from mpi4py import MPI
import socket
import sourcerun
import argparse
import results
import os
import os.path
import shutil

# A list of directories containing the stochastic inputs to the model. Configure as required.
# e.g. INPUT_DIRECTORIES = ['stochastic_replicates/0/', 'stochastic_replicates/1/', 'stochastic_replicates/2/']
INPUT_DIRECTORIES = []
for i in range(10):
    INPUT_DIRECTORIES.append('stochastic_replicates/{}/'.format(i))

# Specify the temporary directory where outputs will be written. WARNING: this directory will be completely erased.
OUTPUT_DIRECTORY = 'output'

def main():
    args = parseArgs()
    if args.licence:
        printLicence()
        return

    printShortLicence()

    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()
    print("rank {0} on machine {1}".format(rank, socket.gethostname()))

    # Delete any existing results in the output directory
    if rank == 0:
        clearOutputDirectory(OUTPUT_DIRECTORY)

    # Wait for output directory to be cleared before we start
    comm.Barrier()

    runner = sourcerun.SourceEMSRunner(rank)
    try:
        # Spread the stochastic inputs around to each of the workers as evenly as possible.
        # Note: a client/server job queue mechanism would be much better for this, look into
        # mpi spawn.
        indices = [x-1 for x in range(1, len(INPUT_DIRECTORIES)+1) if x % size == rank]

        for index in indices:
            outputFile = '{0}/{1:03d}.csv'.format(OUTPUT_DIRECTORY, index)
            success = runner.run(INPUT_DIRECTORIES[index], outputFile, binaryParams=args.bin, realParams=args.real)

            if not success:
                print('GAUncert rank {0} on machine {1} restarting Source EMS server to recover from failed replicate run'.format(rank, socket.gethostname()))
                runner.end()
                runner = sourcerun.SourceEMSRunner(rank)
                success = runner.run(INPUT_DIRECTORIES[index], outputFile, binaryParams=args.bin, realParams=args.real)

                if not success:
                    print('GAUncert rank {0} on machine {1} skipping replicate {2} due to multiple failures'.format(rank, socket.gethostname(), index))

        # Wait till all workers have finished.
        comm.Barrier()

        # Only process the results on one worker.
        if rank == 0:
            results.process(OUTPUT_DIRECTORY)
    finally:
        runner.end()

def parseArgs():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-r', '--real', type=float, dest='real', action='append', help='Provide a real number parameter to the model (e.g. 6.759). Can be used multiple times.')
    parser.add_argument('-b', '--bin', type=int, dest='bin', action='append', help='Provide a binary parameter to the model, in the form of a decimal integer (e.g. 6 for 110). Can be used multiple times.')
    parser.add_argument('--licence', dest='licence', action='store_true', help='Show the copyright licence and warranty.')
    return parser.parse_args()

def printShortLicence():
    print("""GAUncert  Copyright (C) 2013  CSIRO
This program comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to redistribute it
under certain conditions.
""")

def printLicence():
    print("""GAUncert - Combined multioptimisation and uncertainty analysis tool
Copyright 2013 CSIRO

GAUncert is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

GAUncert is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with GAUncert.  If not, see <http://www.gnu.org/licenses/>""")

def clearOutputDirectory(directory):
    if os.path.islink(directory):
        raise Exception("Output directory can not currently be a symbolic link because I am a lazy programmer")

    if os.path.isdir(directory):
        shutil.rmtree(directory)

    os.mkdir(directory)

if __name__ == '__main__':
    main()