import datetime, os, re, time, sys

import osr, gdal

sys.path.append("../var")
try:
    from Config import *
except:
    print("Cannot find local settings file 'Config.py'.  You need to create a Config.py file that contains")
    print("settings appropriate for this copy of the FSWMS project.  You can use the file 'Config.tpl.py'")
    print("as a starting point --- make a copy of that file called 'Config.py', and edit appropriately.")
    exit(-1)

ewsMask = [
  {'name' : 'MaskForForest'},
  {'name' : 'MaskForAgriculture'},
  {'name' : 'MaskForConiferForest'},
  {'name' : 'MaskForDeciduousForest'},
  {'name' : 'MaskForGrass'},
  {'name' : 'MaskForMixedForest'},
  {'name' : 'MaskForNonVegetated'},
  {'name' : 'MaskForShrubland'},
  {'name' : 'MaskForUrban'},
  {'name' : 'MaskForWetland'}
]

Legends = {
  'rsac' : "RSAC-FHTET_CT_7-6-2011_clipped.png",
  'tacs' : "TACs_NASA_CT_7-6-2011_clipped.png"
}

def fileEndsWith(filename, fileExts):
  for ext in fileExts:
    if filename.endswith(ext):
      return True
  return False

class Template:
  def __init__(self, file=None, **args):
    if file is None and 'string' in args:
      self.contents = args['string']
    else:
      f = open(file, "r")
      self.contents = ""
      for line in f:
        self.contents = self.contents + line
      f.close
  def render(self, dict):
    return self.contents % dict


def getLegend(layerName):
    if re.search(r'EFETAC', layerName, re.IGNORECASE):
        return "cmapicons/" + Legends['tacs']
    if re.search(r'RSAC', layerName, re.IGNORECASE):
        return "cmapicons/" + Legends['rsac']
    return ""

def rfind(dir, pattern):
    """Recursive find: returns a list of all files located in a directory or any of its descendent directories,
    and whose names match a regular expression pattern."""
    files = []
    for file in os.listdir(dir):
        if os.path.isdir(os.path.join(dir, file)):
            files = files + rfind(os.path.join(dir,file), pattern)
        if re.match(pattern, file):
            files.append(os.path.join(dir,file))
    return files

def getproj(tif):
    projectionWkt = getwkt(tif)
    spatialReferenceObj = osr.SpatialReference(projectionWkt)
    projectionProj4 = spatialReferenceObj.ExportToProj4()
    return projectionProj4

def interp(string):
  locals  = sys._getframe(1).f_locals
  globals = sys._getframe(1).f_globals
  for item in re.findall(r'#\{([^{]*)\}', string):
    string = string.replace('#{%s}' % item,
                            str(eval(item, globals, locals)))
  return string

def getwkt(tif):

    #function to get the well known text version of the
    #  spatail reference (proejction) of the image (tif)
    wktFile = tif + '.wkt'
    wktData = ''

    #check if a wkt tile exists
    wktFileExists = os.path.exists(wktFile)

    if wktFileExists:
        #if the wkt file exists read the file
        #  trying to avoid doing gdal.open its resource expensive
        #  doing a normal file read of the of MUCH smaller text file seems to speed things up
        with open(wktFile, 'r') as myfile:
            wktData = myfile.read()

    else:
        #if the wkt file does not exist thane use gdal to write it.
        dataSet = gdal.Open( tif, gdal.GA_ReadOnly )
        wktData = dataSet.GetProjection()
        f = open( wktFile, 'w' )
        f.write( wktData )
        f.close()

    return wktData

#mark out for testing new function above
#def getwkt(tif):
#    dataSet = gdal.Open( tif, gdal.GA_ReadOnly )
#    return dataSet.GetProjection()

# formatproj reformats a "proj4" projection string into the form required by a Mapserver mapfile.
# Specifically, it splits it into one expression per line, delimited by double quotes.  It takes
# an optional indentation level, and indents the returned string by that number of spaces.
def formatproj(projstring, indentlevel=0):
    answer = ""
    indentation = " "*indentlevel
    lines = []
    for line in re.split(r'\s+', projstring):
        if line != "":
            lines.append("%s%s\"%s\"" % (answer, indentation, line))
    return "\n".join(lines)

# getModDate gets the date when a file was last edited and formats that timestamp in a readable form
def getModDate(filename):
    t = os.stat(filename).st_mtime
    return datetime.datetime.fromtimestamp(t)

###
### This function simply opens a file for writing, and appends the name of the file
### to the mapfilesWritten array, which is used at the bottom of this script to
### write the index.html file with the list of all the WMS addresses.
###
def openMapfileForWriting(filename):
    return open(filename, "w");


