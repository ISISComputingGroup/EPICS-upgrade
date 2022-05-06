import socket
from src.upgrade_step import UpgradeStep

class RemoveReflDeviceScreen(UpgradeStep):
    """
    Remove reflectometry device screen from all configs and components
    """

    def perform(self, file_access, logger):
        path = "configurations\\devices\\screens.xml"
        xml_tree = file_access.open_xml_file(path)
        keys = xml_tree.getElementsByTagName("key")
        for key in keys:
            device = key.parentNode
            if key.firstChild.data == "Reflectometry OPI":
                device.parentNode.removeChild(device)
        file_access.write_xml_file(path, xml_tree)

        return 0
