# -*- coding: utf-8 -*-
"""
Copyright (c) 2015, Centre for Image Analysis, and Science for Life Laboratory, 
Uppsala University. All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

3. Any scientific work resulting from the use of this software must cite the 
   original paper:
   Matuszewski, D. J., Wählby, C., Puigvert, J. C., Sintorn, I.-M. 
   PopulationProfiler: a tool for population analysis and visualization of
   image-based cell screening data. PLoS ONE. (2016) 

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
"""

# Read data from CSV
import csv

# returns headers of the csv file
def getHeaders(fileName):
    #Open the file
    inputFile = open(fileName, 'rt')
    reader = csv.reader(inputFile)
    headers = reader.next()
    inputFile.close()
    return headers   

# returns list and count of distinctive string records of a given attribute
def getDistinctValuesAndCounts(fileName,attributeName):
    #Open the file
    inputFile = open(fileName, 'rt')
    reader = csv.DictReader(inputFile)
    distinctValuesOfFirstAttribute = []
    outList = []
     # Loop through lines
    for line in reader:
        if line[attributeName] in distinctValuesOfFirstAttribute:
            i = distinctValuesOfFirstAttribute.index(line[attributeName])
            outList[i][1] += 1
        else:
            distinctValuesOfFirstAttribute.append(str(line[attributeName]))
            outList.append([line[attributeName],1])
    inputFile.close()
    return outList;   

# returns list of distinctive string records of a given attribute
def getDistinctValues(fileName,attributeName):
    #Open the file
    inputFile = open(fileName, 'rt')
    reader = csv.DictReader(inputFile)
    distinctValuesOfAttribute = []
     # Loop through lines
    for line in reader:
        if line[attributeName] not in distinctValuesOfAttribute:
            distinctValuesOfAttribute.append(str(line[attributeName]))
    inputFile.close()
    return distinctValuesOfAttribute;
    
