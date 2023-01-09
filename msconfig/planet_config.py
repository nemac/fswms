import sys, os
from planet import api
from requests.auth import HTTPBasicAuth
from requests import Session

sys.path.append("../var")
try:
    from Config import *
    import datetime
except:
    print "Cannot find local settings file 'Config.py'.  You need to create a Config.py file that contains"
    print "settings appropriate for this copy of the FSWMS project.  You can use the file 'Config.tpl.py'"
    print "as a starting point --- make a copy of that file called 'Config.py', and edit appropriately."
    exit(-1)


'''This method uses the planet.com API to find all of the fourteen day USDA Normalized Analytic Mosaics
    and puts them into a dictionary for easy consumption in the ews config template'''
def makePlanetDotComUSDANormalizedAnalyticFourteenDayList():
    os.environ['PL_API_KEY'] = PLANET_API_KEY 
    client = api.ClientV1(api_key=PLANET_API_KEY)
    s = Session()
    s.auth = (PLANET_API_KEY,'')

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


    return mosaic_dictionary

