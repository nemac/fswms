
import sys, os, datetime, re
from osgeo import gdal, osr

sys.path.append('../var')
from Config import *


ewsMask = [
    {'name' : 'MaskForForest'},
    {'name' : 'MaskForAgriculture'},
    {'name' : 'MaskForConiferForest'},
    {'name' : 'MaskForDeciduousForest'},
    {'name' : 'MaskForGrass'},
    {'name' : 'MaskForMixedForest'},
    {'name' : 'MaskForNonVegetated'},
    {'name' : 'MaskForShrubland'},
    {'name' : 'MaskForUrban'},
    {'name' : 'MaskForWetland'}
    ]   

class Template:
    def __init__(self, file):
        f = open(file, "r")
        self.contents = ""
        for line in f:
            self.contents = self.contents + line
        f.close
    def render(self, dict):
        return self.contents % dict

def getproj(tif):
    projectionWkt = getwkt(tif)
    spatialReferenceObj = osr.SpatialReference(projectionWkt)
    projectionProj4 = spatialReferenceObj.ExportToProj4()
    return projectionProj4

def getwkt(tif):

    #function to get the well known text version of the
    #  spatail reference (proejction) of the image (tif)
    wktFile = tif + '.wkt'
    wktData = ''

    #check if a wkt tile exists
    wktFileExists = os.path.exists(wktFile)

    if wktFileExists:
        #if the wkt file exists read the file
        #  trying to avoid doing gdal.open its resource expensive
        #  doing a normal file read of the of MUCH smaller text file seems to speed things up
        with open(wktFile, 'r') as myfile:
            wktData = myfile.read()

    else:
        #if the wkt file does not exist thane use gdal to write it.
        dataSet = gdal.Open( tif, gdal.GA_ReadOnly )
        wktData = dataSet.GetProjection()
        f = open( wktFile, 'w' )
        f.write( wktData )
        f.close()

    return wktData




# everything below is not in makemap already

def _get_date_from_file(filename, is_end=False):
  index_buffer = 11 if is_end else 0
  length_of_date_str = 10
  ds = filename[index_buffer:index_buffer+length_of_date_str]
  date = datetime.datetime.strptime(ds, '%Y-%m-%d')
  return date

def _get_title(start, end):
  start = start.strftime('%m/%d/%Y')
  end = end.strftime('%m/%d/%Y')
  title = start + ' - ' + end
  return title

def _get_id(start, end, ptype):
  start = start.strftime('%Y%m%d')
  end = end.strftime('%Y%m%d')
  layer_id = 'FW3_' + ptype + '_' + end
  return layer_id

def formatproj(projstring, indentlevel=0):
    answer = ""
    indentation = " "*indentlevel
    lines = []
    for line in re.split(r'\s+', projstring):
        if line != "":
            lines.append("%s%s\"%s\"" % (answer, indentation, line))
    return "\n".join(lines)


def get_fw3_layer_string(path, ptype):
    f = os.path.basename(path)
    proj = getproj(path)
    colormapline = 'INCLUDE "../new-forwarn2-standard-2.cmap"'
    start = _get_date_from_file(f)
    end = _get_date_from_file(f, is_end=True)
    title = _get_title(start, end)
    layer_id = _get_id(start, end, ptype)
    layers = []
    layers.append({
       'TIF'             : f,
       'PROJVALID'       : len(proj) > 0,
       'PROJ'            : formatproj(proj,10),
       'WKT'             : getwkt(path),
       'NAME'            : layer_id,
       'DATA'            : path,
       'TITLE'           : layer_id,
       'GROUPTEXT'       : 'GROUP FW_%s_layers' % layer_id,
       'ABSTRACT'        : layer_id,
       'COLORMAPLINE'    : colormapline,
       'MASK'            : ''
    })
    for mask in ewsMask:
        layers.append({  'TIF'             : f,
                         'PROJVALID'       : len(proj) > 0,
                         'PROJ'            : formatproj(proj,10),
                         'WKT'             : getwkt(path),
                         'NAME'            : layer_id + mask['name'],
                         'DATA'            : path,
                         'TITLE'           : layer_id + mask['name'],
                         'GROUPTEXT'       : 'GROUP FW_%s_layers' % layer_id,
                         'ABSTRACT'        : layer_id + mask['name'],
                         'COLORMAPLINE'    : colormapline,
                         'MASK'            : 'MASK ' + mask['name'],
                         })
    tpl = Template("ews_gen.layer.tpl.map")
    layer_string = ""
    layer_string = "\n".join([ tpl.render(d) for d in layers ])
    return layer_string


