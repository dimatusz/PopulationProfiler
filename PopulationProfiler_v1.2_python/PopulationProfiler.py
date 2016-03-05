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

import sys
from PyQt4 import QtCore, QtGui, uic
from ReadDataFromCSV import *
from MainPlotter import *
from ManualGatesSelectionWindow import *


class MyWindow(QtGui.QMainWindow):
    def __init__(self):
        self.inputFileNames = []
        self.headers = []
        self.manualGates = [] 
        self.histBins = []
        self.histRange = []
        
        super(MyWindow, self).__init__()
        self.gui = uic.loadUi('PopulationProfiler_gui.ui', self)
        self.connectActions()
        
        self.show()
        
    def connectActions(self):
        # Connect the user interface controls to the logic
        QtCore.QObject.connect(self.gui.selectFilesButton,QtCore.SIGNAL("clicked()"), self.selectInputFiles)
        QtCore.QObject.connect(self.gui.selectOutPathButton,QtCore.SIGNAL("clicked()"), self.selectOutputPath)
        QtCore.QObject.connect(self.gui.closeButton,QtCore.SIGNAL("clicked()"), self.closingFunction)
        QtCore.QObject.connect(self.gui.clearInFilesButton,QtCore.SIGNAL("clicked()"), self.clearInputFiles)
        QtCore.QObject.connect(self.gui.treatmentFieldCBox,QtCore.SIGNAL("currentIndexChanged(int)"), self.updateTreatmentLabelsList)
        QtCore.QObject.connect(self.gui.selectManualGatesButton,QtCore.SIGNAL("clicked()"), self.selectManualGates)        
        QtCore.QObject.connect(self.gui.runButton,QtCore.SIGNAL("clicked()"), self.checkParamsAndRun)
        QtCore.QObject.connect(self.gui.noBinsSpinBox,QtCore.SIGNAL("valueChanged(int)"), self.resetManualGates)
    
    def selectInputFiles(self):
        fetchedFileNames = QtGui.QFileDialog.getOpenFileNames(self, 'Select .csv files to analyze...', filter='Data files (*.csv)')
        if fetchedFileNames:
            shortNames = []
            for fn in fetchedFileNames:
                self.inputFileNames.append(str(fn))
                shortNames.append(str(fn)[str(fn).rfind("\\")+1:])
            self.gui.csvFilesListWidget.addItems(shortNames)
            
            
            self.headers = []
            self.headers = getHeaders(str(self.inputFileNames[0]))
            self.headers.sort()
            self.headers.insert(0, "Please, select one of the below...")
            
            self.gui.label_2.setEnabled(True)
            self.gui.treatmentFieldCBox.setEnabled(True)
            self.gui.treatmentFieldCBox.clear()
            self.gui.treatmentFieldCBox.addItems(self.headers)
            self.gui.label_4.setEnabled(True)
            self.gui.groupingFieldCBox.setEnabled(True)
            self.gui.groupingFieldCBox.clear()
            self.gui.groupingFieldCBox.addItems(self.headers)
            self.gui.label_5.setEnabled(True)
            self.gui.analyzedFeatureCBox.setEnabled(True)
            self.gui.analyzedFeatureCBox.clear()
            self.gui.analyzedFeatureCBox.addItems(self.headers)
   
    def resetManualGates(self):
        self.manualGates = []
        
    def selectManualGates(self):
        # check the params
        if(not self.inputFileNames):
            self.displayErrorMessage("Missing parameter...", "Please, select input files")
            self.selectInputFiles()
            return
        if(self.gui.treatmentFieldCBox.currentIndex() < 1):
            self.displayErrorMessage("Missing parameter...", "Please, select drug name field")
            return
        if(not self.gui.negCtrlListWidget.selectedItems()):
            self.displayErrorMessage("Missing parameter...", "Please, select at least one negative control label")
            return
        if(self.gui.analyzedFeatureCBox.currentIndex() < 1):
            self.displayErrorMessage("Missing parameter...", "Please, select field with data to be analyzed")
            return
        if(self.gui.useFixedRangeCheckBox.isChecked() and self.gui.rangeFromSpinBox.value() >= self.gui.rangeToSpinBox.value()):
            self.displayErrorMessage("Wrong parameter value...", "The histogram range values are invalid.")
            return
        
        negCtrlLabels = ""
        for si in self.negCtrlListWidget.selectedItems():
            negCtrlLabels = negCtrlLabels + " " + str(si.text())
        
        histRange = []
        if (self.gui.useFixedRangeCheckBox.isChecked()):
            histRange.append(self.gui.rangeFromSpinBox.value())
            histRange.append(self.gui.rangeToSpinBox.value())
        
        status,negCtrlHistData,histRange,histBins = getNegativeCtrlHist(self.inputFileNames[0], str(self.gui.treatmentFieldCBox.currentText()), negCtrlLabels,
                                                               str(self.gui.analyzedFeatureCBox.currentText()), self.gui.noBinsSpinBox.value(), histRange,
                                                               self.gui.scaleDataCheckBox.isChecked(), self.gui.logBaseSpinBox.value())       
        if(status):
            self.displayErrorMessage("Error!", status)
        else:
            self.histBins = histBins
            self.histRange = histRange
            self.gui.rangeFromSpinBox.setValue(histRange[0])
            self.gui.rangeToSpinBox.setValue(histRange[1])
            self.manualGatesWindow = ManualGatesSelectionWindow(self.manualGates, negCtrlHistData)    
            self.manualGatesWindow.finalGates.connect(self.updateGatesList)
    
    def updateGatesList(self, gates):
        self.manualGates = [] 
        for g in gates:
            if g > 0:
                self.manualGates.append(g)
        self.manualGates.sort()        
        self.gui.manualGatesLineEdit.setText(str(self.manualGates)[1:-1])
            
    def selectOutputPath(self):
        self.outPath = QtGui.QFileDialog.getExistingDirectory(self, 'Select output directory...')
        if self.outPath:
            self.gui.outputPathLineEdit.setText(self.outPath)
            print "Output path set to: " + self.outPath
            
    def clearInputFiles(self):
        self.inputFileNames = []
        self.headers = [] 
        self.gui.csvFilesListWidget.clear()
        self.gui.label_2.setEnabled(False)
        self.gui.treatmentFieldCBox.setEnabled(False)
        self.gui.treatmentFieldCBox.clear()
        self.gui.label_3.setEnabled(False)
        self.gui.label_7.setEnabled(False)
        self.gui.negCtrlListWidget.setEnabled(False)
        self.gui.negCtrlListWidget.clear()        
        self.gui.label_4.setEnabled(False)
        self.gui.groupingFieldCBox.setEnabled(False)
        self.gui.groupingFieldCBox.clear()
        self.gui.label_5.setEnabled(False)
        self.gui.analyzedFeatureCBox.setEnabled(False)
        self.gui.analyzedFeatureCBox.clear()
        self.manualGates = [] 
        self.gui.manualGatesLineEdit.clear()
        
    def updateTreatmentLabelsList(self, idx):
        if idx > 0: 
            self.treatmentLabelsList = getDistinctValues(str(self.inputFileNames[0]),self.headers[idx])
            self.treatmentLabelsList.sort()
            self.gui.label_3.setEnabled(True)
            self.gui.label_7.setEnabled(True)
            self.gui.negCtrlListWidget.setEnabled(True)
            self.gui.negCtrlListWidget.clear() 
            self.gui.negCtrlListWidget.addItems(self.treatmentLabelsList)
    
    def displayErrorMessage(self, winTitle, message):  
        messageBox = QtGui.QMessageBox(self)
        messageBox.setText(message)
        messageBox.setWindowTitle(winTitle)
        messageBox.setIcon(QtGui.QMessageBox.Critical)
        messageBox.exec_()
    
    def checkParamsAndRun(self):
        # check the params
        if(not self.inputFileNames):
            self.displayErrorMessage("Missing parameter...", "Please, select input files")
            self.selectInputFiles()
            return
        if(self.gui.treatmentFieldCBox.currentIndex() < 1):
            self.displayErrorMessage("Missing parameter...", "Please, select drug name field")
            return
        if(self.gui.cellCycleAnalysisRadioButton.isChecked() and not self.gui.negCtrlListWidget.selectedItems()):
            self.displayErrorMessage("Missing parameter...", "Please, select at least one negative control label")
            return
        if(self.gui.groupingFieldCBox.currentIndex() < 1):
            self.displayErrorMessage("Missing parameter...", "Please, select field with well names")
            return
        if(self.gui.analyzedFeatureCBox.currentIndex() < 1):
            self.displayErrorMessage("Missing parameter...", "Please, select field with data to be analyzed")
            return
        if(not str(self.gui.outputPathLineEdit.text()) or str(self.gui.outputPathLineEdit.text()) == "Please, select output path..."):
            self.displayErrorMessage("Missing parameter...", "Please, specify the output path")
            self.selectOutputPath()
            return
        if(self.gui.useFixedRangeCheckBox.isChecked() and self.gui.rangeFromSpinBox.value() >= self.gui.rangeToSpinBox.value()):
            self.displayErrorMessage("Wrong parameter value...", "The histogram range values are invalid.")
            return
        if(self.gui.manualGatingAnalysisRadioButton.isChecked() and not self.manualGates):
            self.displayErrorMessage("Wrong parameter value...", "Please, select the manual gates")
            return
        # check the files
        for f in self.inputFileNames:
            fileHead = getHeaders(f)
            if(str(self.gui.treatmentFieldCBox.currentText()) not in fileHead):
                self.displayErrorMessage("Inconsistent input files", f[f.rfind("\\")+1:]+" does not contain field "+str(self.gui.treatmentFieldCBox.currentText()))
                return
            if(str(self.gui.groupingFieldCBox.currentText()) not in fileHead):
                self.displayErrorMessage("Inconsistent input files", f[f.rfind("\\")+1:]+" does not contain field "+str(self.gui.groupingFieldCBox.currentText()))
                return
            if(str(self.gui.analyzedFeatureCBox.currentText()) not in fileHead):
                self.displayErrorMessage("Inconsistent input files", f[f.rfind("\\")+1:]+" does not contain field "+str(self.gui.groupingFieldCBox.currentText()))
                return
        # run the analysis
        print "Input parameters OK! Running the analysis..."
        
        negCtrlLabels = ""
        for si in self.negCtrlListWidget.selectedItems():
            negCtrlLabels = negCtrlLabels + " " + str(si.text())
        
        
        if (self.gui.useFixedRangeCheckBox.isChecked()):
            self.histRange = []
            self.histRange.append(self.gui.rangeFromSpinBox.value())
            self.histRange.append(self.gui.rangeToSpinBox.value())
        
        status = analyzeCSVdata(self.inputFileNames, str(self.gui.outputPathLineEdit.text()), 
                                str(self.gui.treatmentFieldCBox.currentText()), negCtrlLabels,
                                str(self.gui.groupingFieldCBox.currentText()), str(self.gui.analyzedFeatureCBox.currentText()),
                                self.gui.noBinsSpinBox.value(), self.histRange,
                                self.gui.scaleDataCheckBox.isChecked(), self.gui.logBaseSpinBox.value(),
                                self.gui.cellCycleAnalysisRadioButton.isChecked(), 
                                self.gui.manualGatingAnalysisRadioButton.isChecked(), self.manualGates, self.histBins,
                                self.gui.fixedBinsCheckBox.isChecked())       
        if(status):
            self.displayErrorMessage("Error!", status)
        else:
            print "Analysis -> DONE!\n" 
               
    def closingFunction(self):
        plt.close('all')
        self.close()

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    window = MyWindow()
    sys.exit(app.exec_())
    