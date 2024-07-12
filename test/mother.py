"""Mother for test objects
"""

from xml.dom import minidom


class LoggingStub(object):
    """Stub for logging
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
    """Stub for file access
    """

    SYNOPTIC_FILENAME = "synoptic_file"

    def __init__(self):
        self.config_base = None
        self.wrote_version = None
        self.write_filename = None
        self.write_file_contents = None
        self.write_file_dict = dict()
        self.existing_files = None

    def write_version_number(self, version, filename):
        self.wrote_version = version

    def write_file(self, filename, contents):
        self.write_filename = filename
        self.write_file_contents = "\n".join(contents)
        self.write_file_dict[self.write_filename] = self.write_file_contents

    def open_file(self, filename):
        return EXAMPLE_GLOBALS_FILE.splitlines()

    def write_xml_file(self, filename, xml):
        self.write_filename = filename
        self.write_file_contents = xml.toxml()
        self.write_file_dict[self.write_filename] = self.write_file_contents

    def open_xml_file(self, filename):
        return minidom.parseString(self.open_file(filename))

    def listdir(self, dir):
        return ["file1.xml", "README.txt", "file2.xml"]

    def remove_file(self, filename):
        pass

    def is_dir(self, path):
        pass

    def exists(self, path):
        if self.existing_files is None:
            return False
        return self.existing_files[path]

    def get_config_files(self, type):
        yield type, self.open_xml_file(type)

    def get_synoptic_files(self):
        yield "synoptic_file", self.open_xml_file("synoptic_file")


def create_xml_with_iocs(iocs):
    """Args:
        iocs (list): A list of IOC names
    Returns:
        str: xml containing the supplied IOCs
    """
    doc = minidom.Document()
    top = doc.createElement("iocs")
    for ioc in iocs:
        child = doc.createElement("ioc")
        child.setAttribute("name", ioc)
        top.appendChild(child)
    doc.appendChild(top)
    return doc


EXAMPLE_GLOBALS_FILE = """
# IOC specific macros
BINS_01__PLCIP=127.0.0.1
GALIL_01__GALILADDR=127.0.0.1
GALIL_02__GALILADDR=127.0.0.1
GALIL_03__GALILADDR=127.0.0.1
GALIL_04__GALILADDR=127.0.0.1
GALIL_05__GALILADDR=127.0.0.1
GALIL_06__GALILADDR=127.0.0.1
GALIL_07__GALILADDR=127.0.0.1
GALIL_08__GALILADDR=127.0.0.1

GALIL_01__CHANGEME=01
GALIL_02__CHANGEME=02
GALIL_03__CHANGEME=03
GALIL_04__CHANGEME=04
GALIL_05__CHANGEME=05
GALIL_06__CHANGEME=06
GALIL_07__CHANGEME=07
GALIL_08__CHANGEME=08"""
