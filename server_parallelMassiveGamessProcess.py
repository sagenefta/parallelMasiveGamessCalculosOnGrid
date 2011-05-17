#! /usr/bin/env python
# Echo server program
import socket
import sys
import os
import subprocess
import time

class Server_GamessProcess(object):
    """
    """
    
    def __init__(self, gamessProgram='pysingle_gamess.py', backgrond=True, numberOfProcessOnLine=2, typeOfEnergySearch='MP2'):
        """
        
        Arguments:
        - `gamessProgram`:
        - `backgrond`:
        - `numberOfProcessOnLine`:
        - `typeOfEnergySearch`:
        """
        self._gamessProgram = gamessProgram
        self._backgrond = backgrond
        self._numberOfProcessOnLine = numberOfProcessOnLine
        self._typeOfEnergySearch = typeOfEnergySearch
        self._dictionaryOfWorks = None
        self._nameLogFile = None
        
    def _getProcessList(self, nameOfFileWithProcess):
        """Read the file with process to run on GAMESS and
        return a dictionary with the principal identify number
        and inpurt file names.
        
        Arguments:
        - `self`:
        - `nameOfFileWithProcess`:
        """
        workFile = open(nameOfFileWithProcess, 'r')
        workFileLines = workFile.readlines()
        listOfTupleIdName = []
        for line in workFileLines:
            workFileLinesTemp = workFileLines[line].split('\n')[0]
            tupeIdName = (int(workFileLinesTemp.split(' ')[0]), \
                              workFileLinesTemp.split(' ')[1])
            listOfTupleIdName.append(tupeIdName)
        self._dictionaryOfWorks = dict(listOfTupleIdName)
        return 0

    def _extractEnergyInformation(self, outputFile, idProcess):
        """Get the energie value for a one structure.
        
        Arguments:
        - `self`:
        - `outputFile`:
        """
        if self._typeOfEnergySearch == 'MP2':
            chainToResearch = 'E\(MP2\)'
        elif self._typeOfEnergySearch == 'HF':
            chainToResearch0 = 'ENERGY COMPONENTS'
            chainToResearch = 'TOTAL ENERGY'
        else:
            raise 'E', 'Type of search not found'

        chainsOfStatus = ['NORMALLY', 'ABNORMALLY', 'UNKNOWN']
        temporalOutputFile = open(outputFile,'r')
        temporalOutputLines = temporalOutputFile.readlines()
        temporalOutputLinesCopy = temporalOutputLines.copy()
        energyComponentsLine = 0
        # search energy 
        finalEnergy = None
        temporalEnergy = 'None'
        if self._typeOfEnergySearch == 'HF':
            for oline in temporalOutputLines:
                energyComponentsLine = energyComponentsLine + 1
                if re.search(chainToResearch0, oline):
                    break
            temporalOutputLines = temporalOutputLines[energyComponentsLine:energyComponentsLine+40]
        energyComponentsLine = 0
        for oline in temporalOutputLines:
            energyComponentsLine = energyComponentsLine + 1
            if re.search(chainToResearch, oline):
                break
        temporalEnergyLine = temporalOutputLines[energyComponentsLine-1]
        finalEnergy = temporalEnergyLine.split(' ')[-1]
        # search status
        statusLine = 0
        statusGamessProcess = statusTemplate[2]
        for oline in temporalOutputLinesCopy:
            statusLine = statusLine + 1
            if re.search(statusTemplate[0], oline):
                statusGamessProcess = statusTemplate[0]
                break
            elif re.search(statusTemplate[1], oline):
                statusGamessProcess = statusTemplate[1]
                break
        # Colleting data to write
        totalInformationExtracted = str(idProcess) + ' ' + \
            str(finalEnergy) + ' ' + \
            str(statusGamessProcess)
        # Save calculo information.
        self._logGenerator(dataOfGamessWork=totalInformationExtracted)
        # Delete Gamess files
        inputFile = outputFile[:-4]+'.inp'
        dataFile = outputFile[:-4]+'.dat'
        os.remove(outputFile)
        os.remove(inputFile)
        os.remove(dataFile)

    def _logGenerator(self, dataOfGamessWork):
        """
        
        Arguments:
        - `self`:
        """
        if self._nameLogFile == None:
            self._nameLogFile = time.strftime('%Y.%m.%d.%H:%M:%S', time.localtime()) + \
                os.uname()[2]+'.log'
        logFile = open(self._nameLogFile, 'a')
        logFile.write(dataOfGamessWork+'\n')
        logFile.close()

    def _runConsecutiveGamessProcess(self):
        """Execute Gamess to calculate molecular properties
        
        Arguments:
        - `self`:
        """
        dictionaryOfActualSubproces = {}
        numberOfProcess = 0
        for idGamessWork in self._dictionaryOfWorks.keys():                 
            jump = True
            while jump:
                if numberOfProcess < self._numberOfProcessOnLine:
                    gamessSubprocess = subprocess.Popen([self._gamessProgram, self._dictionaryOfWorks[idGamessWork]])
                    # numberOfProcess = numberOfProcess + 1
                    smallDictionary = dict([(idGamessWork, gamessSubprocess)])
                    dictionaryOfActualSubproces.update(smallDictionary)
                    numberOfProcess = len(dictionaryOfActualSubproces.keys())
                else:
                    endProcess = True
                    while endProcess:
                        for idActualProcess in dictionaryOfActualSubproces.keys():
                            statusProcess = dictionaryOfActualSubproce[idActualProcess].poll()
                            if statusProcess != None:
                                # Get energy from output
                                outputGamessFile = self._dictionaryOfWorks[idActualProcess]
                                outputGamessFile = outputFile[:-4]+'.out'
                                self._extractEnergyInformation(outputFile=outputGamessFile, idProcess=idActualProcess)
                                # Build actual dictionary of process
                                dictionaryofactualsubproces.pop(idActualProcess)
                                numberOfProcess = len(dictionaryOfActualSubproces.keys())
                                endProcess = False
                                break
                    jump = False
                

    def _calculosServer(self, noPort=50007, hostName=None):
        """Who run the calculos package
        
        Arguments:
        - `self`:
        - `noPort`:
        - `hostName`:
        """
        # HOST = None               # Symbolic name meaning all available interfaces
        # PORT = 50007              # Arbitrary non-privileged port
        HOST = hostName
        PORT = noPort
        s = None
        for res in socket.getaddrinfo(HOST, PORT, socket.AF_UNSPEC,
                                      socket.SOCK_STREAM, 0, socket.AI_PASSIVE):
            af, socktype, proto, canonname, sa = res
            print res
            try:
                s = socket.socket(af, socktype, proto)
            except socket.error, msg:
                s = None
                continue
            try:
                s.bind(sa)
                s.listen(1)
            except socket.error, msg:
                s.close()
                s = None
                continue
            break
        if s is None:
            print 'could not open socket'
            sys.exit(1)
        # Acepting client petitions
        conn, addr = s.accept()
        print 'Connected by', addr
        # Remote execution 
        shutdownServer = True
        while shutdownServer:
            dataInputs = conn.recv(1024)
            if dataInputs == 'False':
                shutdownServer = False
            else:
                # Execute Gamess calculos
                self._getProcessList(nameOfFileWithProcess=dataInputs)
                self._runConsecutiveGamessProcess()
                conn.send(self._nameLogFile)
        conn.close()
        
if __name__ == '__main__':
    myGamessServer = Server_GamessProcess(gamessProgram='pysingle_gamess.py', \
                                              backgrond=True, \
                                              numberOfProcessOnLine=2, \
                                              typeOfEnergySearch='MP2')            
    myGamessServer._calculosServer(noPort=50007, hostName=None)
