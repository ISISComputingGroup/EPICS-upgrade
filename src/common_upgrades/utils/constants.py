import os

CONFIG_FOLDER = os.path.abspath(os.path.join(os.environ["ICPCONFIGROOT"], "configurations"))
COMPONENT_FOLDER = os.path.abspath(os.path.join(os.environ["ICPCONFIGROOT"], "components"))
SYNOPTIC_FOLDER = os.path.abspath(os.path.join(os.environ["ICPCONFIGROOT"], "synoptics"))
IOC_FILE = "iocs.xml"
GLOBALS_FILENAME = os.path.abspath(os.path.join(os.environ["ICPCONFIGROOT"], "globals.txt"))

# Matches an ioc name and its numbered IOCs e.g. GALIL matches GALIL_01, GALIL_02
FILTER_REGEX = "^{}(_[\d]{{2}})?$"
