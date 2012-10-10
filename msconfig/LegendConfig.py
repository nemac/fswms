import re

Legends = {
  'rsac' : "RSAC-FHTET_CT_7-6-2011_clipped.png",
  'tacs' : "TACs_NASA_CT_7-6-2011_clipped.png"
}

def getLegend(layerName):
    if re.search(r'EFETAC', layerName, re.IGNORECASE):
        return "cmapicons/" + Legends['tacs']
    if re.search(r'RSAC', layerName, re.IGNORECASE):
        return "cmapicons/" + Legends['rsac']
    return ""