def getProcessedLids(csvName):
  processed_lids = dict()
  if csvName in processed_lids:
    return processed_lids[csvName]
  lids_list = []
  lyrs_dict = dict()
  f = open(csvName, "r");
  for line in f:
    sp = line.split(',')
    lid = sp[1].upper().rstrip()
    lyrs_dict[sp[0]] = lid
    lids_list.append(lid)
  f.close();
  file_lids = {
    'lyrs_dict': lyrs_dict,
    'lids_list': lids_list
  }
  processed_lids[csvName] = file_lids
  return file_lids


def next_alpha(s):
    s = s.lower();
    strip_zs = s.rstrip('z')
    if strip_zs:
        leading_chrs = strip_zs[:-1]
        last_chr = strip_zs[-1]
        new_chr = chr((ord(last_chr) + 1))
        # if the last characters are 'z's then you need to append that many 'a's to the string                        
        trailing_a_chrs = 'a' * (len(s) - len(strip_zs))

        new_string = leading_chrs + new_chr + trailing_a_chrs
        return new_string.upper()
    else:
        return ('a' * (len(s) + 1)).upper()


def getLID(layerName, csvName):
  file_lids = getProcessedLids(csvName)
  lids_list = file_lids['lids_list']
  lyrs_dict = file_lids['lyrs_dict']

  layerName = layerName.rstrip()
  if layerName in lyrs_dict:
    nlid = lyrs_dict[layerName]
  else: #this is new one, iterate and add to file
    highest_lid = max(lids_list)
    nlid = next_alpha(highest_lid)

    lyrs_dict[layerName] = nlid
    lids_list.append(nlid)
    
    f = open(csvName, "a");
    f.write(layerName+ "," + nlid + "\n")
    f.close()
  return nlid


def getMonthAndDayDateRangeString(d):
  d2 = d - datetime.timedelta(days=23)
  d1_day = datetime.datetime.strftime(d, '%d').lstrip('0')
  d2_day = datetime.datetime.strftime(d2, '%d').lstrip('0')
  d1_f = datetime.datetime.strftime(d, '%b') + d1_day
  d2_f = datetime.datetime.strftime(d2, '%b') + d2_day
  return d2_f + '-' + d1_f


def extractDateString(f):
  try:
    match = re.search(r"(\d{8})", f)
    if (match.groups(1)):
      return match.groups(1)[0]
    return None
  except:
    return None


def getCurrentDates(pwd, date_format=None):
  files = os.listdir(pwd)
  dateStrings = map(lambda f: extractDateString(f), files)
  # remove duplicates from wkt files
  dateStrings = list(set(dateStrings))
  dateStrings = list(filter(lambda s: s is not None, dateStrings))
  dates = map(lambda ds: datetime.datetime.strptime(ds, "%Y%m%d"), dateStrings)
  sorted_timestamps = list(reversed(sorted(map(lambda d: time.mktime(d.timetuple()), dates))))
  current_timestamps = sorted_timestamps[:3]
  current_dates = map(lambda t: datetime.datetime.fromtimestamp(t), current_timestamps)
  if (date_format):
    return map(lambda d: datetime.datetime.strftime(d, date_format), current_dates)
  return current_dates


''' 
timeframe information for makeDateRangeQueryParam:
0 = current 24 day period
1 = previous 24 day period
2 = previous previous 24 day period before 1

startYear paramater returns everthing from Jan 1st of selected year to present day.
e.g. startYear=2015 returns 2015-01-01/2020-05-18 if executed on May 18th, 2020
'''
def makeDateRangeQueryParam(path, param_template, prior_year=False, date_template='%Y-%m-%d', timeframe=0, yearToDate=False, startYear=CURRENT_YEAR):
  startYear = int(startYear)
  d = getCurrentDates(path)[timeframe]
  date_end = d
  date_start = date_end - datetime.timedelta(days=23)
  if prior_year:
    date_end = date_end - datetime.timedelta(days=365)
    date_start = date_start - datetime.timedelta(days=365)
  if yearToDate:
    current_date = datetime.datetime.now()
    date_end = datetime.datetime(current_date.year, current_date.month, current_date.day)
    date_start = datetime.datetime(startYear, 1, 1) # January 1 of start year
  date_range = formatDateRange(date_start, date_end, param_template, date_template)
  return date_range

def formatDateRange(date_start, date_end, param_template, date_template='%Y-%m-%d'):
  date_end = datetime.datetime.strftime(date_end, date_template)
  date_start = datetime.datetime.strftime(date_start, date_template)
  date_range = param_template.format(date_start, date_end)
  return date_range

if __name__ == "__main__":
    # execute only if run as a script
    main()
