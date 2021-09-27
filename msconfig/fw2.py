#! /usr/bin/python

import sys, re, os, glob, getopt, time
from util import *

#### FCAV configuration (makeviewerconfig)


WMS_LAYER_TEMPLATE = Template(string="""
  <wmsLayer
  %(SELECTED)s %(BREAK)s
  lid="%(LAYER_LID)s"
  visible="false"
  url="%(SERVER_URL)s/forwarn_compare?TRANSPARENT=true"
  srs="EPSG:3857"
  layers="%(LAYER_NAME)s"
  name="%(LAYER_TITLE)s"
  styles="default" 
  identify="true"
  legend="%(SERVER_URL)s/%(LEGEND)s"
  mask="true"
/>  
""")

inlineNoticeTemplate = Template(string="""
    <layerNotice text="%(TEXT)s" />
""")


ALL_PRODUCT_TYPES = PRODUCT_TYPES.copy()
ALL_PRODUCT_TYPES.update(LEGACY_PRODUCT_TYPES)

# Path to a product dir to extract current dates
A_PATH_TO_FW2_PRODUCTS = os.path.join(FW2_DATA_DIR, FW2_SOURCES_AS_LIST[0], 'X_LC_1YEAR')

def makeFW2CurrentLayerTitles():
  pwd = A_PATH_TO_FW2_PRODUCTS
  current_dates = getCurrentDates(pwd)
  date_ranges = map(getMonthAndDayDateRangeString, current_dates)
  date_strings = map(lambda d: datetime.datetime.strftime(d, '%Y%m%d'), current_dates)
  titles = [
  {
    'ForWarn2' : 'Current %Departure {0}'.format(date_ranges[0]),
    'ForWarn2_Sqrt': 'Current Muted Grass/Shrub',
    'Leidos': 'Current %Departure Legacy',
  },
  {
    'ForWarn2': 'Previous1 %Departure {0}'.format(date_ranges[1]),
    'ForWarn2_Sqrt': 'Previous1 Muted Grass/Shrub' ,
    'Leidos': 'Previous1 %Departure Legacy',
  },
  {
    'ForWarn2': 'Previous2 %Departure {0}'.format(date_ranges[2]),
    'ForWarn2_Sqrt': 'Previous2 Muted Grass/Shrub',
    'Leidos': 'Previous2 %Departure Legacy',
  }
  ]
  dates_dict = {}
  dates_dict[date_strings[0]] = titles[0]
  dates_dict[date_strings[1]] = titles[1]
  dates_dict[date_strings[2]] = titles[2]

  return dates_dict




def makeDatesForYear(year, start_date='01-08', cutoff=45):
  dates = []
  d = datetime.datetime.strptime(start_date+'-'+year, '%m-%d-%Y')
  while len(dates) < cutoff:
    dates.append(d)
    d = d + datetime.timedelta(days=8)
  return list(reversed(dates))


def makeLID(source, product_type, date_string, sources=SOURCES, product_types=ALL_PRODUCT_TYPES):
  return '_'.join([
  'FW',
  date_string,
  product_types[product_type],
  sources[source]
  ])


def renderWMSLayerBlock(lid, layer_name, layer_title, selected=False, lineBreak=False, server_url=SERVER_URL, template=WMS_LAYER_TEMPLATE):
  if 'PHENO_PROGRESS' in lid:
    legend = 'cmapicons/pctprogresslegend.png'
  else:
    legend = 'cmapicons/new-forwarn2-standard-legend-2.png'
  return template.render({
    'SELECTED'  : 'selected="true"' if selected is True else '',
    'LAYER_LID'   : lid,
    'LAYER_NAME'  : layer_name,
    'LAYER_TITLE' : layer_title,
    'SERVER_URL'  : server_url,
    'BREAK'     : 'break="true"' if lineBreak else '',
    'LEGEND'    : legend
  })


