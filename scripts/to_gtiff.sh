#!/bin/bash

gdal_translate -co COMPRESS=LZW -co TILED=YES -of GTiff $1 $1.tif

gdaladdo --config GDAL_TIFF_OVR_BLOCKSIZE 128 $1.tif 2 4 8 16 32 64 128 256 512

