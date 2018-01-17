# -*- coding: utf-8 -*-
"""
Created on Wed Dec 13 13:16:36 2017

@author: swink019
"""

# =============================================================================
# # Visualize Raster into QGIS
# startLayer = QgsRasterLayer(raster_path, "start_state")
# startLayer.loadNamedStyle("../GameofLife_Style.qml")
# QgsMapLayerRegistry.instance().addMapLayer(startLayer)
# =============================================================================

# Load modules
from osgeo import gdal, osr
import qgis, numpy, os, time, shutil
from qgis.core import QgsMapLayerRegistry, QgsRasterLayer
import copy

# Function: Reads raster to array
def ReadRasterToArray(input_path):
    openRaster = gdal.Open(input_path)
    band = openRaster.GetRasterBand(1)
    rows = openRaster.RasterYSize
    cols = openRaster.RasterXSize
    geotransform = openRaster.GetGeoTransform()
    rasterOrigin = (geotransform[0], geotransform[3])
    pixelWidth = geotransform[1]
    pixelHeight =  geotransform[5]
    array = band.ReadAsArray(0, 0, cols, rows).astype(numpy.int)    
    return array, rows, cols, geotransform

# Function: Update games of life for a number of cycles
def UpdateGameOfLife(array, cycle_number, rows, cols):
    inBoard = copy.copy(array)
    for cycle in range(1,cycle_number + 1):
        print "Processing new state for Game of Life: Cycle", str(cycle), "out of", str(cycle_number)
        outBoard = copy.copy(inBoard)
        for i in range(0, rows): 
            for j in range(0, cols):
                sumNeighbors = 0 ## counter for neighbors
                boardValue = inBoard[j][i]
                # (2.1.1) Count Neighbours
                for k in range(i-1, i+2): 
                    for l in range(j-1, j+2):
                        ## Only count neighbours and not the cell itself
                        if (l,k) != (j,i):
                            sumNeighbors = sumNeighbors+inBoard[l%cols][k%rows]
                # (2.1.2a) Alive Cells
                if boardValue == 1:
                    ## Under-population
                    if sumNeighbors < 2:
                        outBoard[j][i] = 0
                    ## Over-crowding
                    elif sumNeighbors > 3:
                        outBoard[j][i] = 0
                # (2.1.2b) Reproduction
                elif boardValue == 0 and sumNeighbors == 3:
                    outBoard[j][i] = 1
        if numpy.array_equal(inBoard,outBoard):
            print "There is a stable state at cycle number:" + str(cycle)
            break
        inBoard = copy.copy(outBoard)
    return outBoard

# Function: Writes array to raster                
def WriteArrayToRaster(array, output_path, rows, cols, geotransform):
    driver = gdal.GetDriverByName('GTiff')
    outRaster = driver.Create(output_path,cols,rows,1,gdal.GDT_Int32)
    outRaster.SetGeoTransform(geotransform)
    outband = outRaster.GetRasterBand(1)
    outband.WriteArray(array,0,0)
    outRasterSRS = osr.SpatialReference()
    outRasterSRS.ImportFromEPSG(4326)
    outRaster.SetProjection(outRasterSRS.ExportToWkt())
    outband.FlushCache()
    outRaster.FlushCache()     
  
# Function: Start Game Of Life for a number of cycles
def GameOfLife(input_path, output_path, cycle_number = 1):
    inArray, rows, cols, geotransform = ReadRasterToArray(input_path)
    outArray = UpdateGameOfLife(inArray, cycle_number, rows, cols)
    WriteArrayToRaster(outArray, output_path, rows, cols, geotransform)


input_path = "./input/start_state.tif"    
output_path = "./output/end_state.tif"  
GameOfLife(input_path, output_path, cycle_number = 5)   





