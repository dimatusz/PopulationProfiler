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

from findHistBins import *
from findCellCycleBins import *
from ReadDataFromCSV import *
import csv
import math
import numpy as np
import matplotlib
matplotlib.use('qt4agg')
import matplotlib.pyplot as plt
import scipy.ndimage.filters as filters

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def get_used_wells_region(inFileName, wellLabel):
    firstRow = 999
    firstCol = 999
    lastRow = 0
    lastCol = 0
    wells = getDistinctValues(inFileName,wellLabel)
    for w in wells:
        firstRow = min(firstRow, ord(w[0])-65)
        lastRow = max(lastRow, ord(w[0])-65)
        firstCol = min(firstCol, int(w[1:]))
        lastCol = max(lastCol, int(w[1:]))
    rowOffset = firstRow
    colOffset = firstCol
    rowNo = lastRow - firstRow + 1
    colNo = lastCol - firstCol + 1
    return rowOffset, rowNo, colOffset, colNo
    
def getNegativeCtrlHist(inputFileName, CSVdrugLabels, CSVnegativeControlLabel, CSVcomparedFeature, histBinsNo, histFixedRange, LogScaleData, LogBase):
    negCtrlHist = np.zeros(histBinsNo)
    histRange = []
    bins = []
    data = []
    inputData = open(inputFileName, 'rt')
    try:
        reader = csv.DictReader(inputData) 
        
        for row in reader:
            treatment = row[CSVdrugLabels]
            if treatment in CSVnegativeControlLabel:
                cellData = row[CSVcomparedFeature]
                if cellData and is_number(cellData):  # some data might be missing
                    if(LogScaleData):
                        if cellData <= 0:
                            return "Be positive :) \nTo use logarithm scaling the data must be strictly positive (>0)."
                        data.append(math.log(float(cellData),float(LogBase))) 
                    else:
                        data.append(float(cellData))    
        # get the bins for this cell line
        if histFixedRange:
            histRange = histFixedRange
            bins = fixedRangeHistBins(histRange, histBinsNo)
        else:
            bins, histRange = findHistBins(data, histBinsNo, 0.01)
        negCtrlHist = np.histogram(data, bins)[0]
    except:
        print "Error: unable to fecth data"
        raise
    finally:
        # Close the .csv files
        inputData.close()
    
    return "", negCtrlHist, histRange, bins
    
