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

import csv
import numpy
import os

def calculateObjectivesAndConstraints(results):
    objectives = []
    constraints = []

    # Edit this section to calculate your own objective functions
    # and constraints. Note that their order is important - it must
    # be the same order used by NSGA.
    #
    # At this point results should be a list (one for each replicate) of dicts in the following format:
    #     {
    #        'csv column 1' : [ '2009-01-01', '2009-01-02', '2009-01-03', ... ]
    #        'csv column 2' : [ 47.3, 98.3, 839.38, ... ]
    #     }
	#
	# NSGA considers constraints violated if they are less than zero
    # ------------------------------------------------------------------------

    obj1 = []
    obj2 = []
    #constraint1 = []

    for replicate in results:
        lastOne = len(replicate['$SystemStorageNegation']) - 1
        obj1.append(replicate['$SystemStorageNegation'][lastOne])
        lastOne = len(replicate['$TotalCost']) - 1
        obj2.append(replicate['$TotalCost'][lastOne])
        #constraint1.append(4037.2 - numpy.median(replicate['$TotalCost']))
        
    obj1 = numpy.mean(obj1)
    obj2 = numpy.mean(obj2)
    #constraint1 = numpy.mean(constraint1)

    objectives.append(obj1)
    objectives.append(obj2)
    #constraints.append(constraint1)

    # ------------------------------------------------------------------------

    for obj in objectives:
        print('objective {}\n'.format(obj))

    for constr in constraints:
        print('constraint {}\n'.format(constr))

    return ( objectives, constraints )

def process(resultsDirectory):
    results = []
    outputFilename = os.path.join(resultsDirectory, 'ga.outputs')

    for filename in os.listdir(resultsDirectory):
        if filename == os.path.basename(outputFilename):
            continue

        results.append(processFile(os.path.join(resultsDirectory, filename)))

    outputs = calculateObjectivesAndConstraints(results)

    with open(outputFilename, 'w') as f:
        for obj in outputs[0]:
            f.write('objective {}\n'.format(obj))

        for constr in outputs[1]:
            f.write('constraint {}\n'.format(constr))

def processFile(resultsFilename):
    # Parse the csv file
    results = dict()
    with open(resultsFilename, 'rb') as csvFile:
        reader = csv.DictReader(csvFile)
        first = reader.next()

        for col in first.keys():
            results[col] = [ tryFloat(first[col]) ]

        for row in reader:
            for col in row.keys():
                results[col].append( tryFloat(row[col]) )

    # When RAM becomes an issue, rather than keeping all data,
    # maybe keep only mean/median/total/std/min/max for each column.
    return results

def tryFloat(value):
    try:
        return float(value)
    except ValueError:
        return value