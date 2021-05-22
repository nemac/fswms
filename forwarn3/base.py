
import rasterio as rio
import re

class ForWarnBase:

  def render_tpl(self, path, _dict):
    return self._render_tpl(path, _dict)

  def get_wkt(self, path, write=True):
    wkt = self._get_wkt(path, write=write)
    return wkt

  def get_proj4(self, path):
    proj4 = self._get_proj4(path)
    return proj4

  def get_crs(self, path):
    crs = self._get_crs(path)
    return crs

  def format_proj(self, proj, indent_level=10):
      answer = ""
      indentation = " " * indent_level
      lines = []
      for line in re.split(r'\s+', proj):
          if line != "":
              lines.append("%s%s\"%s\"" % (answer, indentation, line))
      return "\n".join(lines)

  def get_extent(self, path, as_string=False, as_dict=False):
    return self._get_extent(path, as_string=as_string, as_dict=as_dict)

  def _render_tpl(self, path, _dict):
    with open(path) as f:
      tpl = str(f.read())
      r = tpl.format(**_dict)
      return r

  def _get_crs(self, path):
    with rio.open(path) as f:
      crs = f.crs
    return crs

  def _get_extent(self, path, as_string=False, as_dict=False):
    assert not (as_string and as_dict)
    with rio.open(path) as f:
      bounds = f.bounds
    if as_string:
      bounds = ' '.join([ str(c) for c in bounds ])
    if as_dict:
      # LL[XY] = lower-left [xy]
      # UR[XY] = upper-right [xy]
      bounds = { 'LLX': bounds[0], 'LLY': bounds[1], 'URX': bounds[2], 'URY': bounds[3] }
    return bounds

  def _get_wkt(self, path, write=False):
    wkt_path = f'{path}.wkt'
    try:
      wkt = self._read_file(wkt_path)
    except FileNotFoundError:
      wkt = self._get_crs(path).to_wkt()
      if write:
        self._write_file(wkt_path, wkt)
    return wkt

  def _get_proj4(self, path, write=False):
    proj_path = '{path}.proj'
    try:
      proj4 = self._read_file(proj_path)
    except FileNotFoundError:
      print(path)
      proj4 = self._get_crs(path).to_proj4()
      if write:
        self._write_file(proj_path, proj4)
    return proj4

  def _read_file(self, path, lines=False):
    with open(path) as f:
      if lines:
        d = f.readlines()
      else:
        d = f.read()
    return d

  def _write_file(self, path, contents):
    assert not os.path.exists(path)
    with open(path, 'w') as f:
      f.write(contents)
 
