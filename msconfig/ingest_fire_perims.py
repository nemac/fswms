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


def put_results_in_db():
  '''
  Place contents of intermediate SQLite db into efetac postgis database
  Remove -append if the table does not already exist
  '''
  c = '''ogr2ogr -overwrite -skipfailures -f PostgreSQL -nln {} PG:"{}" result.json'''.format(ACTIVE_FIRES_TABLE, POSTGIS_ROOT_CONNECTION_STRING)
  print(c)
  os.system(c)
  print()


def main():
  url = query_builder()
  r = requests.get(url)
  with open('./result.json', 'w') as f:
    d = r.text.encode('ascii', 'ignore')
    f.write(d)
  put_results_in_db()
  os.remove('result.json')


if __name__ == '__main__':
  main()

