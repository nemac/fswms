from datetime import datetime
import os
from planet import api
from pprint import pprint
from requests.auth import HTTPBasicAuth
from requests import Session

## Initialize Planet API client

# If API key is stored as _enviroment variable_
#client = api.ClientV1()

# OR
# If API key **not** stored as an environment variable
PL_API_KEY = "INSERT_KEY_HERE"
client = api.ClientV1(api_key=PL_API_KEY)

## Look up available basemap series

# If API key is stored as _enviroment variable_
#s = Session()
#s.auth = (os.getenv('PL_API_KEY'),'')

# OR
# If API key **not** stored as an environment variable
s = Session()
s.auth = (PL_API_KEY,'')

# Direct query (via `requests` ) Planet API for list of available basemap series
series = []
series_endpoint = 'https://api.planet.com/basemaps/v1/series?_page_size=1000'
response = s.get(series_endpoint)
series.extend(response.json()['series'])
fully_paged = False
while not fully_paged:
    try:
        response.json()['_links']['_next']
        response = s.get(response.json()['_links']['_next'])
        series.extend(response.json()['series'])
    except:
        fully_paged = True

# Locate the biweekly normalized SR basemap series using internal series name.
# `PS sen2_normalized_analytic biweekly subscription`
series_id = None
for i in series:
    if i['name'] == 'PS sen2_normalized_analytic biweekly subscription':
        series_id = i['id']

## Look up available time periods and get info about most recent.

#Use series `id` value to look up available basemap time periods.
available_time_periods = client.get_mosaics_for_series(series_id).get()['mosaics']

# Create list of time periods (by `name`) and sort (reverse chronological order)
series_names = [i['name'] for i in available_time_periods]
series_names.sort(reverse=True)

# Get info about last two time periods
most_recent_mosaic = client.get_mosaic_by_name(series_names[0]).get()
previous_mosaic = client.get_mosaic_by_name(series_names[1]).get()

# Create mosaic dictionary for current and previous
mosaic_dictionary = {}
mosaic_dictionary['current'] = {
    'name': most_recent_mosaic['mosaics'][0]['name'].encode('ascii', 'ignore'),
    'date': most_recent_mosaic['mosaics'][0]['last_acquired'].split('T')[0].encode('ascii', 'ignore')
}
if len(previous_mosaic):
    mosaic_dictionary['previous'] = {
        'name': previous_mosaic['mosaics'][0]['name'].encode('ascii', 'ignore'),
        'date': previous_mosaic['mosaics'][0]['last_acquired'].split('T')[0].encode('ascii', 'ignore')
    }
else: # set previous to current until there is more than one entry
    mosaic_dictionary['previous'] = {
        'name': most_recent_mosaic['mosaics'][0]['name'].encode('ascii', 'ignore'),
        'date': most_recent_mosaic['mosaics'][0]['last_acquired'].split('T')[0].encode('ascii', 'ignore')
    }
print(mosaic_dictionary)
#return mosaic_dictionary
