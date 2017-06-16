import os

from src.upgrade_step import UpgradeStep
from file_access import FileAccess
from xml.dom import minidom
from xml.parsers.expat import ExpatError

from local_logger import LocalLogger

IOC_FILENAME = "configurations\components\_base\iocs.xml"

XML_TO_ADD = """\
    <ioc autostart="true" name="ALARM" restart="true" simlevel="none">
        <macros/>
        <pvs/>
        <pvsets/>
    </ioc>
"""


class UpgradeStepFrom3p2p1(UpgradeStep):
    """
    Add the Alarm server to the _base ioc so that it autostarts
    """

    def perform(self, file_access, logger):
        """
        Perform the upgrade step from version 0 to 1

        Args:
            file_access (FileAccess): file access
            logger (LocalLogger): logger

        Returns: exit code 0 success; anything else fail

        """
        try:
            ioc_file_contents = file_access.open_xml_file(filename=IOC_FILENAME)
        except IOError:
            logger.error("Can not find file to modify in config.")
            logger.error("Filename in configuration: {0}".format(IOC_FILENAME))
            return -1
        except ExpatError as ex:
            logger.error("IOC file appears not be valid XML, error '{0}'".format(ex))
            logger.error("Filename in configuration: {0}".format(IOC_FILENAME))
            return -1

        if not self._check_prerequisits_for_file(ioc_file_contents, logger):
            return -2

        modified_file_contents = self._add_alarm_ioc(ioc_file_contents, logger)
        logger.info("Adding ALARM ioc to autostart in {0}.".format(IOC_FILENAME))

        if not self._check_final_file_contains_one_alarm_ioc(logger, modified_file_contents):
            return -3

        file_access.write_xml_file(IOC_FILENAME, modified_file_contents)
        return 0

    def _check_final_file_contains_one_alarm_ioc(self, logger, xml):
        """
        Check the file to make sure it now contains one and only one alarm ioc entry
        :param logger: logger to write to
        :param xml: xml to check
        :return: True if ok, False otherwise
        """
        ioc_names = []
        for ioc in xml.getElementsByTagName("ioc"):
            ioc_names.append(ioc.getAttribute("name"))

        node_count = ioc_names.count("ALARM")
        if node_count != 1:
            # I can not see how to generate this error but it is here because it is important
            logger.error("IOC default component file now contains contains {0} ALARM iocs it should contain exactly 1."
                         .format(node_count))
            return False
        return True

    def _check_prerequisits_for_file(self, xml, logger):
        """
        Check the file can be modified
        :param xml: xml to check
        :param logger: logger to write errors to
        :return: True everything is ok; False on error
        """
        ioc_names = []
        for ioc in xml.getElementsByTagName("ioc"):
            ioc_names.append(ioc.getAttribute("name"))

        if ioc_names.count("ALARM") != 0:
            logger.error("IOC default component file already contains ALARM ioc.")
            return False

        node_count = ioc_names.count("ISISDAE_01")
        if node_count != 1:
            logger.error("IOC default component file doesn't contain {0} ISISDAE_01 iocs it must contain exactly 1."
                         .format(node_count))
            return False
        return True

    def _add_alarm_ioc(self, ioc_xml, logger):
        """
        Add Alarm IOC entry after ISISDAE_01 if it exists
        :param ioc_xml: xml to add to
        :return: the xml with the added node
        """
        for ioc in ioc_xml.getElementsByTagName("ioc"):
            if ioc.getAttribute("name") == "ISISDAE_01":
                alarm_ioc_node = minidom.parseString(XML_TO_ADD).firstChild
                ioc_xml.firstChild.insertBefore(alarm_ioc_node, ioc.nextSibling)
                # add some formatting to make it look nice
                ioc_xml.firstChild.insertBefore(ioc_xml.createTextNode("\n    "), alarm_ioc_node)
                return ioc_xml

        logger.error("Could not find ISISDAE_01 ioc in file so no alarm ioc added.")
        return ioc_xml
