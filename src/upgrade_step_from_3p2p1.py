from src.upgrade_step import UpgradeStep
from file_access import FileAccess
import xml.etree.ElementTree as ET
from local_logger import LocalLogger

IOC_FILENAME = "configurations\components\_base\iocs.xml"

XML_TO_ADD = """\
<ioc autostart="true" name="ALARM" restart="true" simlevel="none">
    <macros/>
    <pvs/>
    <pvsets/>
</ioc>"""


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
            ioc_file_contents = file_access.open_file(filename=IOC_FILENAME)
        except IOError:
            logger.error("Can not find file to modify in config.")
            logger.error("Filename in configuration: {0}".format(IOC_FILENAME))
            return -1

        if not self._check_prerequisits_for_file(ioc_file_contents, logger):
            return -2

        modified_file_contents = self._add_alarm_ioc(ioc_file_contents)
        logger.info("Adding ALARM ioc to autostart in {0}.".format(IOC_FILENAME))

        if not self._check_final_file_contains_alarm_ioc(logger, modified_file_contents):
            return -3

        file_access.write_file(IOC_FILENAME, modified_file_contents)
        return 0

    def _check_final_file_contains_alarm_ioc(self, logger, modified_file_contents):
        et = ET.fromstringlist(modified_file_contents)
        ns = {"ioc_ns": 'http://epics.isis.rl.ac.uk/schema/iocs/1.0'}
        node_count = len(et.findall(r".//ioc_ns:ioc[@name='ALARM']", ns))
        if node_count != 1:
            # I can not see how to generate this error but it is here because it is important
            logger.error("IOC default component file now contains contains {0} ALARM iocs it should contain exactly 1."
                         .format(node_count))
            return False
        return True

    def _check_prerequisits_for_file(self, ioc_file, logger):
        try:
            et = ET.fromstringlist(ioc_file)
        except ET.ParseError:
            logger.error("Can not parse the file as xml. File starts '{0}'".format(ioc_file[0:10]))
            return False
        ns = {"ioc_ns": 'http://epics.isis.rl.ac.uk/schema/iocs/1.0'}
        node_count = len(et.findall(r".//ioc_ns:ioc[@name='ALARM']", ns))
        if node_count != 0:
            logger.error("IOC default component file already contains ALARM ioc.")
            return False
        node_count = len(et.findall(r".//ioc_ns:ioc[@name='ISISDAE_01']", ns))
        if node_count != 1:
            logger.error("IOC default component file doesn't contain {0} ISISDAE_01 iocs it must contain exactly 1."
                         .format(node_count))
            return False
        return True

    def _add_alarm_ioc(self, ioc_file):
        modified_file_contents = []
        add_after_next_ioc_element_close = False
        for line in ioc_file:
            modified_file_contents.append(line)
            if line.strip().startswith("<ioc") and '"ISISDAE_01"' in line:
                add_after_next_ioc_element_close = True

            if add_after_next_ioc_element_close and line.strip().startswith("</ioc>"):
                indent = line.find("</ioc>")
                for xml_line_to_add in XML_TO_ADD.split("\n"):
                    modified_file_contents.append("{0}{1}".format(" " * indent, xml_line_to_add))
                add_after_next_ioc_element_close = False
        return modified_file_contents
