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

from PyQt4 import QtCore, QtGui
from ReadDataFromCSV import *
from MainPlotter import *
from mySliderWidget import *

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

class ManualGatesSelectionWindow(QtGui.QWidget):
    finalGates = QtCore.pyqtSignal(list)
    def __init__(self, gates,negCtrlHistData):
        super(ManualGatesSelectionWindow, self).__init__()
        self.connect(self, QtCore.SIGNAL('triggered()'), self.closeEvent)
        self.plotData = negCtrlHistData
        self.initUI(gates)
        
    def initUI(self,gates): 
        
        self.maxVal = len(self.plotData)
        
        self.setGeometry(35, 35, 600, 900)
        self.setWindowTitle('Manual gating selector')
        self.setWindowIcon(QtGui.QIcon('icon.png'))
                
        # draw the plot        
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)       
        
        # slider 0
        self.val0Disp = QtGui.QLineEdit(self)
        self.val0Disp.setMaximumWidth(40)
        
        self.slider0 = QtGui.QSlider(QtCore.Qt.Horizontal, self)
        self.slider0.setFocusPolicy(QtCore.Qt.NoFocus)
        self.slider0.setMinimum(1)
        self.slider0.setMaximum(self.maxVal)
        self.slider0.setMinimumWidth(150)
        if len(gates) < 1 or gates[0] < 1:
            self.slider0.setValue(round(self.maxVal/2))
        else:
            self.slider0.setValue(gates[0])
        self.val0Disp.setText(str(self.slider0.value()))
        self.val0Disp.textChanged.connect(self.updateSlider0)
        self.slider0.valueChanged[int].connect(self.updateVal0Disp)
        self.slider0.valueChanged[int].connect(self.updatePlot)
               
        layoutSlider0 = QtGui.QHBoxLayout()
        layoutSlider0.addSpacerItem(QtGui.QSpacerItem(80,20))
        layoutSlider0.addWidget(self.slider0)
        layoutSlider0.addWidget(self.val0Disp)
        layoutSlider0.addSpacerItem(QtGui.QSpacerItem(10,20))
        layoutSlider0.setAlignment(self.val0Disp, QtCore.Qt.AlignHCenter)
        
        # slider 1
        if len(gates) < 2:
            self.slider1 = mySliderWidget(self.maxVal,-1)        
        else:
            self.slider1 = mySliderWidget(self.maxVal,gates[1])
        QtCore.QObject.connect(self.slider1,QtCore.SIGNAL("valueChanged(int)"), self.updatePlot)
       
       # slider 2
        if len(gates) < 3:
            self.slider2 = mySliderWidget(self.maxVal,-1)        
        else:
            self.slider2 = mySliderWidget(self.maxVal,gates[2])
        QtCore.QObject.connect(self.slider2,QtCore.SIGNAL("valueChanged(int)"), self.updatePlot)
        
        # slider 3
        if len(gates) < 4:
            self.slider3 = mySliderWidget(self.maxVal,-1)        
        else:
            self.slider3 = mySliderWidget(self.maxVal,gates[3])
        QtCore.QObject.connect(self.slider3,QtCore.SIGNAL("valueChanged(int)"), self.updatePlot)
        
        # slider 4
        if len(gates) < 5:
            self.slider4 = mySliderWidget(self.maxVal,-1)        
        else:
            self.slider4 = mySliderWidget(self.maxVal,gates[4])
        QtCore.QObject.connect(self.slider4,QtCore.SIGNAL("valueChanged(int)"), self.updatePlot)
        
        # slider 5
        if len(gates) < 6:
            self.slider5 = mySliderWidget(self.maxVal,-1)        
        else:
            self.slider5 = mySliderWidget(self.maxVal,gates[5])
        QtCore.QObject.connect(self.slider5,QtCore.SIGNAL("valueChanged(int)"), self.updatePlot)
        
        # slider 6
        if len(gates) < 7:
            self.slider6 = mySliderWidget(self.maxVal,-1)        
        else:
            self.slider6 = mySliderWidget(self.maxVal,gates[6])
        QtCore.QObject.connect(self.slider6,QtCore.SIGNAL("valueChanged(int)"), self.updatePlot)
        
        # slider 7
        if len(gates) < 8:
            self.slider7 = mySliderWidget(self.maxVal,-1)        
        else:
            self.slider7 = mySliderWidget(self.maxVal,gates[7])
        QtCore.QObject.connect(self.slider7,QtCore.SIGNAL("valueChanged(int)"), self.updatePlot)
        
        # slider 8
        if len(gates) < 9:
            self.slider8 = mySliderWidget(self.maxVal,-1)        
        else:
            self.slider8 = mySliderWidget(self.maxVal,gates[8])
        QtCore.QObject.connect(self.slider8,QtCore.SIGNAL("valueChanged(int)"), self.updatePlot)
        
        
        
        self.closeButton = QtGui.QPushButton('Done', self)
        self.closeButton.clicked.connect(self.closeEvent)   
        self.closeButton.setMaximumWidth(150)
        
        self.scrollArea = QtGui.QScrollArea(self)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QtGui.QWidget()
        #self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 380, 280))
        
        slidersLayout = QtGui.QVBoxLayout(self.scrollAreaWidgetContents) 
        slidersLayout.addLayout(layoutSlider0)
        slidersLayout.addWidget(self.slider1)
        slidersLayout.addWidget(self.slider2)
        slidersLayout.addWidget(self.slider3)
        slidersLayout.addWidget(self.slider4)
        slidersLayout.addWidget(self.slider5)
        slidersLayout.addWidget(self.slider6)
        slidersLayout.addWidget(self.slider7)
        slidersLayout.addWidget(self.slider8)
        
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)        
        
        # set the layout
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.canvas)
        layout.addWidget(self.scrollArea)
        layout.addWidget(self.closeButton)
        layout.setAlignment(self.closeButton, QtCore.Qt.AlignHCenter)        
        self.setLayout(layout)    
        self.show()
        
        self.updatePlot()
        
    def closeEvent(self):
        self.finalGates.emit(self.getGates())
        self.deleteLater()

    def updateVal0Disp(self, v):
        self.val0Disp.setText(str(v))
    
    def updateSlider0(self):
        v = self.val0Disp.text()
        if is_number(v):
            val = int(v)
            if val > 0 and val < self.maxVal:
                self.slider0.setValue(val)
            else:
                self.val0Disp.setText(str(self.slider0.value()))
        else:
            self.val0Disp.setText(str(self.slider0.value()))
        
    def getGates(self):
        gates = []
        if self.slider0.isEnabled():
            gates.append(self.slider0.value())
        if self.slider1.isEnabled():
            gates.append(self.slider1.value())
        if self.slider2.isEnabled():
            gates.append(self.slider2.value())
        if self.slider3.isEnabled():
            gates.append(self.slider3.value())
        if self.slider4.isEnabled():
            gates.append(self.slider4.value())
        if self.slider5.isEnabled():
            gates.append(self.slider5.value())
        if self.slider6.isEnabled():
            gates.append(self.slider6.value())
        if self.slider7.isEnabled():
            gates.append(self.slider7.value())
        if self.slider8.isEnabled():
            gates.append(self.slider8.value())
        return gates
        
    def updatePlot(self):
        # create an axis
        ax = self.figure.add_subplot(111)
        # discards the old graph
        ax.hold(False)
        # plot data
        ax.plot(self.plotData, 'b-')
        plt.xlim((0,self.maxVal))
        #plot the gates
        ax.hold(True)
        ymax = plt.axis()[3]
        plt.plot([self.slider0.value(),self.slider0.value()],
                 [0,ymax], 'k-', linewidth=0.5)
        if self.slider1.isEnabled():
            plt.plot([self.slider1.value(),self.slider1.value()],
                     [0,ymax], 'k-', linewidth=0.5)
        if self.slider2.isEnabled():
            plt.plot([self.slider2.value(),self.slider2.value()],
                     [0,ymax], 'k-', linewidth=0.5)
        if self.slider3.isEnabled():
            plt.plot([self.slider3.value(),self.slider3.value()],
                     [0,ymax], 'k-', linewidth=0.5)
        if self.slider4.isEnabled():
            plt.plot([self.slider4.value(),self.slider4.value()],
                     [0,ymax], 'k-', linewidth=0.5)
        if self.slider5.isEnabled():
            plt.plot([self.slider5.value(),self.slider5.value()],
                     [0,ymax], 'k-', linewidth=0.5)
        if self.slider6.isEnabled():
            plt.plot([self.slider6.value(),self.slider6.value()],
                     [0,ymax], 'k-', linewidth=0.5)
        if self.slider7.isEnabled():
            plt.plot([self.slider7.value(),self.slider7.value()],
                     [0,ymax], 'k-', linewidth=0.5)
        if self.slider8.isEnabled():
            plt.plot([self.slider8.value(),self.slider8.value()],
                     [0,ymax], 'k-', linewidth=0.5)
            
        # refresh canvas
        self.canvas.draw()
