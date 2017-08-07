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
        self.write_file_contents = contents

    def open_file(self, filename):
        pass

    def write_xml_file(self, filename, xml):
        self.write_filename = filename
        self.write_file_contents = xml.toxml()

    def open_xml_file(self, filename):
        return minidom.parseString(self.open_file(filename))

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
