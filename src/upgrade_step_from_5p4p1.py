import os
from src.upgrade_step import UpgradeStep
import xml.etree.ElementTree as ET
from xml.dom import minidom

class UpgradeBannerXml(UpgradeStep):
    """
    Upgrades banner.xml to work with the new banner customsation
    """

    def perform(self, file_access, logger):
        """
        Perform the upgrade step

        Args:
            file_access (FileAccess): file access
            logger (LocalLogger): logger

        Returns: exit code 0 success; anything else fail

        """
        try:
            path = os.path.join(file_access.config_base, os.path.join("configurations", "banner.xml"))
            complete_new = '<?xml version="1.0" ?>\n<banner xmlns="http://epics.isis.rl.ac.uk/schema/banner/1.0" xmlns:blk="http://epics.isis.rl.ac.uk/schema/banner/1.0" xmlns:xi="http://www.w3.org/2001/XInclude">\n  <items>\n    <item>\n      <button>\n        <name>Stop All Motors</name>\n        <pv>CS:MOT:STOP:ALL</pv>\n        <local>true</local>\n        <pvValue>1</pvValue>\n        <textColour>#000000</textColour>\n        <buttonColour>#e0e0e0</buttonColour>\n        <fontSize>9</fontSize>\n        <width>100</width>\n        <height>25</height>\n      </button>\n    </item>\n    <item>\n      <display>\n        <name>Motors are</name>\n        <pv>CS:MOT:MOVING:STR</pv>\n        <local>true</local>\n        <width>170</width>\n      </display>\n    </item>\n    <item>\n      <display>\n        <name>DAE Simulation mode</name>\n        <pv>DAE:SIM_MODE</pv>\n        <local>true</local>\n        <width>250</width>\n      </display>\n    </item>\n    <item>\n      <display>\n        <name>Manager mode</name>\n        <pv>CS:MANAGER</pv>\n        <local>true</local>\n        <width>250</width>\n      </display>\n    </item>\n  </items>\n</banner>'
            line_2 = '<banner xmlns="http://epics.isis.rl.ac.uk/schema/banner/1.0" xmlns:blk="http://epics.isis.rl.ac.uk/schema/banner/1.0" xmlns:xi="http://www.w3.org/2001/XInclude">\n'
            motor_xml = '    <item>\n      <button>\n        <name>Stop All Motors</name>\n        <pv>CS:MOT:STOP:ALL</pv>\n        <local>true</local>\n        <pvValue>1</pvValue>\n        <textColour>#000000</textColour>\n        <buttonColour>#e0e0e0</buttonColour>\n        <fontSize>9</fontSize>\n        <width>100</width>\n        <height>25</height>\n      </button>\n    </item>\n    <item>\n      <display>\n        <name>Motors are</name>\n        <pv>CS:MOT:MOVING:STR</pv>\n        <local>true</local>\n        <width>170</width>\n      </display>\n    </item>\n'

            ET.register_namespace("", "http://epics.isis.rl.ac.uk/schema/banner/1.0")

            try:
                # Parse the old banner.xml
                tree = ET.parse(path)

                # Create a new tree and copy over from the old, adding width data
                new_root = ET.Element('banner')
                new_items = ET.SubElement(new_root, "items")
                for items in tree.getroot():
                    for item in items:
                        new_item = ET.SubElement(new_items, "item")
                        new_display = ET.SubElement(new_item, "display")
                        for element in item:
                            ET.SubElement(new_display, element.tag).text = element.text
                        ET.SubElement(new_display, "width").text = "250"

                # Get pretty xml using minidom and write to file
                xmlstr = minidom.parseString(ET.tostring(new_root)).toprettyxml(indent="  ")
                with open(path, "w") as f:
                    f.write(xmlstr)

                with open(path, 'r') as f:
                    lines = f.readlines()

                # Replace line 2 (not sure if these namespaces are used for anything, except the first, but keeping them anyway)
                lines[1] = line_2

                # Insert the xml for the motor status and button
                lines.insert(3, motor_xml)

                with open(path, 'w') as file:
                    file.writelines(lines)

            except IOError:
                # In case there isn't a banner xml
                with open(path, "w") as f:
                    f.write(complete_new)

        except Exception:
            return -1