def layerIsSelectedByDefault(source, product_type, date_string):
  fw2_current_datestrings = getCurrentDates(A_PATH_TO_FW2_PRODUCTS, '%Y%m%d')
  most_recent_date = fw2_current_datestrings[0]
  tests = [
  most_recent_date == date_string and product_type == 'X_LC_5YEAR' and source == 'ForWarn2'
  ]
  return len(filter(lambda t: t, tests)) > 0


def makeFW2ArchiveLayerListFor(product_type, year):
  blocks = ''
  dates = dict( (year, makeDatesForYear(year)) for year in YEARS)
  for d in dates[year]:
    for src_dirname in FW2_SOURCES_AS_LIST:
      pwd = os.path.join(FW2_DATA_DIR, src_dirname, product_type)
      date_string = d.strftime('%Y%m%d')
      match = glob.glob(pwd + '/*'+date_string+'*')
      if len(match):
        lid = makeLID(src_dirname, product_type, date_string, SOURCES, ALL_PRODUCT_TYPES)
        file = match[0]
        layer_name = lid
        layer_title = date_string
        if src_dirname == 'ForWarn2_Sqrt':
          layer_title += '(Muted Grass/Shrub)'
        selected = layerIsSelectedByDefault(src_dirname, product_type, date_string)
        block = renderWMSLayerBlock(lid, layer_name, layer_title, selected)
        blocks += block
  return blocks


def makeFW2LegacyArchiveLayerListFor(product_type, year):
  blocks = ''
  src_dir = os.path.join(FW2_DATA_DIR, FW2_LEGACY_SOURCE_DIR)
  pwd = os.path.join(src_dir, product_type)
  dates = dict( (year, makeDatesForYear(year)) for year in YEARS)
  for d in dates[year]:
    date_string = d.strftime('%Y%m%d')
    match = glob.glob(pwd + '/*'+date_string+'*')
    if len(match):
      lid = makeLID(FW2_LEGACY_SOURCE_DIR, product_type, date_string, SOURCES, ALL_PRODUCT_TYPES)
      file = match[0]
      layer_name = lid
      layer_title = date_string
      selected = layerIsSelectedByDefault(FW2_LEGACY_SOURCE_DIR, product_type, date_string)
      block = renderWMSLayerBlock(lid, layer_name, layer_title, selected)
      blocks += block
  return blocks


def makeFW2CurrentLegacyLayerListFor(product_type):
  title_formats = [
  'Current %Departure {0}',
  'Previous1 %Departure {0}',
  'Previous2 %Departure {0}'
  ]
  current_dates = getCurrentDates(A_PATH_TO_FW2_PRODUCTS)
  date_ranges = map(getMonthAndDayDateRangeString, current_dates)
  blockList = ''
  pwd = os.path.join(FW2_DATA_DIR, FW2_LEGACY_SOURCE_DIR, product_type)
  fw2_current_datestrings = getCurrentDates(A_PATH_TO_FW2_PRODUCTS, '%Y%m%d')
  for i in range(0, len(fw2_current_datestrings)):
    d = fw2_current_datestrings[i]
    match = glob.glob(pwd + '/*' + d + '*')
    if len(match):
      lid = makeLID(FW2_LEGACY_SOURCE_DIR, product_type, d, SOURCES, ALL_PRODUCT_TYPES)
      file = match[0]
      layer_name = lid
      layer_title = title_formats[i].format(date_ranges[i])
      selected = layerIsSelectedByDefault(FW2_LEGACY_SOURCE_DIR, product_type, d)
      block = renderWMSLayerBlock(lid, layer_name, layer_title, selected)
      blockList += block
  return blockList


def makeFW2CurrentLayerListFor(product_type, list_type):
  how_current = [ "current", "previous1", "previous2" ]
  if list_type == "current":
    sources = FW2_SOURCES_AS_LIST
  if list_type == "current_legacy":
    sources = [ FW2_LEGACY_SOURCE_DIR ]
  blockList = ''
  fw2_current_datestrings = getCurrentDates(A_PATH_TO_FW2_PRODUCTS, '%Y%m%d')
  for i in range(0, len(fw2_current_datestrings)):
    d = fw2_current_datestrings[i]
    for i_source in range(0, len(sources)):
      source = sources[i_source]
      how_current_label = how_current[i] 
      lid = "{0}_{1}_{2}".format(SOURCES[source], ALL_PRODUCT_TYPES[product_type], how_current_label)
      if i_source == len(sources)-1 and list_type != 'current_legacy':
        blockList += makeXMLBlockForLayer(source, product_type, d, True, lid)
      else:
        blockList += makeXMLBlockForLayer(source, product_type, d, False, lid)
  return blockList


