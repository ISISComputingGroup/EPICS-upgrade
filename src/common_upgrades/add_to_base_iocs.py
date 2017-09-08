from xml.dom import minidom
from xml.parsers.expat import ExpatError

from src.local_logger import LocalLogger

IOC_FILENAME = "configurations\components\_base\iocs.xml"


class AddToBaseIOCs():
    """
    Add the ioc autostart to _base ioc so that it autostarts
    """

    def __init__(self, ioc_to_add, add_after_ioc, xml_to_add):
        self._ioc_to_add = ioc_to_add
        self._add_after_ioc = add_after_ioc
        self._xml_to_add = xml_to_add

    def perform(self, file_access, logger):
        """
        Add the autostart of the given.

        Args:
            file_access (FileAccess): file access.
            logger (LocalLogger): logger.

        Returns: 
            exit code 0 success; anything else fail.

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

        modified_file_contents = self._add_ioc(ioc_file_contents, logger)
        logger.info("Adding {what} ioc to autostart in {0}.".format(IOC_FILENAME, what=self._ioc_to_add))

        if not self._check_final_file_contains_one_of_added_ioc(logger, modified_file_contents):
            return -3

        file_access.write_xml_file(IOC_FILENAME, modified_file_contents)
        return 0

    def _check_final_file_contains_one_of_added_ioc(self, logger, xml):
        """
        Check the file to make sure it now contains one and only one ioc added entry.
        
        Args:
            logger (Logger): Logger to write to.
            xml: XML to check.
            
        Returns:
            True if ok, else False.
        """
        ioc_names = []
        for ioc in xml.getElementsByTagName("ioc"):
            ioc_names.append(ioc.getAttribute("name"))

        node_count = ioc_names.count(self._ioc_to_add)
        if node_count != 1:
            # I can not see how to generate this error but it is here because it is important
            logger.error("IOC default component file now contains contains {0} {1} iocs it should contain exactly 1."
                         .format(node_count, self._ioc_to_add))
            return False
        return True

    def _check_prerequisits_for_file(self, xml, logger):
        """
        Check the file can be modified.
        
        Args:
            xml: XML to check
            logger (Logger): logger to write errors to.
            
        Returns:
            True if everything is ok, else False.
        """
        ioc_names = []
        for ioc in xml.getElementsByTagName("ioc"):
            ioc_names.append(ioc.getAttribute("name"))

        if ioc_names.count(self._ioc_to_add) != 0:
            logger.error("IOC default component file already contains {0} ioc.".format( self._ioc_to_add))
            return False

        node_count = ioc_names.count(self._add_after_ioc)
        if node_count != 1:
            logger.error("IOC default component file doesn't contain {0} {1} iocs it must contain exactly 1."
                         .format(node_count, self._add_after_ioc))
            return False
        return True

    def _add_ioc(self, ioc_xml, logger):
        """
        Add IOC entry after add after ioc specified if it exists.
        
        Args:
            ioc_xml: XML to add to.
            
        Returns:
            The XML with the added note.
        """
        for ioc in ioc_xml.getElementsByTagName("ioc"):
            if ioc.getAttribute("name") == self._add_after_ioc:
                new_ioc_node = minidom.parseString(self._xml_to_add).firstChild
                ioc_xml.firstChild.insertBefore(new_ioc_node, ioc.nextSibling)
                # add some formatting to make it look nice
                ioc_xml.firstChild.insertBefore(ioc_xml.createTextNode("\n    "), new_ioc_node)
                return ioc_xml

        logger.error("Could not find {0} ioc in file so no {1} ioc added.".format(
            self._add_after_ioc, self._ioc_to_add))
        return ioc_xml
