import datetime, os, re, time, sys, math, requests

sys.path.append("../var")

try:
    from Config import *
    import datetime
except:
    print "Cannot find local settings file 'Config.py'.  You need to create a Config.py file that contains"
    print "settings appropriate for this copy of the FSWMS project.  You can use the file 'Config.tpl.py'"
    print "as a starting point --- make a copy of that file called 'Config.py', and edit appropriately."
    exit(-1)


class NADM():

  def render_url(self, date):
    datestring = date.strftime('%Y%m')
    url = "https://gis.ncdc.noaa.gov/arcgis/rest/services/nadm/NADM/MapServer/export?TRANSPARENT=true&amp;layers=show%3A5&amp;LAYERDEFS={%225%22%3A%22YEAR_MONTH%3D%27" + datestring + "%27%22}"
    return url


  def render_layer(self, lid_suffix, url, title):
    fcav_lyr_tpl = '''
        <restLayer
          lid="NADM_{lid_suffix}"
          name="{title}"
          visible="false"
          url="{url}"
          format="png">
            <param name="IMAGESR" value="3857"></param>
            <param name="BBOXSR" value="3857"></param>
        </restLayer>
    '''
    rendered = fcav_lyr_tpl.format(
        lid_suffix=lid_suffix, 
        url=url,
        title=title,
    )
    return rendered


  def get_layer_list(self):
    layer_list  = []
    # YYYYMM
    start_date_str = "200211"
    d = datetime.datetime.strptime(start_date_str,'%Y%m')
    today = datetime.datetime.today()
    while (today > d):
      datestring = d.strftime('%Y%m')
      layer_list.append({
        'lid_suffix' : datestring,
        'datestring' : datestring,
        'title' : d.strftime('%b %Y'),
        'url' : self.render_url(d)
      })
      year = d.strftime('%Y')
      month = d.strftime('%m')
      if month == '12':
        year = str(int(year) + 1)
        month = '01'
      else:
        month = str(int(month) + 1)
      d = datetime.datetime.strptime('{year}{month}'.format(year=year, month=month), '%Y%m')
    layer_list.reverse()
    layer_list = self.filter_broken(layer_list)
    return layer_list

 
  def render(self):
    layer_list = self.get_layer_list()
    xml_string = ''
    year = layer_list[0]['datestring'][:4]
    xml_string += '    <wmsSubgroup label="{year}" collapsible="true">\n'.format(year=year)
    for config in layer_list:
      layer_year = config['datestring'][:4]
      if layer_year < year:
        year = layer_year
        xml_string += '    </wmsSubgroup>\n'
        xml_string += '    <wmsSubgroup label="{year}" collapsible="true">\n'.format(year=year)
      xml_string += self.render_layer(
        lid_suffix=config['lid_suffix'],
        url=config['url'],
        title=config['title'],
      )
    xml_string += '    </wmsSubgroup>'
    return xml_string


  def filter_broken(self, layer_list):
    layers = []
    this_year = y = self.get_layer_year(layer_list[0])
    for d in layer_list:
      y = self.get_layer_year(d)
      if this_year != y:
        layers.append(d)
        continue
      try:
        self.test_map(d)
        layers.append(d)
      except Exception as e:
        print e
    return layers


  def get_layer_year(self, config):
    return config['datestring'][:4]


  def test_map(self, config):
    url = config['url']
    layer_name = config['title']
    datestring = config['datestring']
    test_url = 'https://gis.ncdc.noaa.gov/arcgis/rest/services/nadm/NADM/MapServer/5/query?f=json&where=(YEAR_MONTH%20%3D%20%27{datestring}%27)%20AND%20(1%3D1)&returnGeometry=false&returnCountOnly=true&spatialRel=esriSpatialRelIntersects&outFields=*&orderByFields=OBJECTID%20ASC&outSR=102100&resultOffset=0&resultRecordCount=50'.format(datestring=datestring)
    print 'Testing NADM layer: {layer_name}'.format(layer_name=layer_name)
    r = requests.get(test_url, verify=False)
    if not r.ok or r.json()['count'] == 0:
      raise ValueError('Layer is broken or not ready yet: {layer_name}'.format(layer_name=layer_name))

