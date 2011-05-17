#! /usr/bin/env python
import time
import os
import sys
import numpy as np
import socket
import re

# Spatial Grid Generator
# In all time we have the spatial grid on memory.

class Grid :
    """Class to generate a grid object
    """
    
    def __init__( self , dimension = 1 , start = [-1] , end = [0] , \
                  numberOfPoints = [[20]] , localPoints = [[]] ) :
        """
        the numberOfPoints must be ordenated for segment, from minor
        to maximum value.
        """
        import numpy as np

        self.dimension = dimension
        self.numberOfPoints = np.array( numberOfPoints , dtype = 'float64' )
        self.localPoints = np.array( localPoints , dtype = 'float64' )
        if len( start ) == len( end )  and type(start) == type( end ) :
            self.start = np.array( start , dtype = 'float64' )
            self.end = np.array( end , dtype = 'float64' )
        else :
            sys.exit(1)

    def __sortSegments( self ) :
        """
        Sorted all segments.
        """
        import numpy as np

        if np.size(self.localPoints) > 0 :
            self.localPoints.sort( axis = 1 )
        return self.localPoints

    def __sortOneDimensionalSpaces( self ) :
        """
        Sort form minor to major all values in each dimension of space.
        """
        import numpy as np
        
        for oneDimensionSpace in self.linearSpaces :
            oneDimensionSpace.sort()

    def __sortPointsSegments( self , points ):
        """ Sort and delet repeat numbers
        """
        import numpy as np
        
        points.sort()
        tester = points[0] 
        for i in range( np.size( points ) -1 ) :
            if tester == points[i+1] :
                points = np.delete( points , i )
            else :
                tester = points[i+1]
        return points

    def buildUnidimensionalSpaces( self ) :
        """
        Build n one dimensional list
        """
        import numpy as np

        # linearSpaces, variable to contain the array with
        # arrays points on each dimenstion.
        linearSpaces = []
        for dim in range( self.dimension ) :
            # Generate array with on limits values for onedimensional spaces.
            if np.size(self.localPoints) > 0  :
                pointsSegments = np.concatenate( [ np.array([self.start[dim]]),\
                                                   self.localPoints[dim][:],\
                                                   np.array([self.end[dim]]) ] )
            else :
                pointsSegments = np.concatenate( [ np.array([self.start[dim]]),\
                                                   np.array([self.end[dim]]) ] )
            # Points that defining the unidimentional spaces.
            pointsSegments = Grid.__sortPointsSegments( self , pointsSegments )
            temporalSegment = np.array([])
            for segm in range( np.size(pointsSegments) - 1 ):
                # build the one dimensions spaces
                temporalSegment = np.concatenate([temporalSegment,\
                                                  np.linspace(pointsSegments[segm],\
                                                              pointsSegments[segm+1],\
                                                              self.numberOfPoints[dim][segm])])
                endCell = temporalSegment[-1]
                temporalSegment = temporalSegment[0:np.size(temporalSegment)-1]
            temporalSegment = np.concatenate([temporalSegment , [endCell]])
            linearSpaces.append( temporalSegment ) 
        self.linearSpaces = linearSpaces 
        return self.linearSpaces
        pdb.set_trace()

    def build( self ) :
        """
        Build a multidimensional grid.
        
        Parameters:
        -----------
        grid = 
        
        """
        import numpy as np

        Grid.buildUnidimensionalSpaces( self )
        Grid.__sortOneDimensionalSpaces( self )
        totalDimension = 1
        dimensionsList = []
        residueUp = []
        residueDown = []
        # Determining the dimension of complete spaces saving on totalDimension.
        for OneDimensionSpace in self.linearSpaces :
            dimensionsList.append(np.size(OneDimensionSpace)) 
            totalDimension = totalDimension*np.size(OneDimensionSpace)

        rpdt = totalDimension        
        rp = totalDimension
        for dim in dimensionsList :
            rp = rp / dim
            residueUp.append( rp )

        if self.dimension == 1 :
            dimensionLisReverse = dimensionsList[:]
        else:
            dimensionLisReverse = dimensionsList[:]
            dimensionLisReverse.reverse()

        for dim in dimensionLisReverse :
            rpdt = rpdt / dim
            residueDown.append( rpdt )
        residueDown.reverse()

        oneDimensionalCompleteSpace = []
        for idDim in range(self.dimension) :
            OneDimensionSpace = self.linearSpaces[idDim]
            temporalOneDimensionalCompleteSpace = []
            for j in range( residueDown[idDim] ) :
                for m in range( np.size(OneDimensionSpace) ) :
                    for i in range( residueUp[idDim] ) :                    
                        temporalOneDimensionalCompleteSpace.append(OneDimensionSpace[m])
            oneDimensionalCompleteSpace.append( temporalOneDimensionalCompleteSpace )
        self.grid = np.matrix( oneDimensionalCompleteSpace )
        return self.grid


