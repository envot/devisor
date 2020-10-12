#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Python prgramm to run a measurement server
@autor: Klemens Schueppert 2015:
klemens.schueppert@uibk.ac.at
 
'''
import time
import os

class UtilityClass():

    '''
    Class of data of an measuremetn
    '''

    def __init__(self, data, folder='.', delimiter='\t', eol='\n'):
        self.eol = eol
        self.delimiter = delimiter
        self.datafolder = folder
        self.yearfolder = time.strftime("%Y")
        self.dayfolder = time.strftime("%Y-%m-%d")
        self.scanname = time.strftime("%H%M%S")
        self.folder = os.path.join(self.datafolder,self.yearfolder, self.dayfolder,self.scanname)
        self.measure(data)
        self.settings = {}
        return self.folder


    def measure(self, data):
        self.data = data
        return 'Measured.'

    def createFolder(self):
        if not os.path.isdir(os.path.join(self.datafolder, self.yearfolder , self.dayfolder)):
            os.mkdir(os.path.join(self.datafolder, self.yearfolder , self.dayfolder))
        if not os.path.isdir(self.folder):
            os.mkdir(self.folder)

    def save(self):
        self.folder = os.path.join(self.datafolder,self.yearfolder, self.dayfolder,
                self.scanname)
        self.createFolder()
        self._saveExpData()
        self._saveExpSet()
        return 'Saved data in : ' + self.folder

    def _writefile(self, filename, datastr):
        self.folder = os.path.join(self.datafolder,self.yearfolder, self.dayfolder,
                self.scanname)
        datafile = open (os.path.join(self.folder, filename), 'w')
        datafile.write(datastr)
        datafile.close()


    def _saveExpData(self):
        datastr = ''
        for i,datadict in enumerate(self.data):
            datastr += datadict['name'] + self.delimiter
        datastr += self.eol
        datalists = []
        for datadict in self.data:
            datalists.append(datadict['data'])
        for row in list(zip(*datalists)):
            datastr += self.delimiter.join(map(str, row)) + self.eol
        self._writefile('ExperimentData.txt', datastr)


    def _saveExpSet(self):
        settingstr = 'ExperimentCmd.acquisitionMode = excitation'+self.eol \
            + 'ExperimentCmd.scanSettings.dimension.1.ParamName = ' \
            + self.data[0]['name'] + self.eol + self.eol
        for i,val in enumerate(self.settings):
            settingstr += 'Parameter.' + val + ' = ' \
                + str(self.settings[val]) + self.eol
        for i,val in enumerate(self.data):
            settingstr += 'Parameter.' + val['name'] + '.unit = ' \
                + val['unit'] + self.eol
        self._writefile('ExperimentSettings.txt', settingstr)
