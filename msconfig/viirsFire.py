import datetime, os, re, time, sys, math, requests

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


if not os.path.exists(DRT_LIDFILE_PATH):
    print "Can't read required DRT LID file '%s'.  Aborting." % (DRT_LIDFILE_PATH)
    exit(-1)
 

class viirs_fire():

  def render_url(self):
    # url = "{url}/cgi-bin/mapserv.exe?map=/ms4w/apps/usdm/service/usdm_{datestring}_wms.map&amp;TRANSPARENT=true".format(datestring=datestring, url=USDM_PROXY_API)
    url = "https://firms.modaps.eosdis.nasa.gov/mapserver/wms/cumulative_year/daeadb37a15dc29f0405b1f741b16a0b/cy_viirs_noaa20_usa_contiguous_and_hawaii/?REQUEST=GetMap"
    return url

  def render_layer(self, lid, drt_url, name, title):
    fcav_lyr_tpl = '''
          <wmsLayer
            lid="{lid}"
            visible="false"
            url="{drt_url}"
            srs="EPSG:900913"
            layers="{name}"
            name="{title}"
            styles="default" 
            identify="false"
            legend="{server_url}/cmapicons/cumulative-current-year.png" />
    '''
    rendered = fcav_lyr_tpl.format(
        lid=lid, 
        drt_url=drt_url,
        name=name,
        title=title,
        server_url=SERVER_URL
    )
    return rendered

 
  def render(self):
    layer_list  = []
    #lid = getLID("usdm"+d.strftime('%y%m%d'), DRT_LIDFILE_PATH)
    lid = "test_viirs_lid"
    url = self.render_url()
    # layer_name = "usdm"+d.strftime('%Y%m%d')
    layer_name = "test_virs_name"
    # layer_title = d.strftime('%m/%d/%Y')
    layer_title = "NOAA-20 VIIRS Year to Date"
    layer_list.append({
        'LAYER_LID'   : lid,
        'LAYER_NAME'  : layer_name,
        'LAYER_TITLE' : layer_title,
        'SERVER_URL'  : SERVER_URL,
        'DRT_URL'     : url
    })
    for config in layer_list:
        layers = self.render_layer(
            config['LAYER_LID'],
            config['DRT_URL'],
            config['LAYER_NAME'],
            config['LAYER_TITLE']
        )
    return layers


  def get_layer_year(self, config):
    return int(config['LAYER_NAME'].lstrip('usdm')[0:4])


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


  def test_map(self, config):
    url = config['DRT_URL']
    layer_name = config['LAYER_NAME']
    test_url = '{url}&PROJECTION=EPSG%3A3857&UNITS=m&LAYERS={layer_name}&SERVICE=WMS&VERSION=1.1.1&REQUEST=GetMap&STYLES=&FORMAT=image%2Fpng&SRS=EPSG%3A3857&BBOX=-11993496.685428,5440532.8031968,-11984596.548946,5444402.4277538&WIDTH=10&HEIGHT=10'.format(url=url, layer_name=layer_name)
    print 'Testing USDM layer: {layer_name}'.format(layer_name=layer_name)
    r = requests.get(test_url, verify=False)
    if r.headers['Content-Type'] != 'image/png':
      raise ValueError('Layer is broken or not ready yet: {url}'.format(url=url))

