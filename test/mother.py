"""Mother for test objects"""

from xml.dom import minidom

from src.file_access import FileAccess
from src.local_logger import LocalLogger


class LoggingStub(LocalLogger):
    """Stub for logging"""

    def __init__(self):
        self.log = []
        self.log_err = []
        self.config_base = "BASE"

    def error(self, message):
        self.log_err.append(message)

    def info(self, message):
        self.log.append(message)


class FileAccessStub(FileAccess):
    """Stub for file access"""

    SYNOPTIC_FILENAME = "synoptic_file"

    def __init__(self):
        self.config_base = None
        self.wrote_version = None
        self.write_filename = None
        self.write_file_contents = None
        self.write_file_dict = dict()
        self.existing_files = {}

    def write_version_number(self, version, filename):
        self.wrote_version = version

    def write_file(self, filename, file_contents, mode="w", file_full=False):
        self.write_filename = filename
        self.write_file_contents = "\n".join(file_contents)
        self.write_file_dict[self.write_filename] = self.write_file_contents

    def open_file(self, filename):
        return EXAMPLE_GLOBALS_FILE.splitlines()

    def write_xml_file(self, filename, xml):
        self.write_filename = filename
        self.write_file_contents = xml.toxml()
        self.write_file_dict[self.write_filename] = self.write_file_contents

    def open_xml_file(self, filename):
        return minidom.parseString("".join(self.open_file(filename)))

    def listdir(self, dir):
        return ["file1.xml", "README.txt", "file2.xml"]

    def remove_file(self, filename):
        pass

    def is_dir(self, path):
        return True

    def exists(self, path):
        if self.existing_files == {}:
            return False
        return self.existing_files[path]

    def get_config_files(self, file_type):
        yield file_type, self.open_xml_file(file_type)

    def get_synoptic_files(self):
        yield "synoptic_file", self.open_xml_file("synoptic_file")

    def get_file_paths(self, directory: str, extension: str = ""):
        yield directory + extension

    def file_contains(self, filename, string):
        return True


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
