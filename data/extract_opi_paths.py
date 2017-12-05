import os
from xml.dom import minidom

# Script to extract the OPI paths from the OPI info file. Prints output to screen in the syntax of a Python
# dict[path]=key
INFO_PATH = "C:\\Instrument\\Dev\\ibex_gui\\base\\uk.ac.stfc.isis.ibex.opis\\resources\\opi_info.xml"
info_xml = minidom.parse(INFO_PATH)
entries = info_xml.getElementsByTagName("entry")

key_paths = []
for entry_xml in info_xml.getElementsByTagName("entry"):
    key = entry_xml.getElementsByTagName("key")[0].firstChild.nodeValue
    path = entry_xml.getElementsByTagName("value")[0].getElementsByTagName("path")[0].firstChild.nodeValue
    key_paths.append((key, path))

print("OPI_PATH_KEYS = {")
for k, p in key_paths:
    print("    '{0}': '{1}',".format(p, k))
print("}")