def analyzeCSVdata(inputFileNames, outputPath, CSVdrugLabels, CSVnegativeControlLabel, CSVwellNaming, CSVcomparedFeature, histBinsNo, histFixedRange, LogScaleData, LogBase, AnalyzeCellCycle, ManualGatesAnalysis, manualGates, histBins, UseFixedCCBins):
    plt.close('all')
    outputPath = outputPath + '\\'
    shortFileNames = []
    for fn in inputFileNames:
        shortFileNames.append(fn[fn.rfind("\\")+1:-4])
    
    binsAdjustment = "_with_flexible bins"
    if(UseFixedCCBins):
        binsAdjustment = "_with_fixed_bins"  
    
    if AnalyzeCellCycle:
        offset = 1
    else:
        offset = 0
        
    inFilesNo = len(inputFileNames)
    
    gatedCountPerCellLine = []
    treatmentsPerCellLine = []
    
    fontCellCount = {'family':'serif', 'color':'darkgreen', 'weight':'normal', 'size':9}
    fontOutliersCount = {'family':'serif', 'color':'darkred', 'weight':'normal', 'size':9} 
    fontXLabels = {'family':'serif', 'color':'black', 'weight':'normal', 'size':4} 
    titleFont = {'family':'sans-serif', 'color':'darkblue', 'weight':'normal', 'size':7} 
    titleFontNC = {'family':'sans-serif', 'color':'darkred', 'weight':'normal', 'size':7}    
    
    colors = ['#D6D6C2','#FF0000','#3366FF','#009933','#FFFF99','#FF00FF','#669999','#663300','#CCFFCC','#660066']
    if AnalyzeCellCycle:
        legendLabels = ['< 2N', '2N', 'S', '4N', '> 4N']
    else:
        legendLabels = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
    
    for ifn in xrange(inFilesNo):
        rowOffset, rowNo, colOffset, colNo = get_used_wells_region(inputFileNames[ifn],CSVwellNaming)
        smoothedHistData = np.zeros((rowNo, colNo, histBinsNo))
        histData = np.zeros((rowNo, colNo, histBinsNo))
        wellNames = []
        treatmentNames = []
        for i in xrange(rowNo):
            wellNames.append([])     
            treatmentNames.append([])  
            for j in xrange(colNo):
                wellNames[i].append('No data')
                treatmentNames[i].append('No data')  
        histRange = []
        bins = []
        if ManualGatesAnalysis:
            bins = histBins
            histRange = histFixedRange
        negCtrlHist = np.zeros((histBinsNo))
        wellCnt = 0
    
        # open/create .csv files to store extratected data from the database
        inputData = open(inputFileNames[ifn], 'rt')
        outputDataHistograms = open(outputPath+shortFileNames[ifn]+"_"+CSVcomparedFeature+'_histograms.csv', 'wt')
        
        try:
            # create writer for the .csv file
            csvHistWriter = csv.writer(outputDataHistograms, quoting=csv.QUOTE_NONNUMERIC)
            # write the first row
            csvHistWriter.writerow(('File', 'Well', 'Treatment')+(CSVcomparedFeature,))
        
            reader = csv.DictReader(inputData) 
            wellData = []
            prevWell = ''
            prevTreatment = ''
            for row in reader:
                well = row[CSVwellNaming]
                # new well
                if well != prevWell:
                    # calculate histogram for the prvious well if it exists            
                    if prevWell:
                        # get the bins for this cell line
                        if not bins:
                            if histFixedRange:
                                histRange = histFixedRange
                                bins = fixedRangeHistBins(histRange, histBinsNo)
                            else:
                                bins, histRange = findHistBins(wellData, histBinsNo, 0.01, offset)
                        histogram = np.histogram(wellData, bins)[0]
                        thisRow = ord(prevWell[0])-65 - rowOffset
                        thisCol = int(prevWell[1:]) - colOffset
                        histData[thisRow][thisCol] = histogram
                        smoothedHistData[thisRow][thisCol] = filters.gaussian_filter1d(histogram,1.5)
                        csvHistWriter.writerow([shortFileNames[ifn], prevWell, prevTreatment]+list(histogram))
                        wellNames[thisRow][thisCol] = prevWell  
                        treatmentNames[thisRow][thisCol] = prevTreatment
                        wellCnt = wellCnt + 1
                        # sum up all negative controls                    
                        if prevTreatment in CSVnegativeControlLabel:
                            negCtrlHist = np.add(negCtrlHist, histogram)
                    # update well info
                    wellData = []
                    prevWell = well
                    prevTreatment = row[CSVdrugLabels]
         
                if row[CSVcomparedFeature] and is_number(row[CSVcomparedFeature]):  # some data might be missing
                    if(LogScaleData):
                        if row[CSVcomparedFeature] <= 0:
                            return "Be positive :) \nTo use logarithm scaling the data must be strictly positive (>0)."
                        cellData = math.log(float(row[CSVcomparedFeature]),float(LogBase))  
                    else:
                        cellData = float(row[CSVcomparedFeature])
                    wellData.append(cellData)
            # add the last well record
            thisRow = ord(prevWell[0])-65 - rowOffset
            thisCol = int(prevWell[1:]) - colOffset
            histogram = np.histogram(wellData, bins)[0]
            histData[thisRow][thisCol] = histogram
            smoothedHistData[thisRow][thisCol] = filters.gaussian_filter1d(histogram,1.5)
            csvHistWriter.writerow([shortFileNames[ifn], prevWell, prevTreatment]+list(histogram))
            if prevTreatment in CSVnegativeControlLabel:
                negCtrlHist = np.add(negCtrlHist, histogram)
            wellNames[thisRow][thisCol] = prevWell
            treatmentNames[thisRow][thisCol] = prevTreatment   
            wellCnt = wellCnt + 1
        except:
            print "Error: unable to fecth data"
            raise
        finally:
            # Close the .csv files
            inputData.close()
            outputDataHistograms.close()

        print "\nThere are " + str(wellCnt) + " wells in " + shortFileNames[ifn]
               
    #%% ---- GET the 5-bin cell cycle histograms ----------------------------------
        if(AnalyzeCellCycle):
            outputDataCellCycle = open(outputPath+shortFileNames[ifn]+"_"+CSVcomparedFeature+'_based_cell_cycle_histograms'+binsAdjustment+'.csv', 'wt')
            cellCycleHistograms = np.zeros((wellCnt,5))
            cellCycleWellNames = []
            gatedTreatments = []
            normalizedCount = [] 
            cellCycleBins = []
            peaks = []
            
            adjustmentCount = [0,0,0]
            try:
                csvCellCycleWriter = csv.writer(outputDataCellCycle, quoting=csv.QUOTE_NONNUMERIC)
                csvCellCycleWriter.writerow(['FileName','Well','Treatment','2N peak','4N peak','< 2N', '2N', 'S', '4N', '> 4N','Total','< 2N (%)', '2N (%)', 'S (%)', '4N (%)', '> 4N (%)'])
                
                smoothedCLNC = filters.gaussian_filter1d(negCtrlHist,1.5) 
                cellCycleBinsNC, peaksNC = find5bins(list(smoothedCLNC), False, list(negCtrlHist))
                
                w = 0
                for r in xrange(rowNo):
                    for c in xrange(colNo):
                        totalCnt = sum(histData[r][c])
                        if totalCnt == 0:
                            continue
                        if(UseFixedCCBins):
                            b = cellCycleBinsNC
                            p = peaksNC
                        else:
                            b,p,a = adjust5bins(list(smoothedHistData[r][c]), peaksNC, cellCycleBinsNC, False)
                            adjustmentCount[a] = adjustmentCount[a] + 1
                        cellCycleBins.append(b)
                        peaks.append(p)
                        for i in xrange(5): 
                            cellCycleHistograms[w][i] = sum(histData[r][c][cellCycleBins[w][i]:cellCycleBins[w][i+1]])
                        normalizedCount.append(np.divide(cellCycleHistograms[w],sum(cellCycleHistograms[w])))
                        cellCycleWellNames.append(wellNames[r][c])
                        gatedTreatments.append(treatmentNames[r][c])
                        csvCellCycleWriter.writerow([shortFileNames[ifn],wellNames[r][c],treatmentNames[r][c]]+[bins[peaks[w][0]],bins[peaks[w][1]]]+list(cellCycleHistograms[w][:])+[totalCnt]+[x*100 for x in normalizedCount[w]])
                        w = w + 1
                if(UseFixedCCBins):
                    print "Fixed bins based on the negative controls were used"
                else:
                    print str(adjustmentCount[0]) + " x cell cycle bins were adjusted"
                    print str(adjustmentCount[1]) + " x first peak was inconclusive (using NC bins)"
                    print str(adjustmentCount[2]) + " x second peak was inconclusive (using NC bins)"
            finally:
                # Close the .csv files
                outputDataCellCycle.close()
            
            gatedCountPerCellLine.append(normalizedCount)
            treatmentsPerCellLine.append(gatedTreatments)
 
    #%% ---- manual gating histogram analysis ---------------------------------
        if(ManualGatesAnalysis):
            outputDataManualGating = open(outputPath+shortFileNames[ifn]+"_"+CSVcomparedFeature+'_manual_gating.csv', 'wt')
            gatedHistograms = np.zeros((wellCnt,len(manualGates)+1))
            gatedWellNames = []
            gatedTreatments = []
            normalizedCount = [] 
            
            tempGates = [0]
            tempGates.extend(manualGates)
            tempGates.append(histBinsNo)
            gatesStr = []
            gatesStrPerc = []
            for g in xrange(len(manualGates)+1):
                gatesStr.append(str(g+1))
                gatesStrPerc.append(str(g+1)+' (%)')
            try:
                csvManualGatingWriter = csv.writer(outputDataManualGating, quoting=csv.QUOTE_NONNUMERIC)
                csvManualGatingWriter.writerow(['FileName','Well','Treatment']+gatesStr+['Total']+gatesStrPerc)
                
                w = 0
                for r in xrange(rowNo):
                    for c in xrange(colNo):
                        totalCnt = sum(histData[r][c])
                        if totalCnt == 0:
                            continue
                        for i in xrange(len(tempGates)-1): 
                            gatedHistograms[w][i] = sum(histData[r][c][tempGates[i]:tempGates[i+1]])
                        normalizedCount.append(np.divide(gatedHistograms[w],sum(gatedHistograms[w])))
                        gatedWellNames.append(wellNames[r][c])
                        gatedTreatments.append(treatmentNames[r][c])
                        csvManualGatingWriter.writerow([shortFileNames[ifn],wellNames[r][c],treatmentNames[r][c]]+list(gatedHistograms[w][:])+[totalCnt]+[x*100 for x in normalizedCount[w]])
                        w = w + 1
            finally:
                # Close the .csv files
                outputDataManualGating.close()
            
            gatedCountPerCellLine.append(normalizedCount)
            treatmentsPerCellLine.append(gatedTreatments)   
       
    #%% ---- PLOTTING -------------------------------------------------------------
        print "Reading data from file " + shortFileNames[ifn] + " -> DONE!"         
        print "Let's plot the data!"
    
        fig = plt.figure(figsize=(20, 12), dpi=100) 
        fig.suptitle(shortFileNames[ifn]+": "+CSVcomparedFeature+" - histogram range: ("+str(histRange[0])+", "+str(histRange[1])+")",fontsize=13)
        fig.set_facecolor('white')
        fig.subplots_adjust(hspace=.8, bottom=0.01, top=0.95, left=0.01, right=0.99) 
                        
        w = 0
        for r in xrange(rowNo):
            for c in xrange(colNo):
                ax = plt.subplot(rowNo, colNo, r*colNo+c+1)
                cellCount = np.sum(histData[r][c][:])
                outliersCount = histData[r][c][0] + histData[r][c][-1]
                if cellCount > 0: 
                    plt.ylim((0,max(histData[r][c])))
                    # plot histograms
                    plt.plot(histData[r][c][:], 'b-') 
                    plt.text(0.01, 0.9, str(int(cellCount)), horizontalalignment='left', 
                             verticalalignment='center', transform=ax.transAxes, fontdict=fontCellCount)
                    plt.text(0.99, 0.9, str(int(outliersCount)), horizontalalignment='right', 
                                 verticalalignment='center', transform=ax.transAxes, fontdict=fontOutliersCount)                
                    plt.plot(smoothedHistData[r][c], 'r-')
                    # draw division of the aggregated bins
                    if AnalyzeCellCycle:
                        xLabelPos = []
                        xLabelVal = []
                        ymax = plt.axis()[3]
                        for i in xrange(1,5):
                            plt.plot([cellCycleBins[w][i],cellCycleBins[w][i]],
                                     [0,ymax], 'k-', linewidth=0.5)
                        for i in xrange(0,5):
                            xLabelPos.append(cellCycleBins[w][i] + (cellCycleBins[w][i+1] - cellCycleBins[w][i])/1.4) # there could be /2 but 1.4 places the label a bit better
                            xLabelVal.append("{0:.2f}".format(normalizedCount[w][i]*100))
                    if ManualGatesAnalysis:
                        xLabelPos = []
                        xLabelVal = []
                        ymax = plt.axis()[3]
                        for i in xrange(len(manualGates)):
                            plt.plot([manualGates[i],manualGates[i]],
                                     [0,ymax], 'k-', linewidth=0.5)
                        for i in xrange(len(tempGates)-1):
                            xLabelPos.append(tempGates[i] + (tempGates[i+1] - tempGates[i])/1.4) # there could be /2 but 1.4 places the label a bit better
                            xLabelVal.append("{0:.2f}".format(normalizedCount[w][i]*100))
                    # mark the peaks and normalized xaxis scale
                    if(AnalyzeCellCycle):
                        plt.plot(peaks[w][0],smoothedHistData[r][c][peaks[w][0]], 'md', ms=1)
                        plt.plot(peaks[w][1],smoothedHistData[r][c][peaks[w][1]], 'cd', ms=1)
                        plt.plot([peaks[w][0],peaks[w][0]],
                                     [0,max(histData[r][c][:])*0.03], 'k-', linewidth=0.5)
                        plt.plot([peaks[w][1],peaks[w][1]],
                                     [0,max(histData[r][c][:])*0.03], 'k-', linewidth=0.5)
                        plt.text(peaks[w][0]/float(histBinsNo), 0.06, '1', horizontalalignment='center', 
                             verticalalignment='center', transform=ax.transAxes, fontdict=fontXLabels)
                        plt.text(peaks[w][1]/float(histBinsNo), 0.06, '2', horizontalalignment='center', 
                             verticalalignment='center', transform=ax.transAxes, fontdict=fontXLabels) 
                    w = w + 1
                else:
                    plt.plot(histData[r][c][:], 'w-') 
                    plt.text(0.5, 0.7, "No data", horizontalalignment='center', 
                             verticalalignment='center', transform=ax.transAxes, fontdict=fontOutliersCount)    
                    
                if treatmentNames[r][c] in CSVnegativeControlLabel:
                    plt.title("#"+wellNames[r][c]+" " +treatmentNames[r][c], fontdict=titleFontNC)
                    ax.set_xticklabels([])
                    ax.set_yticklabels([])
                    ax.tick_params(axis='both', bottom='off', top='off', left='off', right='off') 
                    for pos in ['top', 'bottom', 'left', 'right']:
                        ax.spines[pos].set_edgecolor('red')
                elif cellCount > 0:
                    plt.title("#"+wellNames[r][c]+" " +treatmentNames[r][c], fontdict=titleFont)  
                    ax.set_xticklabels([])
                    ax.set_yticklabels([])
                    ax.tick_params(axis='both', bottom='off', top='off', left='off', right='off') 
                    ax.spines['bottom'].set_edgecolor('black')
                    ax.spines['bottom'].set_linewidth(0.5)
                    for pos in ['top', 'left', 'right']:
                        ax.spines[pos].set_visible(False)
                else:
                    plt.axis('off')
                if (AnalyzeCellCycle or ManualGatesAnalysis) and cellCount > 0:
                    ax.set_xticks(xLabelPos)
                    ax.set_xticklabels(xLabelVal, rotation=-45, fontdict=fontXLabels, fontsize=3, y=0, verticalalignment='top')
            
        # display the plots on full screen
