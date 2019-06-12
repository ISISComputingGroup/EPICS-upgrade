import os

CONFIG_ROOT = os.environ["ICPCONFIGROOT"]
CONFIG_FOLDER = os.path.abspath(os.path.join(CONFIG_ROOT, "configurations"))
COMPONENT_FOLDER = os.path.abspath(os.path.join(CONFIG_ROOT, "components"))
SYNOPTIC_FOLDER = os.path.abspath(os.path.join(CONFIG_ROOT, "synoptics"))

IOC_FILE = "iocs.xml"
BLOCK_FILE = "blocks.xml"
GLOBALS_FILENAME = os.path.abspath(os.path.join(CONFIG_ROOT, "globals.txt"))

# Matches an ioc name and its numbered IOCs e.g. GALIL matches GALIL_01, GALIL_02
FILTER_REGEX = "^{}(_[\d]{{2}})?$"
