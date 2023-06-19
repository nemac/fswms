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
    '1yr_dev': {
      'title': 'One Year',
      'info': 'One Year Net Ecological Impact',
      'order': 1
    },
    '3yr_dev': {
      'title': 'Three Year',
      'info': 'Three Year Net Ecological Impact',
      'order': 2
    },
    '5yr_dev': {
      'title': 'Five Year',
      'info': 'Five Year Net Ecological Impact',
      'order': 3
    },
  },
  'muted': {
  }
}


