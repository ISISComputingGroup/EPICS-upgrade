"""
Mother for test objects
"""

from xml.dom import minidom


class LoggingStub(object):
    """
    Stub for logging
    """
    def __init__(self):
        self.log = []
        self.log_err = []
        self.config_base = "BASE"

    def error(self, message):
        self.log_err.append(message)

    def info(self, message):
        self.log.append(message)


class FileAccessStub(object):
    """
    Stub for file access
    """
    def __init__(self):
        self.wrote_version = None
        self.write_filename = None
        self.write_file_contents = None

    def write_version_number(self, version, filename):
        self.wrote_version = version

    def write_file(self, filename, contents):
        self.write_filename = filename
        self.write_file_contents = "\n".join(contents)

    def open_file(self, filename):
        return EXAMPLE_GLOBALS_FILE.splitlines()

    def write_xml_file(self, filename, xml):
        self.write_filename = filename
        self.write_file_contents = xml.toxml()

    def open_xml_file(self, filename):
        return minidom.parseString(self.open_file(filename))

    def listdir(self, dir):
        return ["file1.xml", "README.txt", "file2.xml"]

    def remove_file(self, filename):
        pass

    def is_dir(self, path):
        pass

    def exists(self, path):
        return True


def create_xml_with_iocs(iocs):
    """
    Args:
        iocs (list): A list of IOC names
    Returns:
        str: xml containing the supplied IOCs
    """
    doc = minidom.Document()
    top = doc.createElement("iocs")
    for ioc in iocs:
        child = doc.createElement('ioc')
        child.setAttribute("name", ioc)
        top.appendChild(child)
    doc.appendChild(top)
    return doc


CLEAN_COMPONENT_BASE_IOC_FILE_v3p2p1 = """<?xml version="1.0" ?>
<iocs xmlns="http://epics.isis.rl.ac.uk/schema/iocs/1.0" xmlns:ioc="http://epics.isis.rl.ac.uk/schema/iocs/1.0" xmlns:xi="http://www.w3.org/2001/XInclude">
    <ioc autostart="true" name="INSTETC_01" restart="true" simlevel="none">
        <macros/>
        <pvs/>
        <pvsets/>
    </ioc>
    <ioc autostart="true" name="ISISDAE_01" restart="true" simlevel="none">
        <macros/>
        <pvs/>
        <pvsets/>
    </ioc>
    <!-- Above this line only change in master branch -->
</iocs>
"""

CLEAN_COMPONENT_BASE_IOC_FILE_v3p2p1p1 = """<?xml version="1.0" ?>
<iocs xmlns="http://epics.isis.rl.ac.uk/schema/iocs/1.0" xmlns:ioc="http://epics.isis.rl.ac.uk/schema/iocs/1.0" xmlns:xi="http://www.w3.org/2001/XInclude">
    <ioc autostart="true" name="INSTETC_01" restart="true" simlevel="none">
        <macros/>
        <pvs/>
        <pvsets/>
    </ioc>
    <ioc autostart="true" name="ISISDAE_01" restart="true" simlevel="none">
        <macros/>
        <pvs/>
        <pvsets/>
    </ioc>
    <ioc autostart="true" name="ALARM" restart="true" simlevel="none">
        <macros/>
        <pvs/>
        <pvsets/>
    </ioc>
    <!-- Above this line only change in master branch -->
</iocs>
"""

CLEAN_COMPONENT_BASE_IOC_FILE_v3p2p1p2 = """<?xml version="1.0" ?>
<iocs xmlns="http://epics.isis.rl.ac.uk/schema/iocs/1.0" xmlns:ioc="http://epics.isis.rl.ac.uk/schema/iocs/1.0" xmlns:xi="http://www.w3.org/2001/XInclude">
    <ioc autostart="true" name="INSTETC_01" restart="true" simlevel="none">
        <macros/>
        <pvs/>
        <pvsets/>
    </ioc>
    <ioc autostart="true" name="ISISDAE_01" restart="true" simlevel="none">
        <macros/>
        <pvs/>
        <pvsets/>
    </ioc>
    <ioc autostart="true" name="ALARM" restart="true" simlevel="none">
        <macros/>
        <pvs/>
        <pvsets/>
    </ioc>
    <ioc autostart="true" name="ARACCESS" restart="true" simlevel="none">
        <macros/>
        <pvs/>
        <pvsets/>
    </ioc>    
    <!-- Above this line only change in master branch -->
</iocs>
"""

ERROR_COMPONENT_BASE_IOC_FILE_NO_ISISDAE="""<?xml version="1.0" ?>
<iocs xmlns="http://epics.isis.rl.ac.uk/schema/iocs/1.0" xmlns:ioc="http://epics.isis.rl.ac.uk/schema/iocs/1.0" xmlns:xi="http://www.w3.org/2001/XInclude">
    <ioc autostart="true" name="INSTETC_01" restart="true" simlevel="none">
        <macros/>
        <pvs/>
        <pvsets/>
    </ioc>
    <ioc autostart="true" name="NOTISISDAE_01" restart="true" simlevel="none">
        <macros/>
        <pvs/>
        <pvsets/>
    </ioc>
    <!-- Above this line only change in master branch -->
</iocs>
"""

