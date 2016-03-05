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


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

class mySliderWidget(QtGui.QWidget):
    
    valueChanged = QtCore.pyqtSignal(int)
    
    def __init__(self,maxVal,initVal):
        super(mySliderWidget, self).__init__() 
        self.maxVal = maxVal
        self.initUI(maxVal,initVal)
        
    def initUI(self,maxVal,initVal): 
        self.button = QtGui.QPushButton('On / Off', self)
        self.button.clicked.connect(self.buttonEvent)
        self.button.setMaximumWidth(65) 
        
        self.slider = QtGui.QSlider(QtCore.Qt.Horizontal, self)
        self.slider.setFocusPolicy(QtCore.Qt.NoFocus)
        self.slider.setMinimum(1)
        self.slider.setMaximum(maxVal)
        self.slider.setMinimumWidth(150)
        
        self.valDisp = QtGui.QLineEdit(self)
        self.valDisp.setMaximumWidth(40)
        
        if initVal < 1:
            self.slider.setValue(round(maxVal/2))
            self.slider.setEnabled(False)
            self.valDisp.setEnabled(False)
        else:
            self.slider.setValue(initVal)
        self.slider.valueChanged[int].connect(self.updateValDisp)
        self.valDisp.setText(str(self.slider.value()))
        self.valDisp.textChanged.connect(self.updateSliderVal)
        
        layout = QtGui.QHBoxLayout()
        layout.addWidget(self.button)
        layout.addWidget(self.slider)
        layout.addWidget(self.valDisp)
        self.setLayout(layout)
        
    def buttonEvent(self):
        if self.slider.isEnabled():
            self.slider.setEnabled(False)
            self.valDisp.setEnabled(False)
        else:
            self.slider.setEnabled(True)
            self.valDisp.setEnabled(True)
        self.valueChanged.emit(self.value())    
        
    def updateValDisp(self, v):
        self.valueChanged.emit(v)
        self.valDisp.setText(str(v))

    def updateSliderVal(self):
        v = self.valDisp.text()
        if is_number(v):
            val = int(v)
            if val > 0 and val < self.maxVal:
                self.slider.setValue(val)
            else:
                self.valDisp.setText(str(self.slider.value()))
        else:
            self.valDisp.setText(str(self.slider.value()))
        
    def value(self):
        if self.slider.isEnabled():
            return self.slider.value()
        else:
            return -1
        
        
