import datetime, os, re, time, sys, math, requests

import xml.etree.ElementTree as ET

sys.path.append("../var")

try:
    from Config import *
    import datetime
except:
    print "Cannot find local settings file 'Config.py'.  You need to create a Config.py file that contains"
    print "settings appropriate for this copy of the FSWMS project.  You can use the file 'Config.tpl.py'"
    print "as a starting point --- make a copy of that file called 'Config.py', and edit appropriately."
    exit(-1)



class SMAP9kAnomalyTopWeekly():

  def __init__(self, dt=None):
    dt = dt or datetime.datetime.now()
    year = dt.year
    while True:
      url = 'https://cloud.csiss.gmu.edu/smap_server/cgi-bin/mapserv?MAP=/WMS/SMAP-9KM-ANOMALY-WEEKLY-TOP_{year}.map&SERVICE=WMS&REQUEST=GetCapabilities&VERSION=1.1.1'.format(year=year)
      r = requests.get(url, verify=False)
      if not r.ok or r.headers['Content-Type'] != 'application/vnd.ogc.wms_xml; charset=UTF-8':
        print 'SMAP mapfile for {year} is unavailable. Trying {str(int(year)-1)}'.format(year=year)
        year = str(int(year)-1)
      else:
        break
    xml = ET.fromstring(r.text)
    top_layer_elem = xml.find('Capability').find('Layer')
    latest_layer = list(top_layer_elem)[-1]
    self.name = latest_layer.find('Name').text
    self.year = year
    wk_end_datestring = '{year}.{datestring}'.format(year=year, datestring=self.name[-5:])
    self.wk_end = datetime.datetime.strptime(wk_end_datestring, '%Y.%m.%d')
    self.wk_start = self.wk_end - datetime.timedelta(days=6)


  def render_map_tpl(self):
    map_tpl = '''
      LAYER
        NAME "smap_9k_anomaly_weekly_top"
        TYPE RASTER
        STATUS OFF
        CONNECTION "https://cloud.csiss.gmu.edu/smap_server/cgi-bin/mapserv?MAP=/WMS/SMAP-9KM-ANOMALY-WEEKLY-TOP_{year}.map"
        CONNECTIONTYPE WMS
        METADATA
            "wms_srs"             "EPSG:4326"
            "wms_name"            "{name}"
            "wms_server_version"  "1.1.1"
            "wms_format"          "image/png"
        END
      END
    '''
    kwargs = {
      'year' : str(self.year),
      'name' : self.name
    }
    rendered = map_tpl.format(**kwargs)
    return rendered


  def render_view_tpl(self):
    view_tpl = '''
      <wmsSubgroup label="SMAP 9K Anomaly (Weekly)">
        <wmsLayer label="SMAP 9k Top Anomaly {wk_start_title} - {wk_end_title}"
          lid="SMAP9KTOPWEEKLY"
          visible="false"
          url="{server_url}/rlayers"
          srs="EPSG:3857"
          layers="smap_9k_anomaly_weekly_top"
          name="SMAP 9k Top Anomaly ({wk_start_title} - {wk_end_title})"
          identify="false"
          legend="{server_url}/rlayers?SERVICE=WMS&amp;REQUEST=GetLegendGraphic&amp;layer=smap_9k_anomaly_weekly_top&amp;VERSION=1.1.1&amp;FORMAT=image/png"/>
        />
      </wmsSubgroup>
    '''
    kwargs = {
      'wk_start_title' : self.wk_start.strftime('%m/%d'),
      'wk_end_title' : self.wk_end.strftime('%m/%d'),
      'server_url' : SERVER_URL
    }
    rendered = view_tpl.format(**kwargs)
    return rendered



