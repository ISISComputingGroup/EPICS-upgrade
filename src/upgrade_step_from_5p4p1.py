import os
from src.upgrade_step import UpgradeStep
import xml.etree.ElementTree as ET
from xml.dom import minidom
from lxml import etree


class BannerXMLNotValidException(Exception):

    def __init__(self, message):
        super(BannerXMLNotValidException, self).__init__(self, message)


class UpgradeBannerXml(UpgradeStep):
    """
    Upgrades banner.xml to work with the new banner customsation
    """

    def validate(self, xml_filepath, schema_filename):
        """
        Validates an xml against an xsd

        :param xml_filepath: The path to the xml
        :param schema_filename: The name of the xsd file assumed to be in the src/schemas folder
        :rtype: bool
        :return: Whether the xml is valid against the schema
        """
        schema_file = open(os.path.join(os.path.join("src", "schemas"), schema_filename), 'r')
        schema_raw = etree.XML(schema_file.read())
        schema = etree.XMLSchema(schema_raw)
        xml = etree.parse(xml_filepath)
        return schema.validate(xml)

    def perform(self, file_access, logger):
        """
        Perform the upgrade step

        Args:
            file_access (FileAccess): file access
            logger (LocalLogger): logger

        Returns: exit code 0 success; anything else fail

        """
        try:
            complete_new = '''<?xml version="1.0" ?>
            <banner xmlns="http://epics.isis.rl.ac.uk/schema/banner/1.0" xmlns:ioc="http://www.w3.org/2001/XMLSchema-instance" xmlns:xi="http://www.w3.org/2001/XInclude">
              <items>
                <item>
                  <button>
                    <name>Stop All Motors</name>
                    <pv>CS:MOT:STOP:ALL</pv>
                    <local>true</local>
                    <pvValue>1</pvValue>
                    <textColour>#000000</textColour>
                    <buttonColour>#e0e0e0</buttonColour>
                    <fontSize>9</fontSize>
                    <width>100</width>
                    <height>25</height>
                  </button>
                </item>
                <item>
                  <display>
                    <name>Motors are</name>
                    <pv>CS:MOT:MOVING:STR</pv>
                    <local>true</local>
                    <width>170</width>
                  </display>
                </item>
                <item>
                  <display>
                    <name>DAE Simulation mode</name>
                    <pv>DAE:SIM_MODE</pv>
                    <local>true</local>
                    <width>250</width>
                  </display>
                </item>
                <item>
                  <display>
                    <name>Manager mode</name>
                    <pv>CS:MANAGER</pv>
                    <local>true</local>
                    <width>250</width>
                  </display>
                </item>
                <item>
                  <display>
                    <name>Config</name>
                    <pv>CS:BLOCKSERVER:CURR_CONFIG_NAME</pv>
                    <local>true</local>
                    <width>360</width>
                  </display>
                </item>
              </items>
            </banner>
            '''
            motor_button = '''    <item>
                  <button>
                    <name>Stop All Motors</name>
                    <pv>CS:MOT:STOP:ALL</pv>
                    <local>true</local>
                    <pvValue>1</pvValue>
                    <textColour>#000000</textColour>
                    <buttonColour>#e0e0e0</buttonColour>
                    <fontSize>9</fontSize>
                    <width>100</width>
                    <height>25</height>
                  </button>
                </item>
            '''
            motor_display = '''    <item>
                  <display>
                    <name>Motors are</name>
                    <pv>CS:MOT:MOVING:STR</pv>
                    <local>true</local>
                    <width>170</width>
                  </display>
                </item>
            '''
            config_display = '''<item>
                  <display>
                    <name>Config</name>
                    <pv>CS:BLOCKSERVER:CURR_CONFIG_NAME</pv>
                    <local>true</local>
                    <width>360</width>
                  </display>
                </item>
            '''
            banner_path = os.path.join(file_access.config_base, os.path.join("configurations", "banner.xml"))

            motor_button = ET.fromstring(
                motor_button.replace(" ", "").replace("\n", "").replace("StopAllMotors", "Stop All Motors"))
            motor_display = ET.fromstring(
                motor_display.replace(" ", "").replace("\n", "").replace("Motorsare", "Motors are"))
            config_display = ET.fromstring(config_display.replace(" ", "").replace("\n", ""))
            if not os.path.exists(banner_path):
                # In case there isn't a banner xml
                print("banner.xml not found at " + banner_path + ", making a new banner.xml")
                with open(banner_path, "w") as f:
                    f.write(complete_new)
            elif self.validate(banner_path, "new_banner.xsd"):
                # If the banner matches the new schema it has already been updated so do nothing
                # If the banner is also valid against the old schema this is fine, but print a warning
                if self.validate(banner_path, "old_banner.xsd"):
                    print("Warning: schema valid against both old and new schema")
            elif not self.validate(banner_path, "old_banner.xsd"):
                print("Cannot upgrade banner.xml to new schema as it is not valid against the old schema")
                raise BannerXMLNotValidException("banner.xml not valid against old schema")
            else:
                # Parse the old banner.xml
                tree = ET.parse(banner_path)

                # Create a new tree and copy over from the old, adding width data
                new_root = ET.Element('banner')
                new_root.attrib["xmlns"] = "http://epics.isis.rl.ac.uk/schema/banner/1.0"
                new_root.attrib["xmlns:ioc"] = "http://www.w3.org/2001/XMLSchema-instance"
                new_root.attrib["xmlns:xi"] = "http://www.w3.org/2001/XInclude"

                new_items = ET.SubElement(new_root, "items")
                new_items.append(motor_button)
                new_items.append(motor_display)
                for items in tree.getroot():
                    for item in items:
                        new_item = ET.SubElement(new_items, "item")
                        new_display = ET.SubElement(new_item, "display")
                        for element in item:
                            ET.SubElement(new_display, element.tag.split("}", 1)[1]).text = element.text
                        ET.SubElement(new_display, "width").text = "250"

                new_items.append(config_display)

                # Get pretty xml using minidom and write to file
                xmlstr = minidom.parseString(ET.tostring(new_root)).toprettyxml(indent="  ")
                with open(banner_path, "w") as f:
                    f.write(xmlstr)
            return 0

        except Exception as e:
            print(e)
            return -1
