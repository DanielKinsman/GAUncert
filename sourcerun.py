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

import os
import platform
import subprocess
import tempfile
import shutil
import multiprocessing
import time

SOURCE_PROJECT_DIR = 'watergrid_project'
SOURCE_PROJECT = 'Hypothetical.rsproj'

# You will need to change this dependent on your implementation of cygwin.
# Leave the '\\{0}' on the end.
CYGWIN_TEMP = 'd:\\development\\gauncert\\cygwin\\cygwin\\tmp\\{0}'

# Must list all real parameters first, before binary ones. Order is important.
# Typically these are your decision variables passed in from nsga.
SOURCE_META_PARAMETER_NAMES = ['$SRWPNorthThreshold', '$TugunDesalFullThreshold']

SOURCE_CMD = '/cygdrive/c/Program Files/eWater/Source 3.4.2.255/RiverSystem.CommandLine.exe'
SOURCE_SERVER_ADDRESS = 'net.tcp://localhost:{port}/eWater/Services/RiverSystemService'
SOURCE_SERVER_BASE_PORT = 8523

class SourceEMSRunner(object):
    def __init__(self, mpirank):
        self.rank = mpirank
        self.serverAddress = SOURCE_SERVER_ADDRESS.format(port=SOURCE_SERVER_BASE_PORT + self.rank)
        self.pool = multiprocessing.Pool(processes=1)
        self.serverReady = multiprocessing.Manager().Event()
        self.endServer = multiprocessing.Manager().Event()
        self.directory = os.path.join(tempfile.mkdtemp(), 'rank{0}'.format(self.rank))
        self.pool.apply_async(runSourceServer, [self.rank, self.directory, self.serverAddress, self.serverReady, self.endServer])

    def end(self):
        self.endServer.set()
        self.pool.close()
        self.pool.join()

    def run(self, inputDirectory, outputFile, realParams=None, binaryParams=None):
        #make sure the server is up and running
        self.serverReady.wait()

        metaParameters = makeMetaParameterDict(realParams, binaryParams)

        #copy the input set (would love to use symlinks but has to run on windows)
        for filename in os.listdir(inputDirectory):
            path = os.path.join(inputDirectory, filename)
            destination = os.path.join(self.directory, filename)
            print('copying {} to {}'.format(path, destination))
            if os.path.isdir(path):
                shutil.rmtree(path)
                shutil.copytree(path, destination)
            else:
                shutil.copyfile(path, destination)

        #run the source client program
        args = [SOURCE_CMD, '--mode', 'client', '--address', self.serverAddress, '--output', outputFile]
        if (metaParameters is not None) and len(metaParameters) > 0:
            metaParameterArgs = []
            for key in metaParameters.keys():
                metaParameterArgs.append('--value')
                metaParameterArgs.append('{}={}'.format(key, metaParameters[key]))

            args.extend(metaParameterArgs)

        #print(args)
        #todo check output file doesn't already exist

        for i in range(3): # 3 retry attempts when failures occur
            process = subprocess.Popen(args, stdin=subprocess.PIPE)
            process.wait()

            # If we succeeded, return
            if os.path.isfile(outputFile):
                return True

            time.sleep(i*5)

        print("GAUNCERT REPLICATE FAILED after 3 attempts")
        return False

def runSourceServer(rank, directory, address, readyEvent, killEvent):
    try:
        #copy the project file (and possibly non-stochastic input files) into a temp directory
        shutil.copytree(SOURCE_PROJECT_DIR, directory)
        project = os.path.join(directory, SOURCE_PROJECT)

        #uncygwin project hack
        if 'cygwin' in platform.system().lower():
            project = CYGWIN_TEMP.format('{0}\\rank{1}\\{2}'.format(os.path.split(os.path.split(directory)[0])[1], rank, SOURCE_PROJECT))

        args = [SOURCE_CMD, '--mode', 'server', '--address', address, '--project', project]
        process = subprocess.Popen(args, stdin=subprocess.PIPE)

        # Trying to pipe stdin/out/err to source ems is fucked.
        # maybe try stdout to a file and look for "The service is ready"
        # but a simple sleep will do for now. Increase it if loading
        # the project takes a long time.
        time.sleep(30)

        readyEvent.set()
        killEvent.wait()
        process.kill()
    except OSError, e:
        print(e)
    finally:
        shutil.rmtree(directory)

class CommandLineArgumentSourceMetaparametrMismatchError(Exception):
    pass

def makeMetaParameterDict(realParams, binaryParams):
    length = 0
    length += len(realParams) if realParams is not None else 0
    length += len(binaryParams) if binaryParams is not None else 0
    if length != len(SOURCE_META_PARAMETER_NAMES):
        raise CommandLineArgumentSourceMetaparametrMismatchError("GAuncert command line parameters do not match the number of metaParameters defined in 'sourcerun.py'.")

    metaParams = dict()
    index = 0

    if realParams is not None:
        for i in range(len(realParams)):
            metaParams[SOURCE_META_PARAMETER_NAMES[index]] = realParams[i]
            index += 1

    if binaryParams is not None:
        for i in range(len(binaryParams)):
            metaParams[SOURCE_META_PARAMETER_NAMES[index]] = binaryParams[i]
            index += 1

    return metaParams