class GamessGrid(object):
    """class that contain the coordinates whit gamess will be calculated.
    """
    
    def __init__(self, typeOfBuild, spatialGridParameters, gamessTemplateFile, controlIndexes, logggFile):
        """
        
        Arguments:
        - `typeOfBuild`: normal, spetial. if is spetial the first coordinate 
        is interiodine distance and need the first two tupes (n,k), (m,l), 
        modify 0.5 the  (n,k) value and 0.5 (m,l) value.
        - `spatialGridParameters`:
        - `gamessTemplateFile`:
        - `logggFile`:
        """
        self._typeOfBuild = typeOfBuild
        self._spatialGridParameters = spatialGridParameters
        self._gamessTemplateFile = gamessTemplateFile
        self._logggFile = logggFile
        self._controlIndexes = controlIndexes
        self._listOfGeometries = []
        self._spatialGrid = None
        self._geometryDictionary = dict()
        self._gamessTemplateFileLines = None

    def generate(self):
        """
        """
        # Read template
        templateGamessFile = open(self._gamessTemplateFile, 'r')
        linesTemplateGamessFile = templateGamessFile.readlines()
        templateGamessFile.close()
        self._gamessTemplateFileLines = linesTemplateGamessFile
        # Generate the spatial grid
        gridObject = Grid( self, dimension = spatialGridParameters[0], \
                               start = spatialGridParameters[1], \
                               end = spatialGridParameters[2], \
                               numberOfPoints = spatialGridParameters[3], \
                               localPoints = spatialGridParameters[4])
        self._spatialGrid = gridObject.built()
        # Get template geometry
        lineWhereBeginDataBlock = 0
        for inputLineTemplate in linesTemplateGamessFile:
            lineWhereBeginDataBlock = lineWhereBeginDataBlock + 1
            if re.search("\$[D-d][A-a][T-t][A-a]", inputLineTemplate):
                break
        lineWhereEndDataBlock = 0
        for inputLineTemplateNext in linesTemplateGamessFile[lineWhereBeginDataBlock:]:
            if re.search("\$[E-e][N-n][D-d]", inputLineTemplateNext):
               break
            lineWhereEndDataBlock = lineWhereEndDataBlock + 1
        geometryLinesOnTemplate = linesTemplateGamessFile[lineWhereBeginDataBlock:lineWhereEndDataBlock]
        geometryLinesOnTemplate = geometryLinesOnTemplate.split()
        geometryList = []
        for atomCoordinate in geometryLinesOnTemplate:
            geometryList.append([float(atomCoordinate[2]),float(atomCoordinate[3]),float(atomCoordinate[4])])
        finallyTemplateGeometry = np.matrix(geometryList)
        # Generate all geometries...falta terminar de ratificar
        if self._typeOfBuild == 'normal':
            for gridPoint in range(np.size(self._spatialGrid, axis=0)):
                geometryFormed = np.copy(finallyTemplateGeometry) 
                for idIndex in range(len(self._controlIndexes)):
                    geometryFormed[self._controlIndexes[idIndex][0],self._controlIndexes[idIndex][1]] = self._spatialGrid[gridPoint,idIndex]
                self._listOfGeometries.append(geometryFormed)
        elif self._typeOfBuild == 'spetial':
            for gridPoint in range(np.size(self._spatialGrid, axis=0)):
                geometryFormed = np.copy(finallyTemplateGeometry) 
                for idIndex in range(len(self._controlIndexes)-1):
                    if idIndex == 1:
                        geometryFormed[self._controlIndexes[idIndex][0],self._controlIndexes[idIndex][1]] = 0.5*self._spatialGrid[gridPoint,idIndex]
                        geometryFormed[self._controlIndexes[idIndex+1][0],self._controlIndexes[idIndex+1][1]] = -0.5*self._spatialGrid[gridPoint,idIndex]
                    else:
                        newIdIndex = idIndex + 1
                        geometryFormed[self._controlIndexes[newIdIndex][0],self._controlIndexes[newIdIndex][1]] = self._spatialGrid[gridPoint,idIndex]
                self._listOfGeometries.append(geometryFormed)
        # Generate geometry dictionari
        listOfTupleIdGeometrie = []
        for idNumber in range(len(self._listOfGeometries)):
            temporalTuple = (idNumber,self._listOfGeometries[idNumber])
            listOfTupleIdGeometrie.append(temporalTuple)
        self._geometryDictionary = dict(listOfTupleIdGeometrie)
        # Write logFile
        logFileLines = []
        for idNumber in self._geometryDictionary.keys():
            logFileLines.append('---------------------------------------')
            logFileLines.append(str(idNumber))
            for nuberOfAtom in range(np.size(self._geometryDictionary[idNumber], axis=0)):
                logFileLines.append(str(self._geometryDictionary[idNumber][numberOfAtom,0])+\
                                    "    "+str(self._geometryDictionary[idNumber][numberOfAtom,1])+\
                                    "    "+str(self._geometryDictionary[idNumber][numberOfAtom,2])+\
                                    "\n")
            logFileLines.append('---------------------------------------')
        logFileText = ""
        for line in logFileLines:
            logFileText = logFileText+line
        try:
            import zipfile
            geometryLogFileZip = zipfile.ZipFile(self._logggFile+'.zip', 'w')
            geometryLogFileZip.writestr(self._logggFile, logFileText)
            geometryLogFileZip.close()
        except:
            geometryLogFile = open(self._logggFile, 'w')
            geometryLogFile.write(logFileText)
            geometryLogFile.close()
        
    def read(self):
        """
        """
        # Read template
        templateGamessFile = open(self._gamessTemplateFile, 'r')
        linesTemplateGamessFile = templateGamessFile.readlines()
        # Read logFile
        # Asignation of geometries: build listOfGeometries
        self._listOfGeometries = None
        # FALTA POR HACER, IMPLEMENTAR LUEGO DE HABER CORRIDO UNA PRUEBA SATISFACTORIAMENTE.

        



