
import os.path, datetime, re
import rasterio as rio
import functools

from base import ForWarnBase

DEFAULT_PRODUCTS_DIR = '/fsdata3/forwarn3_products'
DEFAULT_PRODUCT_EXT = 'img'
DEFAULT_TEMPLATES_DIR = './templates'
DEFAULT_MAPFILE = './fw3.map'
DEFAULT_COLOR_MAP= 'fw3_colors.include.map'
DEFAULT_MASK_TPL = 'fw3_mask.include.map.tpl'
DEFAULT_MASK_COLOR_MAP = 'fw3_mask_colors.include.map'
DEFAULT_LAYER_TPL = 'fw3_layer.include.map.tpl'
DEFAULT_MASK_DIR = '/mnt/efs/forwarn/masks'


class ForWarn3Map(ForWarnBase):

  def __init__(self):
    self.masks = ForWarnMasks()
    self.root = DEFAULT_PRODUCTS_DIR
    self._init_layers()
    self.mapfile = mappyfile.open(DEFAULT_MAPFILE)
    self.mapfile['layers'] = '\n'.join([ layer.render_tpl() for layer in self.layers ])

  def _init_mapfile(self):
    return mappyfile.open(DEFAULT_MAPFILE) 

  def _init_layers(self):
    self.layers = []
    for p in [ os.path.join(self.root, filename) for filename in os.listdir(self.root) if filename.endswith(DEFAULT_PRODUCT_EXT) ]:
      layer = ForWarn3Layer(p)
      self.layers.append(layer)




class ForWarnMasks(ForWarnBase):

  tpl = os.path.join(DEFAULT_MASK_DIR, DEFAULT_LAYER_TPL)

  masks = {
    'Forest': 'final2_ALLFOREST_mask_nalcms2010_hybrid2016nlcd_9class.img',
    'Agriculture': 'final2_AGRICULTURE_mask_nalcms2010_hybrid2016nlcd_9class.img',
    'ConiferForest': 'final2_EVERGREEN_mask_nalcms2010_hybrid2016nlcd_9class.img',
    'DeciduousForest': 'final2_DECIDUOUS_mask_nalcms2010_hybrid2016nlcd_9class.img',
    'Grass': 'final2_GRASS_mask_nalcms2010_hybrid2016nlcd_9class.img',
    'MixedForest': 'final2_MIXED_FOREST_mask_nalcms2010_hybrid2016nlcd_9class.img',
    'NonVegetated': 'final2_NON_VEGETATED_mask_nalcms2010_hybrid2016nlcd_9class.img',
    'Shrubland': 'final2_SHRUB_mask_nalcms2010_hybrid2016nlcd_9class.img',
    'Urban': 'final2_URBAN_mask_nalcms2010_hybrid2016nlcd_9class.img',
    'Wetland': 'final2_WETLAND_mask_nalcms2010_hybrid2016nlcd_9class.img'
  }

  def get_id(self, mask):
    return f'MaskFor{mask}'

  def get_path(self, mask):
    path = os.path.join(DEFAULT_MASK_DIR, self.masks[mask])
    print(path)
    return path

  def get_title(self, mask):
    return f'Mask For {mask}'

  def render_tpl(self, **kwargs):
    r = ''
    for mask in self.masks.keys():
      d = self._get_tpl_args(
          mask,
          color_map=os.path.join(DEFAULT_TEMPLATES_DIR, DEFAULT_MASK_COLOR_MAP),
          **kwargs
      )
      tpl_path = os.path.join(DEFAULT_TEMPLATES_DIR, DEFAULT_LAYER_TPL)
      r += self._render_tpl(tpl_path, d)
    return r

  def _get_tpl_args(self, mask, **kwargs):
    d = kwargs
    path = self.get_path(mask)
    _id = d.get('layer_id') or self.get_id(mask)
    d['layer_id'] = d.get('layer_id') or _id
    d['group'] = 'Masks'
    d['wms_extent'] = d.get('wms_extent') or self.get_extent(self.get_path(mask), as_string=True)
    d['path'] = d.get('path') or path
    d['proj'] = d.get('proj') or self.format_proj(self.get_proj4(path))
    d['wms_title'] = d.get('wms_title') or self.get_title(mask)
    d['wms_abstract'] = d.get('wms_abstract') or self.get_title(mask)
    d['wcs_rangeset_label'] = d.get('wcs_rangeset_label') or self.get_title(mask)
    d['wcs_bandcount'] = d.get('wcs_bandcount') or '1'
    d['wcs_formats'] = d.get('wcs_formats') or 'GEOTIFF'
    d['wcs_nativeformat'] = d.get('wcs_nativeformat') or '8-bit GeoTIF'
    d['gml_include_items'] = d.get('gml_include_items') or 'value_0'
    return d

 
