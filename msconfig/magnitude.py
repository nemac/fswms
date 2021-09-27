#!/usr/bin/env python

import sys

from duration import getDurationLayers, openMapfileForWriting, fileEndsWith, Template, getwkt, ewsMask

sys.path.append("../var")
try:
  from Config import *
except:
  print "Cannot find local settings file 'Config.py'.  You need to create a Config.py file that contains"
  print "settings appropriate for this copy of the FSWMS project.  You can use the file 'Config.tpl.py'"
  print "as a starting point --- make a copy of that file called 'Config.py', and edit appropriately."
  exit(-1)


def make_map():

  MAGNITUDE_0524_0914_LAYERS = getDurationLayers(
    dataDir=DURATION_BASE_DIR + '/magnitude/mag_0524_0914',
    layerTemplateName='ews_gen.layer.duration.tpl.map',
    groupName='Seasonal Summaries: Magnitude May24-Sept14',
    fileExts=['.img', '.tif'],
    maskBool=True,
    colormapfile='cmaps/DURATION_magnitude.cmap',
    layerTitleSubFromTo=['sumr(\d{4}).+$', '\g<1> Magnitude May24-Sept14'], # \g<1> refers to the first match group
    proj='+proj=laea +lat_0=45 +lon_0=-100 +x_0=0 +y_0=0 +a=6370997 +b=6370997 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs '
  )

  MAGNITUDE_0624_0921_LAYERS = getDurationLayers(
    dataDir=DURATION_BASE_DIR + '/magnitude/mag_0624_0921',
    layerTemplateName='ews_gen.layer.duration.tpl.map',
    groupName='Seasonal Summaries: Magnitude Jun24-Sept21',
    fileExts=['.img', '.tif'],
    maskBool=True,
    colormapfile='cmaps/DURATION_magnitude.cmap',
    layerTitleSubFromTo=['sumr(\d{4}).+$', '\g<1> Magnitude Jun24-Sept21'], # \g<1> refers to the first match group
    proj='+proj=laea +lat_0=45 +lon_0=-100 +x_0=0 +y_0=0 +a=6370997 +b=6370997 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs '
  )
   
  ###
  ### Create the magnitude.map file:
  ###
  template = Template("magnitude.tpl.map")
  f_new = openMapfileForWriting("magnitude.map")
  f_new.write( template.render( {
        'MAGNITUDE_0524_0914_LAYERS' : MAGNITUDE_0524_0914_LAYERS,
        'MAGNITUDE_0624_0921_LAYERS' : MAGNITUDE_0624_0921_LAYERS,
        'DATA_DIR'        : DATA_DIR,
        'SERVICE_URL'     : "%s/%s" % (SERVER_URL, "magnitude")
  } ) )
  f_new.close()


if __name__ == '__main__':
    print "Building magnitude.map..."
    make_map()