class InputsConstructor(object):
    """Write one gamess input 
    """
    
    def __init__(self, geometry, template):
        """
        
        Arguments:
        - `geometry`: A numpy array.
        - `template`:
        """
        self._geometry = geometry
        self._template = template
        self._inputFile = None
        self._inputLines = []
        
    def baptizeInput(self):
        """Name for input Create
        """
        self._inputFile = time.strftime("%Y-%m-%d-%H-%M-%S")+\
            "-"+os.uname()[0]+"-"+os.uname()[1]+".inp"

    def generateInput(self):
        """Build the input lines on an array. 
        """
        lineWhereBeginDataBlock = 0
        for inputLineTemplate in self._template:
            lineWhereBeginDataBlock = lineWhereBeginDataBlock + 1
            if re.search("\$[D-d][A-a][T-t][A-a]", inputLineTemplate):
                break
        self._inputLines = self._template[0:lineWhereBeginDataBlock]
        for atomCoordinates in range(np.size(geometry, axis=0)):
            oldCoordinates = self._template[lineWhereBeginDataBlock+atomCoordinates]
            oldCoordinates = oldCoordinates.split()
            oldCoordinates[2] = geometry[atomCoordinates, 0]
            oldCoordinates[3] = geometry[atomCoordinates, 1]
            oldCoordinates[4] = geometry[atomCoordinates, 2]
            newCoordinates = ""
            for oldCoordinateItem in oldCoordinate:
                newCoordinates = newCoordinates+"    "+oldCoordinateItem
            self._inputLines.append(newCoordinates+" \n")
        for endsTemplateLines in self._template[lineWhereBeginDataBlock+np.size(geomtry, axis=0):]:
            self._inputLines.append(endsTemplateLines)
            
    def writeInput(self):
        """write the inputLines
        """
        if not self._inputFile:
           print("Error!!! Input name haven't be created... Bye")
           sys.exit(1)
        else:
            if not self._inputLines:
                print("Error!!! Input lines haven't be created... Bye")
                sys.exit(1)
            else:
                inputfile = open(self._inputFile, w)
                inputfile.write(self._inputLines)
                inputfile.close()

