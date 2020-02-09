# -*- coding: utf-8 -*-
# --------------------------------------------------------------------------------
# Scraper tools for reading and processing web elements
# --------------------------------------------------------------------------------

#from future import standard_library
#standard_library.install_aliases()
#from builtins import str
#from builtins import chr
import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

import re


def find_single_match(data, patron, index=0):
    try:
        matches = re.findall(patron, data, flags=re.DOTALL)
        return matches[index]
    except:
        return ""


# Parse string and extracts multiple matches using regular expressions
def find_multiple_matches(text, pattern):
    return re.findall(pattern, text, re.DOTALL)
