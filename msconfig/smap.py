import datetime, os, re, time, sys, math, requests

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
    d = dt or datetime.datetime.now()
    config = self.get_config(d)
    ok = False
    while not ok:
      try:
        self.test_map(**config)
        ok = True
      except ValueError:
        d -= datetime.timedelta(days=7)
        config = self.get_config(d)
    self.wk_end = config['wk_end']
    self.wk_start = config['wk_start']
    self.wk_num = config['wk_num']
    self.year = config['year']


  def get_config(self, dt):
    dt_wk_num = dt.isocalendar()[1]
    wk_num = dt_wk_num - 1
    while dt.isocalendar()[1] != wk_num:
      dt -= datetime.timedelta(days=1)
    wk_end = dt
    wk_start = wk_end - datetime.timedelta(days=6)
    year = wk_start.year
    config = {
      'wk_end' : dt,
      'wk_start' : wk_start,
      'wk_num' : str(wk_num),
      'year' : str(year),
    }
    return config


  def test_map(self, year, wk_num, wk_start, wk_end):
    kwargs = {
      'year' : str(year),
      'wk_num': str(wk_num),
      'wk_start' : wk_start.strftime('%Y.%m.%d'),
      'wk_end' : wk_end.strftime('%Y.%m.%d')
    }
    url_tpl = 'https://nassgeo.csiss.gmu.edu/cgi-bin/mapserv?MAP=/SMAP_DATA/SMAP-9KM-ANOMALY-WEEKLY/{year}/SMAP-9KM-ANOMALY-WEEKLY-TOP_{year}_{wk_num}_{wk_start}_{wk_end}.map&SERVICE=WMS&VERSION=1.1.1&REQUEST=GetMap&FORMAT=image/png&TRANSPARENT=true&LAYERS=SMAP-9KM-ANOMALY-WEEKLY-TOP_{year}_{wk_num}_{wk_start}_{wk_end}&SRS=EPSG:5070&WIDTH=512&HEIGHT=512&STYLES=&MAP_RESOLUTION=180&BBOX=469103.37588850036,1094574.5437398292,625471.1678513333,1250942.3357026621'
    url = url_tpl.format(**kwargs)
    r = requests.get(url, verify=False)
    if r.headers['Content-Type'] != 'image/png':
      print 'SMAP layer is not ready yet: '
      print kwargs
      raise ValueError('SMAP layer is not ready')


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
            "wms_name"            "SMAP-9KM-ANOMALY-WEEKLY-TOP_{year}_{wk_num}_{wk_start}_{wk_end}"
            "wms_server_version"  "1.1.1"
            "wms_format"          "image/png"
        END
      END
    '''
    kwargs = {
      'year' : str(self.year),
      'wk_num' : str(self.wk_num),
      'wk_start' : self.wk_start.strftime('%Y.%m.%d'),
      'wk_end' : self.wk_end.strftime('%Y.%m.%d')
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



