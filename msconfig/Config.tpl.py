#
# NOTE: Paths in this file should NOT end with a '/'.
#

# The base URL, complete with 'http://' prefix, of this copy of FSWMS:
SERVER_URL      = 'http://rain.nemac.org/~mbp/fswms/html'

# The absolute path of the base directory of this copy of FSWMS (this should
# be the directory containing, among other things, the subdirectories 'html' and 'msconfig').
BASE_DIR        = '/home/mbp/public_html/fswms'

# The absolute path of the directory containing the uploaded data (tif) files.
DATA_DIR        = "/flood/fsdata"

# The directory (either absolute, or relative to BASE_DIR/msconfig) of the directory
# in which symlinks should be created that point to the tif files in DATA_DIR:
LINK_TARGET_DIR = "linkdir"
#LINK_TARGET_DIR = "fsdata/fdm"

# The directory in which to put simlinks for the WMS makemap script
VIEWER_LINK_TARGET_DIR = "linkdir/viewer"
#VIEWER_LINK_TARGET_DIR = "fsdata/fdm"

# The directory in which to look for tif files to create the layers in the WMS
# (this should normally just be set to VIEWER_LINK_TARGET_DIR from above):
LAYER_DATA_DIR  = VIEWER_LINK_TARGET_DIR

# The absolute path of a CSV file that records the association between NRT layer
# names and LIDS; 'makeviewerconfig' requires this file -- it reads it, and
# updates it as needed:
NRT_LIDFILE_PATH = BASE_DIR + "/msconfig/NRTLayerLID.csv"

# The absolute path of a CSV file that records the association between DRT layer
# names and LIDS; 'makeviewerconfig' requires this file -- it reads it, and
# updates it as needed:
DRT_LIDFILE_PATH = BASE_DIR + "/msconfig/DRTLayerLID.csv"

# The URL (complete with "http://" prefix) of the directory where the viewer
# is deployed:
#VIEWER_DEPLOY_DIR_URL = "http://ews.forestthreats.org/GIS"
VIEWER_DEPLOY_DIR_URL = "http://rain.nemac.org/~mbp/fswms/html/view"

POSTGIS_CONNECTION_STRING = "host=localhost dbname=XXXXXX user=XXXXX  password=XXXXXX"
