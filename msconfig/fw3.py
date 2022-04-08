#!/usr/bin/env python

import sys, os, datetime, re
from osgeo import gdal, osr

from fw3_config import FW3_PRODUCT_TYPES 

from util import ewsMask, Template, getproj, getwkt

sys.path.append('../var')
from Config import FW3_DATA_DIR, DATA_DIR, SERVER_URL, BASE_DIR


def _get_date_from_file(filename, is_end=False, d_format='%Y-%m-%d'):
  index_buffer = 11 if is_end else 0
  length_of_date_str = 10
  ds = filename[index_buffer:index_buffer+length_of_date_str]
  date = datetime.datetime.strptime(ds, d_format)
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

def get_fw3_layer_string(path, ptype, muted, title=None, layer_id=None):
    f = os.path.basename(path)
    proj = getproj(path)
    if ptype == 'adaptivebaseline_daysdiff':
        colormapline = 'INCLUDE "../cmaps/adaptive_baseline_daysdiff.cmap"'
    elif ptype == 'ED' or ptype == '2yrED' or ptype == 'EED' or ptype == '2yrEED' or ptype == 'phenoregionEED' or ptype == 'phenoregionED':
        colormapline = 'INCLUDE "../cmaps/fw3_ED.cmap"'
    elif ptype == 'phenoregions_seasonalprogress':
        colormapline = 'INCLUDE "../cmaps/fw3_phenoregions_seasonalprogress.cmap"'
    else:
        colormapline = 'INCLUDE "../new-forwarn2-standard-2.cmap"'
    start = _get_date_from_file(f)
    end = _get_date_from_file(f, is_end=True)
    title = title or _get_title(start, end)
    layer_id = layer_id or _get_id(start, end, ptype, muted)
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
    legend="%(LEGEND)s"
    mask="true"
    %(SELECTED)s %(BREAK)s 
  />  