class KernelParallel(object):
    """
    """
    
    def __init__(self, dicIdGeometries, inputTemplateFile, statusFileName, potentialGridFile, numberOfCalculosForNone):
        """
        
        Arguments:
        - `dicIdGeometries`:
        - `inputTemplateFile`:
        - `statusFileName`:
        - `potentialGridFile`:
        """
        self._dicIdGeometries = dicIdGeometries
        self._inputTemplateFile = inputTemplateFile
        self._statusFileName = statusFileName
        self._potentialGridFile = potentialGridFile
        self._numberOfCalculosForNone = numberOfCalculosForNone
        self._dictIdStatus = dict()

    def generateIdStatusDictionary(self):
        """
        """
        listOfTuplesIdStatus = []
        for idKey in self._dicIdGeometries.keys():
            listOfTuplesIdStatus.append((idKey, 'waiting'))
        self._dictIdStatus = dict(listOfTuplesIdStatus)
        # Write log file
        self._writeIdstatus()

    def _writeIdstatus(self):
        """
        """
        # Write id-status initial file
        logStatusText = ""
        for idKey in self._dictIdStatus.keys():
            logStatusText = logStatusText + str(idKey) + "=>" + \
                            str(self._dictIdStatus[idKey]) + \
                            "\n" + "----------------------\n"
        logStatusFile = open(self._statusFileName, 'w')
        logStatusFile.write(logStatusText)
        logStatusFile.close()

    def getWorkPackage(self):
        """
        """
        packageOfWork = []
        state = 'completed'
        for idKey in self._dicIdGeometries.keys():
            if len(packageOfWork) <= self._numberOfCalculosForNone:
                state = self._dictIdStatus[idKey]
                if state == 'waiting':
                    packageOfWork.append((idKey,self._dicIdGeometries[idKey]))
            else:
                break
        dicPackageOfWork = dict(packageOfWork)
        return dicPackageOfWork

    def writeInputsPackage(self, dicPackageOfGeometryToWork, listInputTemplate):
        """write inputs for calculate the package of calculos
        """
        listIdNameInputFile = []
        for idKey in dicPackageOfGeometryToWork.keys():
            inputToBuild = InputsConstructor(geometry=dicPackageOfGeometryToWork[idKey], template=listInputTemplate)
            inputToBuild.baptizeInput()
            inputToBuild.generateInput()
            inputToBuild.writeInput()
            listIdNameInputFile.append((idKey,inputToBuild._inputFile))
        dicIdNameInputFile = dict(listIdNameInputFile)
        return dicIdNameInputFile

    def generateFileForServer(self, serverIdentificator, dictionaryOfIdInputsFileToWork):
        """
        
        Arguments:
        - `dictionaryOfIdInputFile`:
        - `serverIdentificator`:
        """
        nameOfFileForServer = serverIdentificator+time.strftime("%Y.%m.%d.%H.%M.%S")+".works"
        workToProcess = ""
        for idKey in dictionaryOfIdInputFile.keys():
            workToProcess = workToProcess + str(idKey)+" "+dictionaryOfIdInputsFileToWork[idKey]+"\n"
        fileForServer = open(nameOfFileForServer, 'w')
        fileForServer.write(workToProcess)
        fileForServer.close()
        return nameOfFileForServer

    def actualizeIdStatusDictionary(self, newsIdStatusDict):
        """
        
        Arguments:
        - `newsIdStatus`:
        """
        self._dictIdStatus = newsIdStatusDict
        # Write log file
        self._writeIdstatus()

    def generatePotentialSurfaceFile(self):
        """
        """
        titleLine = '# Potential Surface Built By Parallel Massive Gamess Process\n'
        potentialSurfaceFile = open(self._potentialGridFile, 'w')
        potentialSurfaceFile.write(titleLine)
        potentialSurfaceFile.close()

    def actualizePotentialSurfaceFile(self, nameOfPotentialGridSection ):
        """Actualize the file that contain values of potential asociates to 
        spatial grid
        
        Arguments:
        - `self`:
        - `nameOfPotentialGrid`:
        """
        # Read the log file generate by server machine.
        newPotentialSurfaceSectionFile = open(nameOfPotentialGridSection, 'r')
        linesNewPotentialSurfaceSectionFile = newPotentialSurfaceSectionFile.readlines()
        newPotentialSurfaceSectionFile.close()
        # Append new points to total grid.
        linesToAppendToTotalGrid = ""
        for potentialLine in linesNewPotentialSurfaceSectionFile:
            listOfPotentialLine = potentialLine.split()
            if listOfPotentialLine[2] == 'NORMALLY':
                linesToAppendToTotalGrid = linesToAppendToTotalGrid + \
                    listOfPotentialLine[0] + ' ' + listOfPotentialLine[1] + '\n'
        # Writen new points on total potential grid.
        potentialSurfaceFile = open(self._potentialGridFile, 'a')
        potentialSurfaceFile.write(linesToAppendToTotalGrid)
        potentialSurfaceFile.close

    def orderPotentialSurfaceFile(self):
        """
        
        Arguments:
        - `self`:
        """
        # Reading actual grid
        potentialSurfaceFile = open(self._potentialGridFile, 'r')
        linesOnPotentialSurfaceFile = potentialSurfaceFile.readlines()
        linesOnPotentialSurfaceFile = linesOnPotentialSurfaceFile[1:]
        potentialSurfaceFile.close 
        # Order order...
        listOfIdEnergy = []
        for words in linesOnPotentialSurfaceFile:
            listOfIdEnergy.append(int(words.split()[0]),words.split()[1])
        dicIdenergy = dict(listOfIdEnergy)
        # Write order grid
        orderedIdEnergyText = '# Potential Surface Built By Parallel Massive Gamess Process\n'
        for idKey in dicIdenergy.keys():
            orderedIdEnergyText = orderedIdEnergyText + str(idKey) + ' ' + \
                str(dicIdenergy[idKey]) + '\n'


