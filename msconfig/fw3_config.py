'''
Main config for describing FW3 layer lists in FCAV

 - Top-level keys 'normal' and 'muted' differentiate normal vs muted meta-types
   - Muted products are the square root of the normal product at each pixel
 - The next level down describes the product types for each meta-type
   - Keys are the names of directories in FW3_DATA_DIR (see ../var/Config.py)
 - Each object describing a product type has the following keys:
   - title: The HTML-escaped title of the layer list in the FCAV
   - info: A description of the product type, displayed under the title
   - order: The order the layer list appears in the FCAV (includes
   - break: Indicates that an extra linebreak should follow this layer list in the FCAV
     - If not present will default to True (see fw3.py)
'''

FW3_PRODUCT_TYPES = {
  'normal': {
    'EED': {
      'title': '&quot;Preview&quot; Early-Early Detect from 6-day One-Year Maximum Baseline &quot;Normal&quot;',
      'info': 'Shows the most recent 6-day departures, relative to the last year.',
      'order': 1,
      'break': False
    },
    '2yrEED': {
      'title': '&quot;Preview&quot; Early-Early Detect from 6-day Two-Year Maximum Baseline &quot;Normal&quot;',
      'info': 'Shows the most recent 6-day departures, relative to the last two years.',
      'order': 2
    },
    'phenoregionEED': {
      'title': '&quot;Preview&quot; Early-Early Detect from 6-day Phenoregion Baseline &quot;Normal&quot;',
      'info': 'Shows the most recent 6-day departures, relative to a multi-year median.',
      'order': 3,
      'break': False
    },
    'ED': {
      'title': 'Early Detect from 8-day One-Year Maximum Baseline &quot;Normal&quot;',
      'info': 'Shows the most recent 8-day departures, relative to the last year.',
      'order': 4,
      'break': False
    },
    '2yrED': {
      'title': 'Early Detect From 8-day Two-Year Maximum Baseline &quot;Normal&quot;',
      'info': 'Shows the most recent 8-day departures, relative to the last two years.',
      'order': 5
    },
    'phenoregionED': {
      'title': 'Early Detect from 8-day Phenoregion Baseline &quot;Normal&quot;',
      'info': 'Shows the most recent 8-day departures, relative to a multi-year median.',
      'order': 6,
      'break': False
    },
    '1yr': {
      'title': 'From Prior One-Year Maximum Baseline &quot;Normal&quot;',
      'info': 'Shows departures that occurred in the last year.',
      'order': 7
    },
    'adaptivebaseline_allyr': {
      'title': 'From Seasonal Progress Adaptive Baseline &quot;Normal&quot;',
      'info': 'Based on Current Percent Completion of green-up or Brown-down in the surrounding phenoregion in all prior years, rather than dates observed. Enhances Small-Scale Local Departures by de-trending/removing larger scale Regional differences.',
      'order': 8,
      'break': False
    },
    'adaptivebaseline_daysdiff': {
      'title': 'Days Early/Late Timing Departures indicated by the Adaptive Baseline &quot;Normal&quot;',
      'info': 'Compares date differences between present time and when Seasonal Progress-based greenness is normally seen in all prior years.',
      'order': 9
    },
    'phenoregions_regionalonly': {
      'title': 'Large-Scale Regional Departures Only &quot;Normal&quot;',
      'info': 'Enhances Wide-Area Departures by using zonal median values from the surrounding Phenoregion. Removes Smaller Departures altogether to only show Regional effects.',
      'order': 10
    },
    '3yr': {
      'title': 'From Prior Three-Year Maximum Baseline &quot;Normal&quot;',
      'info': 'Shows departures that occurred in the last three years.',
      'order': 11
    },
    '5yr': {
      'title': 'From Prior Five-Year 90th Percentile Baseline &quot;Normal&quot;',
      'info': 'Shows departures that occurred in the last five years.',
      'order': 12
    },
    'phenoregions_baseline': {
      'title': 'From All-Prior-Year Phenoregion Baseline &quot;Normal&quot;',
      'info': 'Shows departures relative to the all-year trend.',
      'order': 13
    },
    'phenoregions_seasonalprogress': {
      'title': 'Phenoregion Percent Seasonal Progress Departure',
      'info': 'Shows departure in timing of seasonal development relative to the all-year trend.',
      'order': 14
    },
  },
  'muted': {
    'EED': {
      'title': '&quot;Preview&quot; Early-Early Detect from 6-day One-Year Maximum Baseline &quot;Muted&quot;',
      'info': 'Shows the most recent 6-day departures, relative to the last year.',
      'order': 1,
      'break': False
    },
    '2yrEED': {
      'title': '&quot;Preview&quot; Early-Early Detect from 6-day Two-Year Maximum Baseline &quot;Muted&quot;',
      'info': 'Shows the most recent 6-day departures, relative to the last two years.',
      'order': 2
    },
    'phenoregionEED': {
      'title': '&quot;Preview&quot; Early-Early Detect from 6-day Phenoregion Baseline &quot;Muted&quot;',
      'info': 'Shows the most recent 6-day departures, relative to a multi-year median.',
      'order': 3,
      'break': False
    },
    'ED': {
      'title': 'Early Detect from 8-day One-Year Maximum Baseline &quot;Muted&quot;',
      'info': 'Shows the most recent 8-day departures, relative to the last year.',
      'order': 4,
      'break': False
    },
    '2yrED': {
      'title': 'Early Detect From 8-day Two-Year Maximum Baseline &quot;Muted&quot;',
      'info': 'Shows the newest, most-recent departures in the last two years.',
      'order': 5
    },
    'phenoregionED': {
      'title': 'Early Detect from 8-day Phenoregion Baseline &quot;Muted&quot;',
      'info': 'Shows the most recent 8-day departures, relative to a multi-year median.',
      'order': 6,
      'break': False
    },
    '1yr': {
      'title': 'From Prior One-Year Maximum Baseline &quot;Muted&quot;',
      'info': 'Shows departures that occurred in the last year.',
      'order': 7
    },
    'adaptivebaseline_allyr': {
      'title': 'From Seasonal Progress Adaptive Baseline &quot;Muted&quot;',
      'info': 'Based on Current Percent Completion of green-up or Brown-down in the surrounding phenoregion in all prior years, rather than dates observed. Enhances Small-Scale Local Departures by de-trending/removing larger scale Regional differences.',
      'order': 8
    },
    'phenoregions_regionalonly': {
      'title': 'Large-Scale Regional Departures Only &quot;Muted&quot;',
      'info': 'Enhances Wide-Area Departures by using zonal median values from the surrounding Phenoregion. Removes Smaller Departures altogether to only show Regional effects.',
      'order': 9
    },
    '3yr': {
      'title': 'From Prior Three-Year Maximum Baseline &quot;Muted&quot;',
      'info': 'Shows departures that occurred in the last three years.',
      'order': 10
    },
    '5yr': {
      'title': 'From Prior Five-Year 90th Percentile Baseline &quot;Muted&quot;',
      'info': 'Shows departures that occurred in the last five years.',
      'order': 11
    },
    'phenoregions_baseline': {
      'title': 'From All-Prior-Year Phenoregion Baseline &quot;Muted&quot;',
      'info': 'Shows departures relative to the all-year trend.',
      'order': 12
    },
  }
}