ERROR_COMPONENT_BASE_IOC_FILE_TWO_ALARMS = """<?xml version="1.0" ?>
<iocs xmlns="http://epics.isis.rl.ac.uk/schema/iocs/1.0" xmlns:ioc="http://epics.isis.rl.ac.uk/schema/iocs/1.0" xmlns:xi="http://www.w3.org/2001/XInclude">
    <ioc autostart="true" name="INSTETC_01" restart="true" simlevel="none">
        <macros/>
        <pvs/>
        <pvsets/>
    </ioc>
    <ioc autostart="true" name="ISISDAE_01" restart="true" simlevel="none">
        <macros/>
        <pvs/>
        <pvsets/>
    </ioc>
    <ioc autostart="true" name="ALARM" restart="true" simlevel="none">
        <macros/>
        <pvs/>
        <pvsets/>
    </ioc>
    <ioc autostart="true" name="ALARM" restart="true" simlevel="none">
        <macros/>
        <pvs/>
        <pvsets/>
    </ioc>
    <!-- Above this line only change in master branch -->
</iocs>
"""

ERROR_COMPONENT_BASE_IOC_FILE_TWO_ARACCESS = """<?xml version="1.0" ?>
<iocs xmlns="http://epics.isis.rl.ac.uk/schema/iocs/1.0" xmlns:ioc="http://epics.isis.rl.ac.uk/schema/iocs/1.0" xmlns:xi="http://www.w3.org/2001/XInclude">
    <ioc autostart="true" name="INSTETC_01" restart="true" simlevel="none">
        <macros/>
        <pvs/>
        <pvsets/>
    </ioc>
    <ioc autostart="true" name="ISISDAE_01" restart="true" simlevel="none">
        <macros/>
        <pvs/>
        <pvsets/>
    </ioc>
    <ioc autostart="true" name="ALARM" restart="true" simlevel="none">
        <macros/>
        <pvs/>
        <pvsets/>
    </ioc>
     <ioc autostart="true" name="ARACCESS" restart="true" simlevel="none">
        <macros/>
        <pvs/>
        <pvsets/>
    </ioc>
     <ioc autostart="true" name="ARACCESS" restart="true" simlevel="none">
        <macros/>
        <pvs/>
        <pvsets/>
    </ioc> 
    <!-- Above this line only change in master branch -->
</iocs>
"""

SYOPTIC_WITH_TEMPLATE_TARGET_NAME = """<?xml version="1.0" ?>
<instrument xmlns="http://www.isis.stfc.ac.uk//instrument">
    <name>Goniometer</name>
    <components>
        <component>
            <name>New Component</name>
            <type>GONIOMETER</type>
            <target>
                <name>{0}</name>
                <type>OPI</type>
                <properties/>
            </target>
            <pvs/>
            <components/>
        </component>
    </components>
</instrument>
"""

CLEAN_SYNOPTIC_v3p2p1p2 = SYOPTIC_WITH_TEMPLATE_TARGET_NAME.format("Goniometer")
UNKNOWN_SYNOPTIC_v3p2p1p2 = SYOPTIC_WITH_TEMPLATE_TARGET_NAME.format("unknown\path\gonio.opi")
DIRECT_PATH_SYNOPTIC_v4p0p0 = SYOPTIC_WITH_TEMPLATE_TARGET_NAME.format("jaws/Jaws.opi")
DIRECT_PATH_SYNOPTIC_v3p2p1p2 = SYOPTIC_WITH_TEMPLATE_TARGET_NAME.format("Jaws.opi")

EXAMPLE_GLOBALS_FILE = """
# IOC specific macros
# Names changed to prevent accidental overwrites during testing
BINS_01__PLCIP=127.0.0.1
GALOL_01__GALOLADDR=127.0.0.1
GALOL_02__GALOLADDR=127.0.0.1
GALOL_03__GALOLADDR=127.0.0.1
GALOL_04__GALOLADDR=127.0.0.1
GALOL_05__GALOLADDR=127.0.0.1
GALOL_06__GALOLADDR=127.0.0.1
GALOL_07__GALOLADDR=127.0.0.1
GALOL_08__GALOLADDR=127.0.0.1

GALOL_01__CHANGEME=01
GALOL_02__CHANGEME=02
GALOL_03__CHANGEME=03
GALOL_04__CHANGEME=04
GALOL_05__CHANGEME=05
GALOL_06__CHANGEME=06
GALOL_07__CHANGEME=07
GALOL_08__CHANGEME=08"""
