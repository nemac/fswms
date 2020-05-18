import datetime, os, re, time

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
def makeDateRangeQueryParam(path, param_template, prior_year=False, date_template='%Y-%m-%d', timeframe=0, yearToDate=False, startYear=2020):
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