def makeXMLBlockForLayer(source, product_type, date_string, lineBreak=False, lid=''):
  pwd = os.path.join(FW2_DATA_DIR, source, product_type)
  match = glob.glob(pwd +'/*'+date_string+'*')
  FW2_CURRENT_DATES_TITLES = makeFW2CurrentLayerTitles()
  if len(match):
    if not lid:
      lid = makeLID(source, product_type, date_string)
    file = match[0]
    layer_name = lid
    layer_title = FW2_CURRENT_DATES_TITLES[date_string][source]
    selected = layerIsSelectedByDefault(source, product_type, date_string)
    block = renderWMSLayerBlock(lid, layer_name, layer_title, selected, lineBreak)
    return block
  else:
    return ''






#### Mapfile Generation (makemap)

def getFW2Layers(dataDir, product_type, layerTemplateName, fileExt, wcs, maskBool, source='', period=''):
  tifList  = []
  files = sorted([file for file in os.listdir(dataDir) if file.endswith(fileExt)], reverse=False)

  if period:
    files = list(filter(lambda x: period in x, files))

  for tif in files:
    dynaList  = []
    try:
      tif = re.sub('^' + dataDir + '/', '', tif)
      tif_fullpath = dataDir + '/' + tif;
      proj = getproj(tif_fullpath)

      if period:
        layerName = '{0}_{1}_{2}'.format(SOURCES[source], ALL_PRODUCT_TYPES[product_type], period)
      else:
        layerName = re.sub(r'^.*/', '', tif)

      if product_type == 'X_LC_PCTPROGRESS':
        colormapline = 'INCLUDE "percent_progress_color_table.cmap"'
      elif source == 'Leidos':
        colormapline = 'INCLUDE "new-forwarn2-legacy-2.cmap"'
      else:
        colormapline = 'INCLUDE "new-forwarn2-standard-2.cmap"'

      tifList.append({ 'TIF'       : tif,
               'PROJVALID'     : len(proj) > 0,
               'PROJ'      : formatproj(proj,10),
               'WKT'       : getwkt(tif_fullpath),
               'NAME'      : layerName,
               'DATA'      : dataDir + '/' + tif,
               'TITLE'       : layerName,
         'GROUPTEXT'     : 'GROUP FW_%s_layers' % layerName,
               'ABSTRACT'    : layerName,
               'COLORMAPLINE'  : colormapline,
               'MASK'      : '',
               })

      if maskBool:
        for mask in ewsMask:
          tifList.append({ 'TIF'       : tif,
                   'PROJVALID'     : len(proj) > 0,
                   'PROJ'      : formatproj(proj,10),
                   'WKT'       : getwkt(tif_fullpath),
                   'NAME'      : layerName + mask['name'],
                   'DATA'      : dataDir + '/' + tif,
                   'TITLE'       : layerName + mask['name'],
           'GROUPTEXT'     : 'GROUP FW_%s_layers' % layerName,
                   'ABSTRACT'    : layerName + mask['name'],
                   'COLORMAPLINE'  : colormapline,
                   'MASK'      : 'MASK ' + mask['name'],
                   })
      layerTemplate = Template(layerTemplateName)
      layers = ""

    except Exception as e:
      print e
      continue

  layerTemplate = Template(layerTemplateName)
  layers = ""

  for tifdict in tifList:
    if tifdict['PROJVALID']:
      layers = layers + layerTemplate.render(tifdict)  

  return layers