class ForWarn3Layer(ForWarnBase):

  def __init__(self, path, date_format='%Y-%m-%d'):
    self._date_format = date_format
    self._file = os.path.basename(path)
    self._type = self._get_type_from_file(self._file)
    self._start_date = self._get_date_from_file(self._file)
    self._end_date = self._get_date_from_file(self._file, is_end=True)
    self._color_map = os.path.join(DEFAULT_TEMPLATES_DIR, DEFAULT_COLOR_MAP)
    self._layer_tpl = os.path.join(DEFAULT_TEMPLATES_DIR, DEFAULT_LAYER_TPL)
    self._mask_tpl = os.path.join(DEFAULT_TEMPLATES_DIR, DEFAULT_MASK_TPL)
    self._mask_color_map = os.path.join(DEFAULT_TEMPLATES_DIR, DEFAULT_MASK_COLOR_MAP)
    self.path = path
    self.start = self._start_date
    self.end = self._end_date
    self.filename = self._file
    self.ptype = self._type
    self.title = self._get_title()
    self.proj4 = self.get_proj4(self.path)
    self.ptype_title = 'Prior Year Departure' if self.ptype == '1yr' else 'Early Detect'

  def render_tpl(self, **kwargs):
    return self._render_layer_tpl(**kwargs) 

  def get_id(self):
    return self._get_id()

  def _get_id(self):
    start = self.start.strftime('%Y%m%d')
    end = self.end.strftime('%Y%m%d')
    ptype = self.ptype
    layer_id = f'FW3_{ptype}_{end}'
    return layer_id

  def _get_title(self, full=False):
    start = self.start.strftime('%m/%d/%Y')
    end = self.end.strftime('%m/%d/%Y')
    title = f'{start} - {end}'
    if full:
      title = f'ForWarn 3 {self.ptype_title}: {title}'
    return title
 
  def _render_layer_tpl(self, **kwargs):
    d = self._get_tpl_args(
        layer_id=self.get_id(),
        color_map=self._color_map,
        wms_extent=self.get_extent(self.path, as_string=True),
        **kwargs
    )
    r = self._render_tpl(self._layer_tpl, d)
    return r

  def _get_tpl_args(self, **kwargs):
    d = kwargs
    _id = d.get('layer_id') or self.get_id()
    d['layer_id'] = d.get('layer_id') or _id
    d['group'] = d.get('group') or _id
    d['wms_extent'] = d.get('wms_extent') or self.get_extent(as_string=True)
    d['path'] = d.get('path') or self.path
    d['proj'] = d.get('proj') or self.format_proj(self.proj4)
    d['wms_title'] = d.get('wms_title') or self.title
    d['wms_abstract'] = d.get('wms_abstract') or self.title
    d['wcs_rangeset_label'] = d.get('wcs_rangeset_label') or self.title
    d['wcs_bandcount'] = d.get('wcs_bandcount') or '1'
    d['wcs_formats'] = d.get('wcs_formats') or 'GEOTIFF'
    d['wcs_nativeformat'] = d.get('wcs_nativeformat') or '8-bit GeoTIF'
    d['gml_include_items'] = d.get('gml_include_items') or 'value_0'
    return d

  def _get_type_from_file(self, filename):
    if 'ED' in filename:
      return 'ED'
    if '1yr' in filename:
      return '1yr'
    raise Exception('Could not determine type from path {path}')
   
  def _get_date_from_file(self, filename, is_end=False):
    index_buffer = 11 if is_end else 0
    length_of_date_str = 10
    ds = self._file[index_buffer:index_buffer+length_of_date_str]
    date = datetime.datetime.strptime(ds, self._date_format)
    return date

  def _format_date(self, date):
    d = datetime.datetime.strftime('%Y-%m-%d')
    return d