class Client_GamessProcess(object):
    """
    """
    
    def __init__(self, hostNameList):
        """
        
        Arguments:
        - `dicidGeometries`:
        - `gamessInputsTemplateLinesFormat`:
        """
        self._dicidGeometries = dict()
        self._gamessInputsTemplateLinesFormat = []
        self._hostNameList = hostNameList
        self._globalStatus = 'uncompleted'
    
    def _switchOnServers(self):
        """Switch up servers
        """
        import subprocess
        import os
        for host in self._hostNameList:
            serverScript = os.path.abspath('.')
            serverScript = serverScript + '/server_parallelMassiveGamessProcess.py'
            procesToUpServer = 'nohup python '+ serverScript
            print('Begin up server: '+ host)
            subprocess.Popen(['ssh', host, procesToUpServer])
            print('Host Server '+ host+' .... Up')


    def _calculosManagerClient(self):
        """
        """
        # Build
        self._globalStatus = 'completed'
        pass


    # Server Comunication
    # Clietn Manager
    def _closeServer(self, port=50007):
        """
        Close servers
        Arguments:
        - `host`:
        - `port`:
        """
        import socket
        finishMessage = 'False'
        for host in self._hostNameList:
            s = socket.socket()
            s.connect((host, port))
            print('Closing Server '+host)
            s.send(finishMessage)
            s.close()
            print('Host Server '+host+' .... Closed')
            
if __name__ == '__main__':
    # nameHostList = ['megara', 'itaka', 'pergamo', 'meknes', 'zion', 'delfos', 'efeso', 'tebas', 'cocodrilopolis', 'cefalu', 'pidna', 'dyme', 'knosos', 'abdera', 'anfisa', 'mykonos', 'serifos', 'skyros', 'kythnos']
    # nameHostList = ['megara', 'itaka', 'pergamo', 'meknes', 'zion', 'delfos', 'efeso', 'tebas', 'knosos', 'anfisa', 'mykonos', 'kythnos']

    # OPTIONS TO MAKE ALL CALCULOS:
    nameHostList = ['cefalu', 'cocodrilopolis']
    templateInputFile = 'gamessIHITemplate.inp'
    # RUN CLIENT SERVICES
    gamessClient = Client_GamessProcess(nameHostList)
    gamessClient._switchOnServers()
    gamessClient._calculosManagerClient()
    time.sleep(10)
    if gamessClient._globalStatus == 'completed':
        gamessClient._closeServer()
    else:
        print("WARNING!!! Problems with main client manager \n Servers haven't been shutdown")
        
