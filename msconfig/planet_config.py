import sys, os
from planet import api

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
  client = api.ClientV1()
  # grab all mosaics - this is a bit presumptious but it may be okay if we only ever get what we expect
  # if this ever breaks in the future this is probably why
  allMosaics = client.get_mosaics().get()
  mosaics = allMosaics['mosaics']
  # Separate the mosaics into a dictionary of 'current' and 'previous' containing the name of the mosaic and ending date (e.g. 2020-08-24)
  mosaic_dictionary = {}
  mosaic_dictionary['current'] = {
    'name': mosaics[-1]['name'].encode('ascii', 'ignore'), 
    'date': mosaics[-1]['last_acquired'].split('T')[0].encode('ascii', 'ignore')
  }
  if len(mosaics) > 1:
    mosaic_dictionary['previous'] = {
      'name': mosaics[-2]['name'].encode('ascii', 'ignore'), 
      'date': mosaics[-2]['last_acquired'].split('T')[0].encode('ascii', 'ignore')
    }
  else: # set previous to current until there is more than one entry 
    mosaic_dictionary['previous'] = {
      'name': mosaics[-1]['name'].encode('ascii', 'ignore'),
      'date': mosaics[-1]['last_acquired'].split('T')[0].encode('ascii', 'ignore')
    }
  return mosaic_dictionary


