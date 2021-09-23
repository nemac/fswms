import os
from util import Template, getCurrentDates

from util import *

sys.path.append("../var")
try:
    from Config import *
except:
    print "Cannot find local settings file 'Config.py'.  You need to create a Config.py file that contains"
    print "settings appropriate for this copy of the FSWMS project.  You can use the file 'Config.tpl.py'"
    print "as a starting point --- make a copy of that file called 'Config.py', and edit appropriately."
    exit(-1)


GLAM_WMTS_LAYER_TEMPLATE = Template(string="""
  <wmtsLayer
    lid="GLAM_%(SATELLITE_ID)s_%(YEAR)s_%(JULIAN_DAY)s"
    visible="false"
    url="https://glam1n1.gsfc.nasa.gov/wmt/MODIS/%(TYPE)s/%(SATELLITE_URL_PART)s/%(YEAR)s/%(JULIAN_DAY)s/wmts"
    srs="EPSG:3857"
    layers="0"
    identify="false"
    name="%(SATELLITE_ID)s Bands %(SATELLITE_ID_NUM)s"
    mask="false"
    />
""")

def renderGlamLayerBlocksFor(yr):
  sats = ['Aqua', 'Terra']
  blocks = '<wmsSubgroup label="'+yr+'">\n</wmsSubgroup>'
  A_PATH_TO_FW2_PRODUCTS = os.path.join(FW2_DATA_DIR, FW2_SOURCES_AS_LIST[0], 'X_LC_1YEAR')
  dates = [ d for d in getCurrentDates(A_PATH_TO_FW2_PRODUCTS) ]
  for d in dates:
    # Subtract 8 days to get the start of the period. This value is passed to
    # the gimms URL template so we get the correct year.
    # "Current dates" are based on the END of the period
    period_start = d - datetime.timedelta(days=7)
    jd = period_start.strftime('%j')
    url_year = period_start.strftime('%Y')
    date_end = d
    date_start = d - datetime.timedelta(days=7)
    day_of_month_end = date_end.strftime('%d').lstrip('0')
    day_of_month_start = date_start.strftime('%d').lstrip('0')
    month_name_end = date_end.strftime('%b').lstrip('0')
    month_name_start = date_start.strftime('%b').lstrip('0')
    blocks += '<wmsSubgroup label="'+ month_name_start + day_of_month_start + '-' + month_name_end + day_of_month_end + '">\n'
    # Use Near-realtime for the latest date
    prod_type = 'nrt' if dates[0] == d else 'std'
    for sat_id in sats:
      url_part = GLAM_CONFIG[sat_id]
      id_num = '721' if sat_id == 'Aqua' else '621'
      blocks += renderGLAMLayerBlock(sat_id, id_num, url_year, url_part, jd, prod_type)
    blocks += '</wmsSubgroup>'
  return blocks


def renderGLAMLayerBlock(satellite_id, sat_id_num, yr, satellite_url_part, jd, prod_type, template=GLAM_WMTS_LAYER_TEMPLATE):
  return template.render({
    'SATELLITE_ID' : satellite_id,
    'YEAR' : yr,
    'SATELLITE_URL_PART' : satellite_url_part,
    'JULIAN_DAY' : jd,
    'SATELLITE_ID_NUM' : sat_id_num,
    'TYPE': prod_type
  })