""")


def get_fw3_subgroup_title(ptype, muted):
    meta_type = 'muted' if muted else 'normal'
    return FW3_PRODUCT_TYPES[meta_type][ptype]['title']

def get_fw3_subgroup_info(ptype, muted):
    meta_type = 'muted' if muted else 'normal'
    return FW3_PRODUCT_TYPES[meta_type][ptype]['info']

def filter_path_list(paths, muted=False, ext='.img'):
    if muted:
        return [ p for p in paths if 'muted' in p and p.endswith(ext) ]
    else:
        return [ p for p in paths if 'muted' not in p and p.endswith(ext) ]

def to_add_sublist_spacing(ptype, muted, default=True):
    meta_type = 'muted' if muted else 'normal'
    add_break = default
    try:
        add_break = FW3_PRODUCT_TYPES[meta_type][ptype]['break']
    except:
        pass 
    return add_break

def make_fw3_layer_list(ptype, muted):
    subgroup_title = get_fw3_subgroup_title(ptype, muted)
    subgroup_info = get_fw3_subgroup_info(ptype, muted)
    to_break = to_add_sublist_spacing(ptype, muted)
    break_text = 'break="true"' if to_break else 'break="false"'
    string = '<wmsSubgroup label="' + subgroup_title + '" info="' + subgroup_info + '" ' + break_text + '>\n'
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

def current_title_maker(filename, title_prefix, muted):
    start = _get_date_from_file(filename)
    end = _get_date_from_file(filename, is_end=True)
    title = '{prefix} %Departure {start}-{end}'.format(
        prefix=title_prefix,
        start=start.strftime('%b%d'),
        end=end.strftime('%b%d')
    )
    if muted:
        title += ' (Muted Grass/Shrub)'
    return title

def current_id_maker(index, ptype, muted):
    how_current = [ 'current', 'previous1', 'previous2' ]    
    _id = 'FW3_{ptype}_{how_current}'.format(ptype=ptype, how_current=how_current[index])
    if muted:
        _id += '_muted'
    return _id

def make_current_mapfiles(ptype, muted):
    folder = os.path.join(FW3_DATA_DIR, ptype)
    files = os.listdir(folder)
    files = filter_path_list(files, muted=muted)
    files = sorted(files, reverse=True)[:3]
    paths = [ os.path.join(folder, f) for f in files ]
    prefixes = [ 'Current', 'Previous1', 'Previous2' ]
    for i, path in enumerate(paths):
        filename = os.path.basename(path)
        layer_id = current_id_maker(i, ptype, muted=muted)
        make_mapfile(ptype, path, muted=muted, layer_id=layer_id)

def make_current_layer_list(ptype, muted):
    # NOTE: this function has the side effect of creating symlinks to mapfiles
    subgroup_title = get_fw3_subgroup_title(ptype, muted=muted)
    subgroup_info = get_fw3_subgroup_info(ptype, muted=muted)
    subgroup_title = subgroup_title
    to_break = to_add_sublist_spacing(ptype, muted=muted)
    break_text = 'break="true"' if to_break else 'break="false"'
    string = '<wmsSubgroup label="' + subgroup_title + '" info="' + subgroup_info + '" ' + break_text + '>\n'
    folder = os.path.join(FW3_DATA_DIR, ptype)
    files = os.listdir(folder)
    files = filter_path_list(files, muted=muted)
    files = sorted(files, reverse=True)[:3]
    paths = [ os.path.join(folder, f) for f in files ]
    prefixes = [ 'Current', 'Previous1', 'Previous2' ]
    for i, path in enumerate(paths):
        filename = os.path.basename(path)
        title = current_title_maker(filename, prefixes[i], muted=muted)
        layer_id = current_id_maker(i, ptype, muted=muted)
        layer_xml = make_layer_xml(path, ptype, title=title, layer_id=layer_id, muted=muted)
        string += layer_xml
    string += '\n</wmsSubgroup>\n\n'
    return string

def make_fw3_current_xml():
    full = ''
    for meta_type in [ 'normal', 'muted' ]:
        muted = meta_type == 'muted'
        config = FW3_PRODUCT_TYPES[meta_type]
        sorted_keys = sorted(config.keys(), key=lambda x: config[x]['order'])
        for key in sorted_keys:
            full += make_current_layer_list(key, muted)
    return full

def make_fw3_archive_xml():
    full = ''
    for meta_type in [ 'normal', 'muted' ]:
        muted = meta_type == 'muted'
        config = FW3_PRODUCT_TYPES[meta_type]
        sorted_keys = sorted(config.keys(), key=lambda x: config[x]['order'])
        for key in sorted_keys:
            full += make_fw3_layer_list(key, muted)
    return full

def make_layer_xml(path, ptype, muted, title=None, layer_id=None, to_break=False):
    filename = os.path.basename(path)
    start = _get_date_from_file(filename)
    end = _get_date_from_file(filename, is_end=True)
    layer_id = layer_id or _get_id(start, end, ptype, muted)
    title = title or _get_title(start, end)
    template = WMS_LAYER_TEMPLATE
    if ptype == 'adaptivebaseline_daysdiff':
        legend_file = 'daysdifflegend.png'
      	legend = os.path.join(SERVER_URL, 'cmapicons', legend_file)
    else:
        legend_file = 'new-forwarn2-standard-legend-2.png'
        legend = os.path.join(SERVER_URL, 'cmapicons', legend_file)
    # Temporary fix while aqua is down
    selected = ''
    if layer_id == 'FW3_adaptivebaseline_allyr_current':
      selected = "selected=\"true\""
    # End of temporary fix
    return template.render({
      'BREAK'       : '' if not to_break else 'break="true"',
      #'SELECTED'    : '',
      'SELECTED'    : selected,
      'LAYER_LID'   : layer_id,
      'LAYER_NAME'  : layer_id,
      'LAYER_TITLE' : title,
      'SERVER_URL'  : SERVER_URL,
      'LEGEND'      : legend
    })

def get_mapfile_path(ptype, path, muted):
    f = os.path.basename(path)
    start, end = _get_date_from_file(f), _get_date_from_file(f, is_end=True)
    layer_id = _get_id(start, end, ptype, muted)
    mapfile_path = os.path.join(BASE_DIR, 'msconfig', 'forwarn3_maps', layer_id+'.map')
    return mapfile_path

def make_mapfile(ptype, path, muted, layer_id=None):
    layer_string = get_fw3_layer_string(path, ptype, muted, layer_id=layer_id)
    template = Template("ews_gen.tpl.map")
    f = os.path.basename(path)
    start, end = _get_date_from_file(f), _get_date_from_file(f, is_end=True)
    layer_id = layer_id or _get_id(start, end, ptype, muted)
    mapfile_path = 'forwarn3_maps/'+layer_id+'.map'
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

 
def make_mapfiles(): 
    print "Building ForWarn 3 mapfiles..."
    meta_types = [ 'normal', 'muted' ]
    for meta_type in meta_types:
        config = FW3_PRODUCT_TYPES[meta_type]
        for key in config.keys():
            fdr = os.path.join(FW3_DATA_DIR, key)
            title = config[key]['title']
            info = config[key]['info']
            muted = meta_type == 'muted'
            make_mapfile_batch(ptype=key, folder=fdr, muted=muted)
            make_current_mapfiles(ptype=key, muted=muted)

    print "Done!"


if __name__ == '__main__':
    make_mapfiles()
