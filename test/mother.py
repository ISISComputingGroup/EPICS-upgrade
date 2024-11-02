"""Mother for test objects"""

import typing
from typing import Generator, LiteralString
from xml.dom import minidom
from xml.dom.minidom import Document, Node

from src.file_access import FileAccess
from src.local_logger import LocalLogger


class LoggingStub(LocalLogger):
    """Stub for logging"""

    def __init__(self) -> None:
        self.log = []
        self.log_err = []
        self.config_base = "BASE"

    def error(self, message: str) -> None:
        self.log_err.append(message)

    def info(self, message: str) -> None:
        self.log.append(message)


class FileAccessStub(FileAccess):
    """Stub for file access"""

    SYNOPTIC_FILENAME = "synoptic_file"

    def __init__(self) -> None:
        self.config_base = None
        self.wrote_version = None
        self.write_filename = None
        self.write_file_contents = None
        self.write_file_dict = dict()
        self.existing_files = {}

    def write_version_number(self, version: str, filename: str) -> None:
        self.wrote_version = version

    def write_file(
        self, filename: str, file_contents: list[str], mode: str = "w", file_full: bool = False
    ) -> None:
        self.write_filename = filename
        self.write_file_contents = "\n".join(file_contents)
        self.write_file_dict[self.write_filename] = self.write_file_contents

    def open_file(self, filename: str) -> list[LiteralString]:
        return EXAMPLE_GLOBALS_FILE.splitlines()

    def write_xml_file(self, filename: str, xml: Node) -> None:
        self.write_filename = filename
        self.write_file_contents = xml.toxml()
        self.write_file_dict[self.write_filename] = self.write_file_contents

    def open_xml_file(self, filename: str) -> Document:
        return minidom.parseString("".join(self.open_file(filename)))

    def listdir(self, dir: str) -> list[str]:
        return ["file1.xml", "README.txt", "file2.xml"]

    def remove_file(self, filename: str) -> None:
        pass

    def is_dir(self, path: str) -> bool:
        return True

    def exists(self, path: str) -> bool:
        if self.existing_files == {}:
            return False
        return self.existing_files[path]

    def get_config_files(self, file_type: str) -> Generator[tuple[str, Document], typing.Any, None]:
        yield file_type, self.open_xml_file(file_type)

    def get_synoptic_files(self) -> Generator[tuple[str, Document], typing.Any, None]:
        yield "synoptic_file", self.open_xml_file("synoptic_file")

    def get_file_paths(
        self, directory: str, extension: str = ""
    ) -> Generator[str, typing.Any, None]:
        yield directory + extension

    def file_contains(self, filename: str, string: str) -> bool:
        return True


def create_xml_with_iocs(iocs: list) -> Document:
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
