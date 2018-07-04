import os

CONFIG_FOLDER = os.path.join("configurations", "configurations")
COMPONENT_FOLDER = os.path.join("configurations", "components")
IOC_FILE = "iocs.xml"
GLOBALS_FILENAME = os.path.join("configurations", "globals.txt")

# Matches an ioc name and it's numbered IOC's e.g. GALIL matches GALIL_01, GALIL_02
FILTER_REGEX = "^{}(_[\d]{{2}})?$"
