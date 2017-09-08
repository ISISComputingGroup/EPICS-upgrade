import os

SYNOPTICS_PATH = "configurations\synoptics"


class Synoptics(object):
    """
    Manipulate an instrument's synoptics
    """

    @staticmethod
    def _get_synoptic_files(logger):
        """
        Get a list of synoptic files associated with this instrument
        
        Returns:
            List(String): A list of file paths associated with instrument synoptics
        """
        try:
            return [file for file in os.listdir(SYNOPTICS_PATH) if file.endswith('.xml')]
        except WindowsError as e:
            logger.error("Unable to find the synoptics directory")
            return []

    def update_opi_paths(self, file_access, logger, paths_to_update):
        """
        Update the paths to OPIs in all synoptics

        Args:
            paths_to_update (Dict)): The OPI paths that need updating as a dictionary with keys as the OPI path and the
            value as the opi key from opi_info.xml

        Returns: 
            exit code 0 success; anything else fail

        """
        for filename in Synoptics._get_synoptic_files():
            xml = file_access.open_xml_file(filename)
            for target_element in xml.findElementsByTag("target"):
                name_element = target_element.findElementsByTag("name")[0]
                name = name_element.firstChild.nodeValue
                if ".opi" in name:
                    try:
                        name_element.firstChild.nodeValue = paths_to_update[name]
                    except:
                        return -1
            file_access.write_xml_file(filename, xml)
        return 0
