#!/usr/bin/env python

import re, os, sys

from util import getproj, formatproj, openMapfileForWriting, fileEndsWith, Template, getwkt, ewsMask

sys.path.append("../var")
try:
    from Config import *
except:
    print "Cannot find local settings file 'Config.py'.  You need to create a Config.py file that contains"
    print "settings appropriate for this copy of the FSWMS project.  You can use the file 'Config.tpl.py'"
    print "as a starting point --- make a copy of that file called 'Config.py', and edit appropriately."
    exit(-1)


def getDurationLayers(dataDir, layerTemplateName, groupName, fileExts, maskBool, colormapfile=None, layerTitleSubFromTo=[]):
    tifList  = []
    for tif in sorted([filename for filename in os.listdir(dataDir) if fileEndsWith(filename, fileExts) ], reverse=False):
        try:        
            tif = re.sub('^' + dataDir + '/', '', tif)
            tif_fullpath = dataDir + '/' + tif;
            proj = getproj(tif_fullpath)
            if colormapfile:
                colormapline = 'INCLUDE "%s"' % colormapfile
            else:
                colormapline   = ''
            layerTitle = tif
            for ext in fileExts:
                if layerTitle.endswith(ext):
                    layerTitle = layerTitle.rstrip(ext)
            layerName = layerTitle
            if len(layerTitleSubFromTo):
                subFrom = layerTitleSubFromTo[0]
                subTo = layerTitleSubFromTo[1]
                layerTitle = re.sub(subFrom, subTo, layerTitle)
                wmsLayerGroup = '/{}/{}'.format(groupName, layerTitle)
                tifList.append({ 
                                   'PROJVALID'       : len(proj) > 0,
                                   'PROJ'            : formatproj(proj,10),
                                   'WKT'             : getwkt(tif_fullpath),
                                   'NAME'            : layerName,
                                   'DATA'            : dataDir + '/' + tif,
                                   'TITLE'           : layerTitle,
                                   'ABSTRACT'        : layerTitle,
                                   'COLORMAPLINE'    : colormapline,
                                   'MASK'            : '',
                                   'WMS_LAYER_GROUP' : wmsLayerGroup
                                   })
                if maskBool:
                    for mask in ewsMask:
                        tifList.append({ 
                                           'PROJVALID'       : len(proj) > 0,
                                           'PROJ'            : formatproj(proj,10),
                                           'WKT'             : getwkt(tif_fullpath),
                                           'NAME'            : layerName + mask['name'],
                                           'DATA'            : dataDir + '/' + tif,
                                           'TITLE'           : layerTitle +'_' + mask['name'],
                                           'ABSTRACT'        : layerTitle + '_' + mask['name'],
                                           'COLORMAPLINE'    : colormapline,
                                           'MASK'            : 'MASK ' + mask['name'],
                                           'WMS_LAYER_GROUP' : wmsLayerGroup
                        })
        except Exception as e:
            print e
            continue

    layerTemplate = Template(layerTemplateName)
    layers = ""
    for tifdict in tifList:
        if tifdict['PROJVALID']:
            layers = layers + layerTemplate.render(tifdict)    
    return layers


def make_map():

  DURATION_12PERIOD_0624_0921_LAYERS = getDurationLayers(
    dataDir=DURATION_BASE_DIR + '/dur1yr_0624_0921',
    layerTemplateName='ews_gen.layer.duration.tpl.map',
    groupName='Seasonal Summaries: Duration Fixed 12-Period Jun24-Sep21',
    fileExts=['.img', '.tif'],
    maskBool=True,
    colormapfile='cmaps/DURATION_v2_6and12period.cmap',
    layerTitleSubFromTo=['dur\d1yr_(\d{4}).+$', '\g<1> 12-Period Jun24-Sep21'],
  )

  DURATION_6PERIOD_0508_0617_LAYERS = getDurationLayers(
    dataDir=DURATION_BASE_DIR + '/dur1yr_0508_0617',
    layerTemplateName='ews_gen.layer.duration.tpl.map',
    groupName='Seasonal Summaries: Duration Fixed 6-Period May8-Jun17',
    fileExts=['.img', '.tif'],
    maskBool=True,
    colormapfile='cmaps/DURATION_v2_6and12period.cmap',
    layerTitleSubFromTo=['dur\d1yr_(\d{4}).+$', '\g<1> 6-Period May8-Jun17'],
  )

  DURATION_6PERIOD_0624_0804_LAYERS = getDurationLayers(
    dataDir=DURATION_BASE_DIR + '/dur1yr_0624_0804',
    layerTemplateName='ews_gen.layer.duration.tpl.map',
    groupName='Seasonal Summaries: Duration Fixed 6-Period Jun24-Aug04',
    fileExts=['.img', '.tif'],
    maskBool=True,
    colormapfile='cmaps/DURATION_v2_6and12period.cmap',
    layerTitleSubFromTo=['dur\d1yr_(\d{4}).+$', '\g<1> 6-Period Jun24-Aug4'],
  )

  DURATION_6PERIOD_0812_0921_LAYERS = getDurationLayers(
    dataDir=DURATION_BASE_DIR + '/dur1yr_0812_0921',
    layerTemplateName='ews_gen.layer.duration.tpl.map',
    groupName='Seasonal Summaries: Duration Fixed 6-Period Aug12-Sep21',
    fileExts=['.img', '.tif'],
    maskBool=True,
    colormapfile='cmaps/DURATION_v2_6and12period.cmap',
    layerTitleSubFromTo=['dur\d1yr_(\d{4}).+$', '\g<1> 6-Period Aug12-Sep21'],
  )

  DURATION_LAYERS = DURATION_12PERIOD_0624_0921_LAYERS + \
        DURATION_6PERIOD_0508_0617_LAYERS + \
        DURATION_6PERIOD_0624_0804_LAYERS + \
        DURATION_6PERIOD_0812_0921_LAYERS

  ###
  ### Create the duration.map file:
  ###
  template = Template("duration.tpl.map")
  f_new = openMapfileForWriting("duration.map")
  f_new.write( template.render( {
        'DURATION_LAYERS' : DURATION_LAYERS,
              'DATA_DIR'        : DATA_DIR,
              'SERVICE_URL'     : "%s/%s" % (SERVER_URL, "duration")
              } ) )
  f_new.close()


if __name__ == '__main__':
    print "Building duration.map..."
    make_map()
