import datetime, os, re, time, sys, math, requests
import xml.etree.ElementTree as ET
from dateutil import parser

from utilityScript import getLID

sys.path.append("../var")

try:
    from Config import *
    import datetime
except:
    print "Cannot find local settings file 'Config.py'.  You need to create a Config.py file that contains"
    print "settings appropriate for this copy of the FSWMS project.  You can use the file 'Config.tpl.py'"
    print "as a starting point --- make a copy of that file called 'Config.py', and edit appropriately."
    exit(-1)


class VegDRI():

  def __init__(self):
    self.url = 'https://dmsdata.cr.usgs.gov/geoserver/quickdri_vegdri_conus_1_week_data/vegdri_conus_1_week_data/wms'
    self.date_format = '%m-%d-%Y'
    self.lids = [ "VDAAM", "VDAAL", "VDAAK", "VDAAJ", "VDAAI", "VDAAH", "VDAAG", "VDAAF", "VDAAE", "VDAAD", "VDAAC", "VDAAB", "VDAAA" ]

  def render(self):
    full = ''
    times = self.get_recent_times()
    for i, timestamp in enumerate(times):
      lid = self.lids[i]
      full += self.render_layer(lid, timestamp)
    return full

  def get_capabilities(self):
    r = requests.get(self.url, params={ 'SERVICE': 'WMS', 'REQUEST': 'GetCapabilities' })
    if not r.ok:
      raise Exception('GetCapabilities request for VegDRI data failed with status code ' + r.status_code)
    xml = ET.fromstring(r.text)
    return xml

  def get_recent_times(self):
    xml = self.get_capabilities()
    schema_str = '{http://www.opengis.net/wms}'
    xpath_search = './{schema}Capability/{schema}Layer/{schema}Layer/{schema}Dimension[@name="time"]'.format(schema=schema_str)
    dim_el = xml.find(xpath_search)
    if dim_el is None:
      raise Exception('Failed to correctly parse GetCapabilities response for VegDRI data!')
    timestamps = dim_el.text.split(',')[-len(self.lids):]
    flipped = list(reversed(timestamps))
    return flipped

  def render_url(self, timestamp):
    url = '{url}?TIME={timestamp}'.format(url=self.url, timestamp=timestamp)
    return url

  def render_title(self, timestamp):
    date = parser.parse(timestamp)
    formatted = date.strftime('%m-%d-%Y')
    return formatted

  def render_layer(self, lid, timestamp):
    url = self.render_url(timestamp)
    title = self.render_title(timestamp)
    lyr_tpl = '''
          <wmsLayer
            lid="{lid}"
            visible="false"
            url="{url}"
            srs="EPSG:3857"
            layers="vegdri_conus_1_week_data"
            name="{title}"
            styles="default" 
            identify="false"
            legend="{url}&amp;SERVICE=WMS&amp;REQUEST=GetLegendGraphic&amp;layer=vegdri_conus_1_week_data&amp;VERSION=1.1.1&amp;FORMAT=image/png" />
    '''
    rendered = lyr_tpl.format(
        lid=lid,
        url=url,
        title=title
    )
    return rendered
 
