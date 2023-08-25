import sys, os, datetime, re
from osgeo import gdal, osr

from fw3_config_dev import FW3_PRODUCT_TYPES

from util import ewsMask, Template, getproj, getwkt

sys.path.append('../var')
from Config import DATA_DIR, SERVER_URL, BASE_DIR
FW3_DATA_DIR = "/mnt/efs/forwarn/net_ecological_impact_dev_products" # NEW
SUB_DIRS = ['1yr_dev', '2yr_dev', '3yr_dev', '4yr_dev', '5yr_dev']

FW3_PRODUCT_TYPES = {
  '1yr_dev': {
    'title': 'One Year',
    'info': 'One Year Net Ecological Impact',
    'order': 1
  },
  '2yr_dev': {
    'title': 'Two Year',
    'info': 'Two Year Net Ecological Impact',
    'order': 2
  },
  '3yr_dev': {
    'title': 'Three Year',
    'info': 'Three Year Net Ecological Impact',
    'order': 3
  },
  '4yr_dev': {
    'title': 'Four Year',
    'info': 'Four Year Net Ecological Impact',
    'order': 4
  },
  '5yr_dev': {
    'title': 'Five Year',
    'info': 'Five Year Net Ecological Impact',
    'order': 5
  },
}

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

def _get_id(start, end, ptype):
  start = start.strftime('%Y%m%d')
  end = end.strftime('%Y%m%d')
  layer_id = 'FW3_' + ptype + '_' + end
  return layer_id

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
            break="%(BREAK)s"
            %(SELECTED)s
          />
""")

def filter_path_list(paths, ext='.img'):
    return [ p for p in paths if 'muted' not in p and p.endswith(ext) ]

def make_layer_xml(path, layer_id, insertBreak="false", title=None):
    filename = os.path.basename(path)
    template = WMS_LAYER_TEMPLATE
    legend_file = 'new-forwarn2-standard-legend-2.png'
    legend = os.path.join(SERVER_URL, 'cmapicons', legend_file)
    return template.render({
      'SELECTED'    : '',
      'LAYER_LID'   : layer_id,
      'LAYER_NAME'  : layer_id,
      'LAYER_TITLE' : title,
      'SERVER_URL'  : SERVER_URL,
      'LEGEND'      : legend,
      'BREAK'       : insertBreak
    })

def make_current_layer_list(year_dict, start_dates, end_dates):
    year_list = []
    string = ''
    for idx, d in enumerate(start_dates):
        if d.year not in year_list:
            if len(year_list) > 0:
                string += '\n</wmsSubgroup>\n\n'
            year_list.append(d.year)
            string+= '<wmsSubgroup label="' + str(d.year) + '" collapsible="true">\n'
        start = d
        end = end_dates[idx]
        subgroup_title = _get_title(start, end)
        #string += '    <wmsSubgroup label="' + subgroup_title + '">\n'
        for key in SUB_DIRS:
            insertBreak = "false"
            if key == '5yr_dev':
                insertBreak = "true"
            try:
                title = subgroup_title + ' ' +  str(key)
                ptype = key
                layer_id = _get_id(start, end, ptype)
                layer_xml = make_layer_xml(year_dict[key][idx], layer_id, insertBreak, title)
                string += layer_xml
            except:
                continue
        #string += '\n    </wmsSubgroup>\n\n'
    string += '\n</wmsSubgroup>\n\n'
    return string    
        
def make_fw3_dev_xml_new_test():
    full = ''
    year_dict = {}
    start_date_list = []
    end_date_list = []
    for key in SUB_DIRS:
        folder = os.path.join(FW3_DATA_DIR, key)
        files = os.listdir(folder)
        files = filter_path_list(files)
        files = sorted(files, reverse=True)
        if (key == '1yr_dev'):
            for f in files:
                start_date_list.append(_get_date_from_file(f))
                end_date_list.append(_get_date_from_file(f, is_end=True))
        paths = [ os.path.join(folder, f) for f in files ]
        year_dict[key] = paths
    full += make_current_layer_list(year_dict, start_date_list, end_date_list)
    print(full)
    return full

if __name__ == '__main__':
    make_fw3_dev_xml_new_test()