#        mng = plt.get_current_fig_manager()
#        mng.window.showMaximized()
        plt.show()
        
    #      # draw division lines
    #    l1 = plt.Line2D([0.271, 0.271], [0.045, 0.965],transform=fig.transFigure, figure=fig, color='black')
    #    l2 = plt.Line2D([0.5, 0.5], [0.045, 0.965],transform=fig.transFigure, figure=fig, color='black')
    #    l3 = plt.Line2D([0.729, 0.729], [0.045, 0.965],transform=fig.transFigure, figure=fig, color='black')
    #    fig.lines.extend([l1,l2,l3])
    #    fig.canvas.draw()  
        
        # save the plots to pdf
        fName = outputPath+shortFileNames[ifn]+"_"+CSVcomparedFeature+'_histograms'
        if(AnalyzeCellCycle):
            fName = fName + binsAdjustment
        fig.savefig(fName+'.pdf', dpi=720, bbox_inches='tight')
        fig.savefig(fName+'.png', dpi=720, bbox_inches='tight')
        #    fig.savefig(fName+'.ps', dpi=720)
            
    #%% ---- PLOT THE FIRST vs. SECOND PEAK ---------------------------------------
        if(AnalyzeCellCycle):
            fig = plt.figure()
            fig.suptitle("Cell line "+shortFileNames[ifn]+": cell count - 2N vs. 4N",fontsize=13)   
            
            negCtrlCnt = 0 
            treatedCnt = 0
            p1, p2 = [], []
            for w in xrange(wellCnt):
                if gatedTreatments[w] in CSVnegativeControlLabel: # Negative control
                    p1 = plt.plot(cellCycleHistograms[w][3], cellCycleHistograms[w][1], 'r*', ms=12)
                    negCtrlCnt = negCtrlCnt + 1
                else:
                    p2 = plt.plot(cellCycleHistograms[w][3], cellCycleHistograms[w][1], 'bo') 
                    treatedCnt = treatedCnt + 1
                    
            plt.xlabel("N4")
            plt.ylabel("N2")
            if negCtrlCnt and treatedCnt:          
                plt.legend( (p1[0], p2[0]), ('Negative control', 'Treated'), loc='best', numpoints=1 )  
            elif negCtrlCnt:
                plt.legend( (p1[0],), ('Negative control',), loc='best', numpoints=1 ) 
            elif treatedCnt:
                plt.legend( (p2[0],), ('Treated',), loc='best', numpoints=1 ) 
            # save the plots to pdf
            fName = outputPath+shortFileNames[ifn]+"_"+CSVcomparedFeature+"-based cell count - 2N vs. 4N"+binsAdjustment
            fig.savefig(fName+'.pdf', dpi=720, bbox_inches='tight')
            fig.savefig(fName+'.png', dpi=720, bbox_inches='tight')    
                
        print "Plotting " + shortFileNames[ifn] + " - DONE!"
    
    #%% ---- PLOT THE STACK CHARTS ------------------------------------------------
    if(AnalyzeCellCycle or ManualGatesAnalysis):
        if len(gatedCountPerCellLine[0]) > 100:
            # plot one cell line per figure because there are too many wells
            for ifn in xrange(inFilesNo):
                subplotsNum = 4
                wellsNum = len(gatedCountPerCellLine[0])
                if wellsNum%4 != 0:
                    if wellsNum%3 != 0:
                        subplotsNum = 3
                    elif wellsNum%5 != 0:
                        subplotsNum = 5
                    elif wellsNum%2 != 0:
                        subplotsNum = 2
                
                fig = plt.figure(figsize=(20, 12), dpi=100)
                if AnalyzeCellCycle:
                    fig.suptitle("Cell cycle subpopulations distribution - "+shortFileNames[ifn],fontsize=13)
                else:
                    fig.suptitle(CSVcomparedFeature+" subpopulations distribution - "+shortFileNames[ifn],fontsize=13)
                width = 0.98
                data = np.array(gatedCountPerCellLine)# enable accessing column of 3rd dimension
                
                for sp in xrange(subplotsNum):
                    if sp == subplotsNum-1: # last subplot -> take all that is left
                        thisSubplotData = data[ifn,sp*int(wellsNum/subplotsNum):,:]
                    else:
                        thisSubplotData = data[ifn,sp*int(wellsNum/subplotsNum):(sp+1)*int(wellsNum/subplotsNum),:]
                    nextBottom = np.cumsum(np.array(thisSubplotData), axis=1)
                    
                    N = len(thisSubplotData)
                    plt.subplot(subplotsNum, 1, sp+1)
                    ind = np.arange(N)    # the x locations for the groups
        
                    # reverse order plotting for more intuitive legend
                    for j in xrange(len(thisSubplotData[0])-1, 0, -1):
                        plt.bar(ind, thisSubplotData[:,j], width, color=colors[j], bottom=nextBottom[:,j-1], label=legendLabels[j])    
                    plt.bar(ind, thisSubplotData[:,0], width, color=colors[0], label=legendLabels[0])
                    
                    if sp == subplotsNum-1: # last subplot -> take all that is left
                        plt.xticks(ind + width/2., treatmentsPerCellLine[ifn][sp*int(wellsNum/subplotsNum):(sp+1)*int(wellsNum/subplotsNum)], rotation=90)
                    else:
                        plt.xticks(ind + width/2., treatmentsPerCellLine[ifn][sp*int(wellsNum/subplotsNum):], rotation=90)
                    plt.tick_params(axis='x', labelsize=6)    
                    
                    axes = plt.gca()
                    axes.set_ylim([0,1])
                    axes.set_xlim([0,N])
                    axes.legend(loc='center left', bbox_to_anchor=(1, 0.5))
                
                fig.subplots_adjust(hspace=.95, bottom=0.1, top=0.94, left=0.05, right=0.9) 
                # display the plots on full screen
