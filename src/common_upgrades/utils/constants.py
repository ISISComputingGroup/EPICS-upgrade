import os

EPICS_ROOT = os.environ["EPICS_ROOT"]
SUPPORT_ROOT = os.path.abspath(os.path.join(EPICS_ROOT, "support"))

CONFIG_ROOT = os.environ["ICPCONFIGROOT"]
CONFIG_FOLDER = os.path.abspath(os.path.join(CONFIG_ROOT, "configurations"))
COMPONENT_FOLDER = os.path.abspath(os.path.join(CONFIG_ROOT, "components"))
SYNOPTIC_FOLDER = os.path.abspath(os.path.join(CONFIG_ROOT, "synoptics"))
DEVICE_SCREENS_FOLDER = os.path.abspath(os.path.join(CONFIG_ROOT, "devices"))

ICP_CONFIG_BASE = os.environ["ICPCONFIGBASE"]
CALIB_FOLDER = os.path.abspath(os.path.join(ICP_CONFIG_BASE, "common"))

SCRIPTS_ROOT = os.environ["ICPINSTSCRIPTROOT"]

IOC_FILE = "iocs.xml"
BLOCK_FILE = "blocks.xml"
DEVICE_SCREEN_FILE = "screens.xml"
GLOBALS_FILENAME = os.path.abspath(os.path.join(CONFIG_ROOT, "globals.txt"))
DASHBOARD_DB_FILENAME = os.path.abspath(os.path.join(CONFIG_ROOT, "dashboard.db"))

MOTION_SET_POINTS_FOLDER = os.path.abspath(os.path.join(CONFIG_ROOT, "motionSetPoints"))

# Matches an ioc name and its numbered IOCs e.g. GALIL matches GALIL_01, GALIL_02
FILTER_REGEX = r"^{}(_[\d]{{2}})?$"
