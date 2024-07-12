import os

from src.upgrade_step import UpgradeStep


class RemoveReflDeviceScreen(UpgradeStep):
    """Remove reflectometry device screen from all configs and components
    """

    path = os.path.join("configurations", "devices", "screens.xml")

    def perform(self, file_access, logger):
        if file_access.exists(self.path):
            xml_tree = file_access.open_xml_file(self.path)
            keys = xml_tree.getElementsByTagName("key")
            for key in keys:
                device = key.parentNode
                if key.firstChild.data == "Reflectometry OPI":
                    device.parentNode.removeChild(device)
            file_access.write_xml_file(self.path, xml_tree)

        return 0
