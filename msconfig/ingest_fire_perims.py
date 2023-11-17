#!/usr/bin/env python

import ogr
import os
import os.path
import shutil
import datetime
import argparse
import traceback
import requests
import sys
import datetime
import json

sys.path.append("../var")
try:
    from Config import *
    import datetime
except:
    print "Cannot find local settings file 'Config.py'.  You need to create a Config.py file that contains"
    print "settings appropriate for this copy of the FSWMS project.  You can use the file 'Config.tpl.py'"
    print "as a starting point --- make a copy of that file called 'Config.py', and edit appropriately."
    exit(-1)


def query_builder(): #(start_date, end_date):
  url = "https://services3.arcgis.com/T4QMspbfLg3qTGWY/arcgis/rest/services/CY_WildlandFire_Perimeters_ToDate/FeatureServer/0/query?outFields=*&outSR=4326&f=pgeojson&orderByFields=poly_GISACRES+desc&where=1%3D1"
  print(url)
  return url


def put_results_in_db(table):
  '''
  Place contents of intermediate SQLite db into efetac postgis database
  Remove -append if the table does not already exist
  '''
  #c = '''ogr2ogr -overwrite -skipfailures -f PostgreSQL -nln {} PG:"{}" result.json'''.format(ACTIVE_FIRES_TABLE, POSTGIS_ROOT_CONNECTION_STRING)
  c = '''ogr2ogr -overwrite -skipfailures -f PostgreSQL -nln {} PG:"{}" result.json'''.format(table, POSTGIS_ROOT_CONNECTION_STRING)
  print(c)
  os.system(c)
  print()


def main():
  urls = {
    # ACTIVE_FIRES_TABLE is broken
    #ACTIVE_FIRES_TABLE: 'https://services3.arcgis.com/T4QMspbfLg3qTGWY/arcgis/rest/services/CY_WildlandFire_Perimeters_ToDate/FeatureServer/0/query?outFields=*&outSR=4326&f=pgeojson&orderByFields=poly_GISACRES+desc&where=1%3D1',
    WILDLAND_FIRES_INCIDENT_TABLE: 'https://services3.arcgis.com/T4QMspbfLg3qTGWY/arcgis/rest/services/WFIGS_Incident_Locations_YearToDate/FeatureServer/0/query?outFields=*&outSR=4326&orderByFields=firediscoverydatetime+desc&where=1%3D1&f=geojson',
    WFIGS_INTERAGENCY_FIRE_PERIMS_TABLE: 'https://services3.arcgis.com/T4QMspbfLg3qTGWY/arcgis/rest/services/WFIGS_Interagency_Perimeters/FeatureServer/0/query?outFields=*&outSR=4326&orderByFields=poly_datecurrent+desc&where=1%3D1&f=geojson',
    WFIGS_INTERAGENCY_FIRE_PERIMS_TO_DATE_TABLE: 'https://services3.arcgis.com/T4QMspbfLg3qTGWY/arcgis/rest/services/WFIGS_Interagency_Perimeters_YearToDate/FeatureServer/0/query?outFields=*&outSR=4326&orderByFields=poly_datecurrent+desc&where=1%3D1&f=geojson'
  }
  for x, y in urls.items():
    table = x
    url = y
    response = requests.get(url)
    data = response.json()

    # Convert dates to human readable time if they exist
    # Lots of code duplication here. It can be better but it's Friday before Thanksgiving and trying to get this out
    for feature in data['features']:
      if table == WFIGS_INTERAGENCY_FIRE_PERIMS_TABLE or table == WFIGS_INTERAGENCY_FIRE_PERIMS_TO_DATE_TABLE:
        if feature['properties']['poly_DateCurrent'] is not None:
          unix_time = int(feature['properties']['poly_DateCurrent'])
          human_time = datetime.datetime.fromtimestamp(unix_time/1000).strftime('%c')
          feature['properties']['DateCurrent_S'] = human_time

        if feature['properties']['poly_CreateDate'] is not None:
          unix_time = int(feature['properties']['poly_CreateDate'])
          human_time = datetime.datetime.fromtimestamp(unix_time/1000).strftime('%c')
          feature['properties']['CreateDate_S'] = human_time

        if feature['properties']['poly_PolygonDateTime'] is not None:
          unix_time = int(feature['properties']['poly_PolygonDateTime'])
          human_time = datetime.datetime.fromtimestamp(unix_time/1000).strftime('%c')
          feature['properties']['PolygonDateTime_S'] = human_time

      else:
        if feature['properties']['FireDiscoveryDateTime'] is not None:
          unix_time = int(feature['properties']['FireDiscoveryDateTime'])
          human_time = datetime.datetime.fromtimestamp(unix_time/1000).strftime('%c')
          feature['properties']['FireDiscoveryDT_S'] = human_time

    # Write the results to a JSON file
    with open('result.json', 'w') as f:
      json.dump(data, f)

    #r = requests.get(url)
    #with open('./result.json', 'w') as f:
    #  d = r.text.encode('ascii', 'ignore')
    #  f.write(d)
    put_results_in_db(table)
    os.remove('result.json')


if __name__ == '__main__':
  main()

