from src.upgrade_step import UpgradeStep


import xml.etree.ElementTree as ET
import os

SCHEMA_PATH = "http://epics.isis.rl.ac.uk/schema/"
IOC_SCHEMA = "iocs/1.0"


class ChangeConfigurationSchema(UpgradeStep):
    """
    Step that changes the PVs associated with the jawsmanager as they have been renamed.
    """

    def perform(self, file_access, logger):

        ET.register_namespace('', SCHEMA_PATH + IOC_SCHEMA)

        configs_dir = os.getenv("ICPCONFIGROOT")

        for subdir in ["configurations", "components"]:
            joined_dir = os.path.join(configs_dir, subdir)
            for config_name in [p for p in os.listdir(joined_dir) if os.path.isdir(os.path.join(joined_dir, p))]:

                filename = os.path.join(joined_dir, config_name, "iocs.xml")
                logger.info("Upgrading {} to new schema".format(filename))

                et = ET.parse(filename)
                root = et.getroot()

                root.attrib["xmlns:ioc"] = SCHEMA_PATH + IOC_SCHEMA
                root.attrib["xmlns:xi"] = "http://www.w3.org/2001/XInclude"

                for ioc in root.iter("{{{}}}ioc".format(SCHEMA_PATH + IOC_SCHEMA)):
                    ioc.attrib["remotePvPrefix"] = ""

                et.write(filename)

        return 0
