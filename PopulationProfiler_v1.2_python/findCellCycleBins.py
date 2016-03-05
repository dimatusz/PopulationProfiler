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
   Matuszewski, D. J., Puigvert, J. C., Wählby, C.,  Sintorn, I.-M. (2015) 
   PopulationProfiler: a tool for population analysis, dimensionality reduction, 
   and visualization of image-based cell screening data. 

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

import matplotlib
matplotlib.use('qt4agg')
import matplotlib.pyplot as plt


def find5bins(smoothedData, debug=False, originalData = []):
    ignoreExtreme = 5
    firstPeakValue = max(smoothedData[ignoreExtreme:-ignoreExtreme])    
    firstPeakIdx = smoothedData.index(firstPeakValue)
    
    interval = max(2, int(round(len(smoothedData)*0.03)))
    locMinVal = firstPeakValue
    locMinCandidateVal = 0
    tryOriginalData = False
    i = 0    
    while 1:
        locMinCandidateVal = min(smoothedData[firstPeakIdx+i*interval:firstPeakIdx+(i+1)*interval])         
        if locMinCandidateVal < locMinVal:
            locMinVal = locMinCandidateVal
        else:
            break
        i += 1
        if firstPeakIdx+(i+1)*interval > len(smoothedData)-1-ignoreExtreme: # no minimum found try with original data
            tryOriginalData = True
            break
    if tryOriginalData:
        if len(originalData) != 0:
            return find5bins(originalData, debug)
        else:
            return [], []   # something went wrong
            
    locMinIdx = smoothedData[firstPeakIdx:].index(locMinVal) + firstPeakIdx
    
    secondPeakValue = max(smoothedData[locMinIdx:-ignoreExtreme])
    secondPeakIdx = smoothedData[locMinIdx:].index(secondPeakValue) + locMinIdx
    
    # 1 - 2N peak
    # 2 - 4N peak
    # Sub G1 < 0.75
    # 0.75 < 2N < 1.25    
    # 1.25 < S < 1.75
    # 1.75 < 4N < 2.5
    # > 2.5 >4N  
    firstPeakRange = int(round((secondPeakIdx - firstPeakIdx)/4))
    secondPeakRange = firstPeakRange*2
    bins = [0,max(ignoreExtreme,firstPeakIdx-firstPeakRange),min(firstPeakIdx+firstPeakRange,len(smoothedData)-ignoreExtreme),
            max(ignoreExtreme,secondPeakIdx-firstPeakRange),min(secondPeakIdx+secondPeakRange,len(smoothedData)-ignoreExtreme),len(smoothedData)]
    
    if debug:
        plt.figure()
        # plot the smoothedData
        plt.plot(smoothedData, 'b-', linewidth=5)
        
        plt.plot(firstPeakIdx, firstPeakValue, 'ro', ms=5) 
        plt.plot(secondPeakIdx, secondPeakValue, 'bo', ms=5)
        plt.plot(locMinIdx, locMinVal, 'go', ms=5)     
        
        plt.plot([bins[1],bins[1]],[0,2000], 'r-', linewidth=0.5)
        plt.plot([bins[2],bins[2]],[0,2000], 'r-', linewidth=0.5)
        
        plt.plot([bins[3],bins[3]],[0,2000], 'b-', linewidth=0.5)
        plt.plot([bins[4],bins[4]],[0,2000], 'b-', linewidth=0.5)
        
        plt.show() 
        
    return bins, [firstPeakIdx,secondPeakIdx]

# =============================================================================

def adjust5bins(data, oldPeaks, oldBins, debug=False):
    ignoreExtreme = 5
    # find first peak
    searchZone = [ignoreExtreme, oldPeaks[0]+int((oldPeaks[1]-oldPeaks[0])/2)]
    firstPeakVal = max(data[searchZone[0]:searchZone[1]])
    firstPeakIdx = data[searchZone[0]:searchZone[1]].index(firstPeakVal) + searchZone[0]
    
    # check if first peak is valid    
    minDifference = 0 #max(firstPeakVal*0.05, 5)
    distance = (oldPeaks[1]-oldPeaks[0])/4
    difference = min(firstPeakVal-data[max(0,firstPeakIdx-distance)],firstPeakVal-data[min(firstPeakIdx+distance,len(data))])
    if firstPeakIdx == searchZone[0] or firstPeakIdx == searchZone[1]-1 or minDifference > difference:
        #print "Inconclusive first peak -> using the Negative Control bins"
        return oldBins, oldPeaks, 1
    
    # find second peak
    searchZone = [firstPeakIdx+int((oldPeaks[1]-oldPeaks[0])/2), len(data)-ignoreExtreme]
    secondPeakVal = max(data[searchZone[0]:searchZone[1]])
    secondPeakIdx = data[searchZone[0]:searchZone[1]].index(secondPeakVal) + searchZone[0] 
    if secondPeakIdx == searchZone[1]:
        #print "Inconclusive second peak -> using the Negative Control bins"
        return oldBins, oldPeaks, 2
    # make sure we don't consider first peak slope as the second peak    
    while secondPeakIdx == searchZone[0]:
        searchZone[0] = searchZone[0] + 1
        if searchZone[0] >= searchZone[1]:
            #print "Inconclusive second peak -> using the Negative Control bins"
            return oldBins, oldPeaks, 2
        secondPeakVal = max(data[searchZone[0]:searchZone[1]])
        secondPeakIdx = data[searchZone[0]:searchZone[1]].index(secondPeakVal) + searchZone[0]   
        
    firstPeakRange = int(round((secondPeakIdx - firstPeakIdx)/4))
    secondPeakRange = firstPeakRange*2
    newBins = [0,max(ignoreExtreme,firstPeakIdx-firstPeakRange),min(firstPeakIdx+firstPeakRange,len(data)-ignoreExtreme),
            max(ignoreExtreme,secondPeakIdx-firstPeakRange),min(secondPeakIdx+secondPeakRange,len(data)-ignoreExtreme),len(data)]
    
    if debug:
        plt.figure()
        # plot the data
        plt.plot(data, 'b-', linewidth=5)
        # plot old peaks
        plt.plot(oldPeaks[0], data[oldPeaks[0]], 'rx', ms=5) 
        plt.plot(oldPeaks[1], data[oldPeaks[1]], 'bx', ms=5) 
        # plot new peaks
        plt.plot(firstPeakIdx, firstPeakVal, 'ro', ms=5) 
        plt.plot(secondPeakIdx, secondPeakVal, 'bo', ms=5) 
        # plot old bins
        plt.plot([oldBins[1],oldBins[1]],[0,firstPeakVal], 'k-', linewidth=0.5)
        plt.plot([oldBins[2],oldBins[2]],[0,firstPeakVal], 'k-', linewidth=0.5)
        plt.plot([oldBins[3],oldBins[3]],[0,firstPeakVal], 'k-', linewidth=0.5)
        plt.plot([oldBins[4],oldBins[4]],[0,firstPeakVal], 'k-', linewidth=0.5)
        # plot new bins
        plt.plot([newBins[1],newBins[1]],[0,firstPeakVal], 'r-', linewidth=0.5)
        plt.plot([newBins[2],newBins[2]],[0,firstPeakVal], 'r-', linewidth=0.5)
        plt.plot([newBins[3],newBins[3]],[0,firstPeakVal], 'b-', linewidth=0.5)
        plt.plot([newBins[4],newBins[4]],[0,firstPeakVal], 'b-', linewidth=0.5)
        
        plt.show() 
        
    return newBins, [firstPeakIdx,secondPeakIdx], 0
    