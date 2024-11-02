import os
from xml.dom.minidom import Text

from src.file_access import FileAccess
from src.local_logger import LocalLogger
from src.upgrade_step import UpgradeStep


class RemoveReflDeviceScreen(UpgradeStep):
    """Remove reflectometry device screen from all configs and components"""

    path = os.path.join("configurations", "devices", "screens.xml")

    def perform(self, file_access: FileAccess, logger: LocalLogger) -> int:
        if file_access.exists(self.path):
            xml_tree = file_access.open_xml_file(self.path)
            keys = xml_tree.getElementsByTagName("key")
            for key in keys:
                device = key.parentNode
                assert key.firstChild is not None
                if isinstance(key.firstChild, Text) and key.firstChild.data == "Reflectometry OPI":
                    device.parentNode.removeChild(device)
            file_access.write_xml_file(self.path, xml_tree)

        return 0
