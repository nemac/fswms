
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

def _get_id(start, end, ptype, muted):
  start = start.strftime('%Y%m%d')
  end = end.strftime('%Y%m%d')
  layer_id = 'FW3_' + ptype + '_' + end + ('_muted' if muted else '')
  return layer_id

def formatproj(projstring, indentlevel=0):
    answer = ""
    indentation = " "*indentlevel
    lines = []
    for line in re.split(r'\s+', projstring):
        if line != "":
            lines.append("%s%s\"%s\"" % (answer, indentation, line))
    return "\n".join(lines)


def get_fw3_layer_string(path, ptype, muted):
    f = os.path.basename(path)
    proj = getproj(path)
    if ptype != 'adaptivebaseline_daysdiff':
        colormapline = 'INCLUDE "../new-forwarn2-standard-2.cmap"'
    else:
        colormapline = 'INCLUDE "../cmaps/adaptive_baseline_daysdiff.cmap"'
    start = _get_date_from_file(f)
    end = _get_date_from_file(f, is_end=True)
    title = _get_title(start, end)
    layer_id = _get_id(start, end, ptype, muted)
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
    lid="%(LAYER_LID)s"
    visible="false"
    url="%(SERVER_URL)s/forwarn3?TRANSPARENT=true"
    srs="EPSG:3857"
    layers="%(LAYER_NAME)s"
    name="%(LAYER_TITLE)s"
    styles="default" 
    identify="true"
    legend="%(SERVER_URL)s/%(LEGEND)s"
    mask="true"
    %(SELECTED)s %(BREAK)s 
  />  
""")


def get_fw3_subgroup_title(ptype, muted):
    meta_type = 'muted' if muted else 'normal'
    return FW3_PRODUCT_TYPES[meta_type][ptype]['title']


def filter_path_list(paths, muted=False, ext='.img'):
    if muted:
        return [ p for p in paths if 'muted' in p and p.endswith(ext) ]
    else:
        return [ p for p in paths if 'muted' not in p and p.endswith(ext) ]


def make_fw3_layer_list(ptype, muted):
    subgroup_title = get_fw3_subgroup_title(ptype, muted)
    string = '<wmsSubgroup label="' + subgroup_title + '">\n'
    folder = os.path.join(FW3_DATA_DIR, ptype)
    files = os.listdir(folder)
    files = filter_path_list(files, muted)
    files = sorted(files, reverse=True)
    paths = [ os.path.join(folder, f) for f in files ]
    for path in paths:
        layer_xml = make_layer_xml(path, ptype, muted)
        string += layer_xml
    string += '\n</wmsSubgroup>\n\n'
    return string


def make_fw3_viewer_xml():
    full = ''
    for meta_type in [ 'normal', 'muted' ]:
        muted = meta_type == 'muted'
        config = FW3_PRODUCT_TYPES[meta_type]
        sorted_keys = sorted(config.keys(), key=lambda x: config[x]['order'])
        for key in sorted_keys:
            full += make_fw3_layer_list(key, muted)
    return full


def make_layer_xml(path, ptype, muted):
    template = WMS_LAYER_TEMPLATE
    legend = 'cmapicons/new-forwarn2-standard-legend-2.png'
    filename = os.path.basename(path)
    start = _get_date_from_file(filename)
    end = _get_date_from_file(filename, is_end=True)
    layer_id = _get_id(start, end, ptype, muted)
    title = _get_title(start, end)
    return template.render({
      'BREAK'       : '',
      'SELECTED'    : '',
      'LAYER_LID'   : layer_id,
      'LAYER_NAME'  : layer_id,
      'LAYER_TITLE' : title,
      'SERVER_URL'  : SERVER_URL,
      'LEGEND'      : legend
    })


def make_mapfile(ptype, path, muted):
    layer_string = get_fw3_layer_string(path, ptype, muted)
    template = Template("ews_gen.tpl.map")
    f = os.path.basename(path)
    start, end = _get_date_from_file(f), _get_date_from_file(f, is_end=True)
    layer_id = _get_id(start, end, ptype, muted)
    start = _get_date_from_file(f)
    end = _get_date_from_file(f, is_end=True)
    mapfile_path = "forwarn3_maps/"+layer_id+".map"
    if os.path.exists(mapfile_path):
        try:
            os.remove(mapfile_path)
        except:
            print 'Unable to remove existing mapfile: ' + mapfile_path
    f_new = open(mapfile_path, "w")
    f_new.write(template.render( {
        'DATA_DIR'              : DATA_DIR,
        'SERVICE_URL'           : "%s/%s?MAPFILE=%s" % (SERVER_URL, 'forwarn3', layer_id),
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


def make_mapfile_batch(ptype, folder, muted):
    files = [ f for f in os.listdir(folder) if f.endswith('.img') ]
    if muted:
        files = [ f for f in files if 'muted' in f ]
    else:
        files = [ f for f in files if 'muted' not in f ]
    for f in files:
        path = os.path.join(folder, f)
        make_mapfile(ptype, path, muted)

 
def make_all(): 
    meta_types = [ 'normal', 'muted' ]
    for meta_type in meta_types:
        config = FW3_PRODUCT_TYPES[meta_type]
        for key in config.keys():
            fdr = os.path.join(FW3_DATA_DIR, key)
            title = config[key]['title']
            info = config[key]['info']
            muted = meta_type == 'muted'
            make_mapfile_batch(ptype=key, folder=fdr, muted=muted)