def makeCurrentMapfilesFor(source, product_type, fileExt='.img'):
  path = os.path.join(VIEWER_LINK_TARGET_DIR, source, product_type)
  periods = [ 'current', 'previous1', 'previous2' ]
  for period in periods:
    LAYERS = getFW2Layers(path, product_type, "ews_gen.layer.tpl.map", fileExt, "no", True, source, period)
    template = Template("ews_gen.tpl.map")
    layerName = '{0}_{1}_{2}'.format(SOURCES[source], ALL_PRODUCT_TYPES[product_type], period)
    mapfile_path = "forwarn2_maps/"+layerName+".map"
    try:
      os.remove(mapfile_path)
    except:
      pass
    f_new = open(mapfile_path, "w")
    f_new.write( template.render( {
          'DATA_DIR'        : DATA_DIR,
          'SERVICE_URL'       : "%s/%s?MAPFILE=%s" % (SERVER_URL, 'forwarn_compare', layerName),
          'LAYERS'        : LAYERS,
          'WMS_SRS'         : "EPSG:4326 EPSG:2163 EPSG:3857 EPSG:900913",
          'MAPFILE_PROJECTION'  : '"init=epsg:3857"',
          'SERVICE_NAME'      : 'forwarn_compare',
          'TEMP_FILE_PREFIX'    : "ms_%s" % (layerName),
          'MAPFILE'         : "%s/msconfig/%s.map" % (BASE_DIR, layerName),
          'OWS_TITLE'       : "NEMAC %s WMS" % (layerName),
          'OWS_ABSTRACT'      : "NEMAC %s WMS" % (layerName),
          'OWS_KEYWORDLIST'     : "mapserver,ogc,%s" % (layerName),
          'SERVICE_URL'       : "%s/%s?MAPFILE=%s" % (SERVER_URL, 'forwarn_compare', layerName),
          'MS_ERRORFILE'      : "../var/log/%s.log" % (layerName),
          'WFS_NAMESPACE_PREFIX'  : layerName, 
          'WCS_LABEL'       : layerName
          } ) )
    f_new.close()


def makeBundledMapfileFor(source, product_type, cgi_endpoint):
  print cgi_endpoint + '.map'
  groupName = SOURCES[source]+ALL_PRODUCT_TYPES[product_type]
  LAYERS = getFW2Layers(os.path.join(FW2_DATA_DIR, source, product_type), product_type, "ews_gen.layer.tpl.map", ".img", "no", True)
  template = Template("ews_gen.tpl.map")
  f_new = openMapfileForWriting('{0}.map'.format(cgi_endpoint))
  SERVICE_NAME = cgi_endpoint
  WCS_LABEL = groupName
  f_new.write( template.render( {
        'DATA_DIR'        : DATA_DIR,
        'SERVICE_URL'       : "%s/%s?MAPFILE=%s" % (SERVER_URL, SERVICE_NAME, cgi_endpoint),
        'LAYERS'        : LAYERS,
        'WMS_SRS'         : "EPSG:4326 EPSG:2163 EPSG:3857 EPSG:900913",
        'MAPFILE_PROJECTION'  : '"init=epsg:3857"',
        'SERVICE_NAME'      : SERVICE_NAME,
        'TEMP_FILE_PREFIX'    : "ms_%s" % (SERVICE_NAME),
        'MAPFILE'         : "%s/msconfig/%s.map" % (BASE_DIR, SERVICE_NAME),
        'OWS_TITLE'       : "NEMAC %s WMS" % (SERVICE_NAME),
        'OWS_ABSTRACT'      : "NEMAC %s WMS" % (SERVICE_NAME),
        'OWS_KEYWORDLIST'     : "mapserver,ogc,%s" % (SERVICE_NAME),
        'SERVICE_URL'       : "%s/%s" % (SERVER_URL, SERVICE_NAME),
        'MS_ERRORFILE'      : "../var/log/%s.log" % (SERVICE_NAME),
        'WFS_NAMESPACE_PREFIX'  : SERVICE_NAME, 
        'WCS_LABEL'       : WCS_LABEL
        } ) )
  f_new.close()



