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
 

class USDM_Current():

  def render_url(self, date):
    datestring = date.strftime('%Y%m%d')
    #url = "{url}/cgi-bin/mapserv.exe?map=/ms4w/apps/usdm/service/usdm_{datestring}_wms.map&amp;TRANSPARENT=true".format(datestring=datestring, url=USDM_PROXY_API)
    url = "{url}/cgi-bin/mapserv.exe?map=/ms4w/apps/usdm/service/usdm_current_wms.map&amp;TRANSPARENT=true".format(url=USDM_PROXY_API)
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
            legend="{server_url}/cmapicons/drought-monitor.png" />
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
    start_date_str = "000104"
    d = datetime.datetime.strptime(start_date_str,'%y%m%d')
    today = datetime.datetime.today()
    counter = 0
    #while (today > d):
    while (counter < 1):
       #lid = getLID("usdm"+d.strftime('%y%m%d'), DRT_LIDFILE_PATH)
       lid = "usdm_current"
       url = self.render_url(d)
       #layer_name = "usdm"+d.strftime('%Y%m%d')
       layer_name = "usdm_current"
       #layer_title = d.strftime('%m/%d/%Y')
       layer_title = "Current"
       layer_list.append({
          'LAYER_LID'   : lid,
          'LAYER_NAME'  : layer_name,
          'LAYER_TITLE' : layer_title,
          'SERVER_URL'  : SERVER_URL,
          'DRT_URL'     : url
       })
       d = d + datetime.timedelta(days=7)
       counter += 1
    layer_list.reverse() #reverse the list so that newest dates are on top always
    #year = layer_list[0]['LAYER_NAME'].lstrip('usdm')[0:4]
    year = 2022
    layer_list = self.filter_broken(layer_list)
    layers = '<wmsSubgroup label="{0}" collapsible="true">\n'.format('Current')
    for config in layer_list:
        #layer_year = config['LAYER_NAME'].lstrip('usdm')[0:4]
        layer_year = 2022
        if layer_year < year:
          year = layer_year
          layers += '    </wmsSubgroup>\n'
          #layers += '    <wmsSubgroup label="{0}" collapsible="true">\n'.format(year)
          layers += '    <wmsSubgroup label="Current" collapsible="true">\n'
        layers = layers + self.render_layer(
            config['LAYER_LID'],
            config['DRT_URL'],
            config['LAYER_NAME'],
            config['LAYER_TITLE']
        )
    layers += "</wmsSubgroup>\n"
    return layers


  def get_layer_year(self, config):
    #return int(config['LAYER_NAME'].lstrip('usdm')[0:4])
    return 2022


  def filter_broken(self, layer_list):
    layers = []
    #this_year = y = self.get_layer_year(layer_list[0])
    this_year = 2022
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

