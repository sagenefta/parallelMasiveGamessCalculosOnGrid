#! /usr/bin/env python
import sys
import os
import subprocess
import shutil
import fnmatch

class localGamessCalculo(object):
    """Run Gamess with a input on local directory
    """
    
    def __init__(self, scratchDirectory, nameCommandGamess, inputFileName, numberOfCores, version):
        """
        
        Arguments:
        - `scratchDirectory`:
        - `commandRunGamess`:
        - `inputFile`:
        - `mode`:
        """
        self._nameCommandGamess = nameCommandGamess
        self._scratchDirectory = scratchDirectory
        self._commandRunGamess = None
        self._inputFileName = inputFileName
        self._outputFileName = self._inputFileName.replace('.inp', '.out')
        self._dataFileName = self._inputFileName.replace('.inp', '.dat')
        self._numberOfCores = numberOfCores
        self._version = version
        self._binaryPaths = None
        self._inputFileOnScratch = None
        self._outputFileOnScratch = None
        self._dataFileOnScratch = None

    def __getPaths__(self):
        """
        """
        self._inputFile = os.path.abspath(self._inputFileName)
        self.inputPath = os.path.dirname(self._inputFile)
        self._inputFileOnScratch = os.path.join(scratchDirectory, self._inputFileName) 
        self._outputFileOnScratch = os.path.join(scratchDirectory, self._outputFileName) 
        self._dataFileOnScratch = os.path.join(scratchDirectory, self._dataFileName) 

    def moveInputToRun(self):
        """move the input file to scratch directory, and remove old output and data
        
        Arguments:
        - `self`:
        """
        if os.path.exists(os.path.join(self.inputPath, self._outputFileName)):
            os.remove(os.path.join(self.inputPath, self._outputFileName))
        if os.path.exists(os.path.join(self.inputPath, self._dataFileName)):
            os.remove(os.path.join(self.inputPath, self._dataFileName))

    def moveResultsToHome(self):
        """
        
        Arguments:
        - `self`:
        """
        shutil.move(self._dataFileOnScratch, os.path.join(self.inputPath, self._dataFileName))

    def __loacteGamessBinary__(self):
        """loacated the games programa [rungms] to run
        
        Arguments:
        - `self`:
        - `binPaths`:
        """
        
        basicPath = '/opt/gamess'
        try:
            self._binaryPaths = [basicPath] + os.environ['PATH'].split(':')
            for path in self._binaryPaths:
                for binFiles in os.listdir(path):
                    if fnmatch.fnmatchcase(self._nameCommandGamess, binFile):
                        self._commandRunGamess = os.path.join(path, self._nameCommandGamess)
                        break
                if self._commandRunGamess != None:
                    break
        except:
            self._commandRunGamess = os.path.join(basicPath, self._nameCommandGamess)
            if not os.path.exists(self._commandRunGamess):
               print 'ERROR!!! Gamess binary don\'t found'

    def runGAMESS_US(self):
        """
        
        Arguments:
        - `NameInputFile`:
        """
        outputFile = os.path.join(self.inputPath, self._outputFileName)
        ofile = open(outputFile, 'w')
        calculo = subprocess.Popen([self._commandRunGamess, self._inputFileName, str(self._version)], \
                                       stdout=ofile)
        calculo.wait()
           
    
if __name__ == '__main__':
    try:
        inputFileName = sys.argv[1]
    except:
        print('Error input file unknown')
        sys.exit(1)

    nameCommandGamess = 'rungms'
    scratchDirectory = '/scratch'
    numberOfCores = 1
    version = 11
    gamess_us_object = localGamessCalculo(scratchDirectory, nameCommandGamess, \
                                              inputFileName, numberOfCores, \
                                              version)
    gamess_us_object.__getPaths__()
    gamess_us_object.__loacteGamessBinary__()
    gamess_us_object.moveInputToRun()
    gamess_us_object.runGAMESS_US()
    gamess_us_object.moveResultsToHome()