def makeLID(source, product_type, date_string, sources=SOURCES, product_types=ALL_PRODUCT_TYPES):
  return '_'.join([
  'FW',
  date_string,
  product_types[product_type],
  sources[source]
  ])


def makeFW2MapfilesFor(source, p_type):
  pwd = os.path.join(FW2_DATA_DIR, source, p_type)
  if not os.path.exists(pwd):
    return

  for f in os.listdir(pwd):
    products = []

    if not f.endswith(('tif', 'img')):
      continue

    f_path = os.path.join(pwd, f)
    
    # Assume a string of 8 digits in the filename is the date formatted as %Y%m%d
    match = re.search(r"(\d{8})", f)
    if not match:
      continue

    date_string = str(match.groups(1)[0])

    lid = makeLID(source, p_type, date_string)
    proj = getproj(f_path)
    if p_type == 'X_LC_PCTPROGRESS':
      colormapline = 'INCLUDE "percent_progress_color_table.cmap"'
    if source == 'Leidos':
      colormapline = 'INCLUDE "new-forwarn2-legacy-2.cmap"'
    else:
      colormapline = 'INCLUDE "new-forwarn2-standard-2.cmap"'
    products.append({
         'GROUPTEXT'     : 'GROUP %s_layers' % lid,
         'NAME'      : lid,
         'PROJ'      : formatproj(proj,10),
         'DATA'      : f_path,
         'COLORMAPLINE'  : colormapline,
         'TITLE'       : lid,
         'ABSTRACT'    : lid,
         'MASK'      : '',
    })
    for mask in ewsMask:
      products.append({
         'GROUPTEXT'     : 'GROUP %s_layers' % lid,
           'NAME'      : lid + mask['name'],
           'PROJ'      : formatproj(proj,10),
           'DATA'      : f_path,
           'COLORMAPLINE'  : colormapline,
           'TITLE'       : lid + mask['name'],
           'ABSTRACT'    : lid + mask['name'],
           'MASK'      : 'MASK ' + mask['name'],
      })

    layerTemplate = Template('ews_gen.layer.tpl.map')
    layers = ""

    for props in products:
      layers = layers + layerTemplate.render(props)  
      mapTemplate = Template("ews.map.tmpl")
      SERVICE_NAME = "forwarn_compare"
      f_new = open("forwarn2_maps/"+lid+".map", "w")
      f_new.write(mapTemplate.render({
          'DATA_DIR'        : DATA_DIR,
          'LAYERS'          : layers,
          'MS_ERRORFILE'      : "../var/log/%s.log" % (SERVICE_NAME),
          'WMS_SRS'         : "EPSG:3857 EPSG:4326",
          'MAPFILE_PROJECTION'    : '"init=epsg:4326"',
          'TEMP_FILE_PREFIX'    : "ms_%s" % (SERVICE_NAME),
          'OWS_TITLE'         : "NEMAC %s WMS" % (SERVICE_NAME),
          'OWS_ABSTRACT'      : "NEMAC %s WMS" % (SERVICE_NAME),
          'SERVICE_URL'       : "%s/%s?MAPFILE=%s" % (SERVER_URL, SERVICE_NAME, lid),
        })
      )
      f_new.close()          


def make_mapfiles():
  print "Building ForWarn 2 mapfiles..."
  for s in SOURCES:
    for p in ALL_PRODUCT_TYPES:
      makeFW2MapfilesFor(s, p)

  for s in FW2_SOURCES:
    for p in PRODUCT_TYPES:
      if s == 'ForWarn2_Sqrt' and p == 'X_LC_PCTPROGRESS':
        continue
      cgi_endpoint = '{0}_{1}'.format(FW2_SOURCES[s], PRODUCT_TYPES[p])
      makeBundledMapfileFor(s, p, cgi_endpoint)
      makeCurrentMapfilesFor(s, p)

  for s in LEGACY_SOURCES:
    for p in ALL_LEGACY_PRODUCT_TYPES:
      makeCurrentMapfilesFor(s, p, '.tif')

  print "Done building ForWarn 2 mapfiles..."
