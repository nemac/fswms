#!/usr/bin/env python

import sys

from util import ewsMask, openMapfileForWriting, fileEndsWith, Template, getwkt
from duration import getDurationLayers

sys.path.append("../var")
try:
  from Config import *
except:
  print "Cannot find local settings file 'Config.py'.  You need to create a Config.py file that contains"
  print "settings appropriate for this copy of the FSWMS project.  You can use the file 'Config.tpl.py'"
  print "as a starting point --- make a copy of that file called 'Config.py', and edit appropriately."
  exit(-1)


def make_map():

  MAGNITUDE_LAYERS = getDurationLayers(
    dataDir=DURATION_BASE_DIR + '/magnitude',
    layerTemplateName='ews_gen.layer.duration.tpl.map',
    groupName='ForWarn Seasonal Summaries: Magnitude',
    fileExts=['.img', '.tif'],
    maskBool=True,
    colormapfile='cmaps/DURATION_magnitude.cmap',
    layerTitleSubFromTo=['magnitude(\d{4}).+$', '\g<1> Magnitude'], # \g<1> refers to the first match group
  )
   
  ###
  ### Create the magnitude.map file:
  ###
  template = Template("magnitude.tpl.map")
  f_new = openMapfileForWriting("magnitude.map")
  f_new.write( template.render( {
        'MAGNITUDE_LAYERS' : MAGNITUDE_LAYERS,
        'DATA_DIR'        : DATA_DIR,
        'SERVICE_URL'     : "%s/%s" % (SERVER_URL, "magnitude")
  } ) )
  f_new.close()


if __name__ == '__main__':
    print "Building magnitude.map..."
    make_map()

