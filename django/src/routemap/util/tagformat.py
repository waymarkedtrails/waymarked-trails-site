"""
Helper functions to format the OSM tag values.
"""

import re

unit_re = re.compile("\s*(\d+)([.,](\d+))?\s*([a-zA-Z]*)")

def convert_to_km(value):
    """Take an OSM value and make the best guess at a
       conversion into kilometers.
    """
    if value is not None:
        m = unit_re.match(value)
        if m is not None:
            if m.group(3) is None:
                mag = float(m.group(1))
            else:
                mag = float('%s.%s' % (m.group(1), m.group(3)))
            unit = m.group(4).lower()
            if unit == '' or unit == 'km':
                return mag
            elif unit == 'm':
                return mag/1000
            elif unit == 'mi':
                return mag*1.6093

    return None