#                mng = plt.get_current_fig_manager()
#                mng.window.showMaximized()
                plt.show()
                
                # save the plots to pdf
                if AnalyzeCellCycle:
                    appendix = "-based cell cycle cell count"+binsAdjustment
                else:
                    appendix = "_manual_gating"
                fName = outputPath+shortFileNames[ifn]+"_"+CSVcomparedFeature+appendix
                fig.savefig(fName+'.pdf', dpi=720, bbox_inches='tight')
                fig.savefig(fName+'.png', dpi=720, bbox_inches='tight') 
        else: # plot all cell lines in one figure
            maxFilePerFig = 5
            for figIdx in xrange(int(round(inFilesNo/maxFilePerFig+0.5))):
                fig = plt.figure(figsize=(20, 12), dpi=100)
                if AnalyzeCellCycle:
                    fig.suptitle("Cell cycle subpopulations distribution - "+shortFileNames[ifn],fontsize=13)
                else:
                    fig.suptitle(CSVcomparedFeature+" subpopulation distribution - "+shortFileNames[ifn],fontsize=13)
                width = 0.98
                lastFileInFigIdx = min(inFilesNo, figIdx*maxFilePerFig+maxFilePerFig)
                subpltsNo = lastFileInFigIdx-figIdx*maxFilePerFig
                for spIdx in xrange(subpltsNo):
                    ifn = spIdx + figIdx*maxFilePerFig
                    nextBottom = np.cumsum(np.array(gatedCountPerCellLine[ifn]), axis=1)
                    N = len(gatedCountPerCellLine[ifn][:])
                    
                    plt.subplot(subpltsNo, 1, spIdx+1)
                    plt.title(shortFileNames[ifn], fontsize=11)
                    ind = np.arange(N)    # the x locations for the groups
                    
                    data = np.array(gatedCountPerCellLine) # enable accessing column of 3rd dimension
                    # reverse order plotting for more intuitive legend                    
                    for j in xrange(len(data[ifn][0])-1, 0, -1):
                        plt.bar(ind, data[ifn,:,j], width, color=colors[j], bottom=nextBottom[:,j-1], label=legendLabels[j])    
                    plt.bar(ind, data[ifn,:,0], width, color=colors[0], label=legendLabels[0])
                    
                    plt.xticks(ind + width/2., treatmentsPerCellLine[ifn], rotation=90)
                    plt.tick_params(axis='x', labelsize=7)    
                    
                    axes = plt.gca()
                    axes.set_ylim([0,1])
                    axes.set_xlim([0,N])
                    axes.legend(loc='center left', bbox_to_anchor=(1, 0.5))
                
                fig.subplots_adjust(hspace=.95, bottom=0.1, top=0.94, left=0.05, right=0.9) 
                # display the plots on full screen
    #            mng = plt.get_current_fig_manager()
    #            mng.window.showMaximized()
                plt.show()
                
                # save the plots to pdf
                if AnalyzeCellCycle:
                    appendix = "-based cell cycle cell count"+binsAdjustment
                else:
                    appendix = "_manual_gating"
                if inFilesNo > 1:
                    fName = outputPath+shortFileNames[figIdx*maxFilePerFig]+"_-_"+shortFileNames[lastFileInFigIdx-1]+"___"+CSVcomparedFeature+appendix
                else:
                    fName = outputPath+shortFileNames[0]+"_"+CSVcomparedFeature+appendix
                fig.savefig(fName+'.pdf', dpi=720, bbox_inches='tight')
                fig.savefig(fName+'.png', dpi=720, bbox_inches='tight') 

    return ""
