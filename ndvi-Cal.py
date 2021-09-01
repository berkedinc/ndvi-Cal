"""
Berke Dinç @ 2021

A simple script for calculating NDVI using GDAL. 
Despite the fact that the script fundamentally written for NDVI calculation, it can easily be transformed to calculate other Remote Sensing indices (such as NDWI) as well.

"""

# IMPORT REQUIRED PACKAGES

from osgeo import gdal
from osgeo import osr
import numpy as np
import glob

# FUNCTION DEFINITIONS

def readBands (band, path):

    x = path+'*B'+band+'*.jp2' # default; works when input is Sentinel-2 L1C data.

    # however, the code above can be easily replaced with:
                                                        # Sentinel-2 L2A data: x = path+'*B'+band+'*10m.jp2' (10m, 20m or 60m)
                                                        # Landsat-8 L1TP data: x = path+'*B'+band+'*.tif'

    image = gdal.Open(glob.glob(x)[0])
    data = np.array(image.GetRasterBand(1).ReadAsArray())
    spatialReference = image.GetProjection()
    geoTransform = image.GetGeoTransform()
    targetProjection = osr.SpatialReference(wkt=image.GetProjection())

    return data, spatialReference, geoTransform, targetProjection

def NDVI (red, nir):

    NDVI = (nir - red) / (nir + red)

    return NDVI

def array2raster (array, geoTransform, projection, filename):

    xPixels = array.shape[1]
    yPixels = array.shape[0]
    drv = gdal.GetDriverByName('Gtiff')
    dts = drv.Create (filename, xPixels, yPixels, 1, gdal.GDT_Float32, options=["COMPRESS=LZW"])
    dts.SetGeoTransform(geoTransform)
    dts.SetProjection(projection)
    dts.GetRasterBand(1).WriteArray(array)
    dts.FlushCache()

    return dts, dts.GetRasterBand(1)

# INPUT & OUTPUT

pathImagery = "path/to/folder/" # always end the path with "/", otherwise you'll get "index error".
pathOutput = "path/to/output.tif"

# 04 = Red, 08 = NIR for Sentinel-2 data. Be sure that you include "0" as well while defining the required bands below.
# 4 = Red, 5 = NIR for Landsat-8 data. DON'T include "0" while working with Landsat-8 imagery. 

red = '04' # change this to '4' while working with Landsat-8 imagery.
nir = '08' # change this to '5' while working with Landsat-8 imagery.

(bandRed, crs, geoTransform, targetProjection) = readBands (red, pathImagery)
(bandNIR, crs, geoTransform, targetProjection) = readBands (nir, pathImagery)

ndvix = NDVI(bandRed.astype(int), bandNIR.astype(int))
tifNDVI, NDVIband = array2raster(ndvix, geoTransform, crs, pathOutput)