def _get_ptype_from_path(path):
  filename = os.path.basename(path)
  if '1yr' in filename:
    return '1yr'
  if 'ED' in filename:
    return 'ED'
  return None




def make_mapfile(path):
    ptype = _get_ptype_from_path(path)
    assert ptype is not None
    layer_string = get_fw3_layer_string(path, ptype)
    template = Template("ews_gen.tpl.map")
    f = os.path.basename(path)
    start, end = _get_date_from_file(f), _get_date_from_file(f, is_end=True)
    layer_id = _get_id(start, end, ptype)
    start = _get_date_from_file(f)
    end = _get_date_from_file(f, is_end=True)
    mapfile_path = "forwarn3_maps/"+layer_id+".map"
    try:
        os.remove(mapfile_path)
    except:
        pass
    f_new = open(mapfile_path, "w")
    f_new.write(template.render( {
        'DATA_DIR'              : DATA_DIR,
        'SERVICE_URL'           : "%s/%s?MAPFILE=%s" % (SERVER_URL, 'fw3_test', layer_id),
        'LAYERS'                : layer_string,
        'WMS_SRS'               : "EPSG:4326 EPSG:2163 EPSG:3857 EPSG:900913",
        'MAPFILE_PROJECTION'    : '"init=epsg:3857"',
        'SERVICE_NAME'          : 'forwarn3',
        'TEMP_FILE_PREFIX'      : "ms_%s" % (layer_id),
        'MAPFILE'               : "%s/msconfig/forwarn3_maps/%s.map" % (BASE_DIR, layer_id),
        'OWS_TITLE'             : "NEMAC %s WMS" % (layer_id),
        'OWS_ABSTRACT'          : "NEMAC %s WMS" % (layer_id),
        'OWS_KEYWORDLIST'       : "mapserver,ogc,%s" % (layer_id),
        'MS_ERRORFILE'          : "../var/log/%s.log" % (layer_id),
        'WFS_NAMESPACE_PREFIX'  : layer_id, 
        'WCS_LABEL'             : layer_id
    }))
    f_new.close()



class FrontendTemplate:
    def __init__(self, file=None, **args):
        if file is None and 'string' in args:
            self.contents = args['string']
        else:
            f = open(file, "r")
            self.contents = ""
            for line in f:
                self.contents = self.contents + line
            f.close
    def render(self, dict):
        return self.contents % dict


WMS_LAYER_TEMPLATE = FrontendTemplate(string="""
  <wmsLayer
    %(SELECTED)s %(BREAK)s
    lid="%(LAYER_LID)s"
    visible="false"
    url="%(SERVER_URL)s/fw3_test?TRANSPARENT=true"
    srs="EPSG:3857"
    layers="%(LAYER_NAME)s"
    name="%(LAYER_TITLE)s"
    styles="default" 
    identify="true"
    legend="%(SERVER_URL)s/%(LEGEND)s"
    mask="true"
/>  
""")

def make_fw3_layer_list(ptype):
  string = ''
  for f in [ f for f in sorted(os.listdir(FW3_DATA_DIR), reverse=True) if ptype in f and f.endswith('img') ]:
    path = os.path.join(FW3_DATA_DIR, f)
    layer_xml = make_layer_xml(path)
    string += layer_xml
  return string

def make_layer_xml(path):
    template = WMS_LAYER_TEMPLATE
    legend = 'cmapicons/new-forwarn2-standard-legend-2.png'
    filename = os.path.basename(path)
    ptype = _get_ptype_from_path(path)
    assert ptype is not None
    start = _get_date_from_file(filename)
    end = _get_date_from_file(filename, is_end=True)
    layer_id = _get_id(start, end, ptype)
    title = _get_title(start, end)
    return template.render({
      'SELECTED'    : '',
      'LAYER_LID'   : layer_id,
      'LAYER_NAME'  : layer_id,
      'LAYER_TITLE' : title,
      'SERVER_URL'  : SERVER_URL,
      'BREAK'       : '',
      'LEGEND'      : legend
    })

 
def make_all(): 
    fw3_paths = [
      os.path.join(FW3_DATA_DIR, f) for f in os.listdir(FW3_DATA_DIR)
      if f.endswith('img') and ('1yr' in f or 'ED' in f)
    ]
    for path in fw3_paths:
        make_mapfile(path)

