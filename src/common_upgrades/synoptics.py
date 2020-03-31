class Synoptics(object):
    """
    Manipulate an instrument's synoptics
    """

    def __init__(self, file_access, logger):
        self.file_access = file_access
        self.logger = logger

    def update_opi_paths(self, paths_to_update):
        """
        Update the paths to OPIs in all synoptics

        Args:
            paths_to_update (Dict)): The OPI paths that need updating as a dictionary with keys as the OPI path and the
            value as the opi key from opi_info.xml

        Returns: 
            exit code 0 success; anything else fail

        """
        result = 0
        try:
            synoptics = self.file_access.get_synoptic_files()
        except OSError:
            result = -1
        else:
            for path, xml in synoptics:
                try:
                    self._update_opi_paths_in_file(path, xml, paths_to_update)
                except KeyError as e:
                    self.logger.error("Cannot upgrade synoptic {0}: {1}".format(path, e))
                    result = -2
                    break
        return result

    def _update_opi_paths_in_file(self, path, xml, paths_to_update):
        """
        Replaces an opi path with the relevant key in a given file
        
        Args:
            filename (String): file to update
            paths_to_update (Dict): A dictionary whose keys are OPI paths and values are the keys used by the IBEX gui
            
        Returns:
            None
        """
        for target_element in xml.getElementsByTagName("target"):
            name_element = target_element.getElementsByTagName("name")[0]
            name = name_element.firstChild.nodeValue
            if ".opi" in name:
                try:
                    name_element.firstChild.nodeValue = paths_to_update[name]
                    self.logger.info("OPI name '{0}' replaced with corresponding key '{1}'".
                                     format(name, paths_to_update[name]))
                except KeyError:
                    raise KeyError("Unknown opi path encountered, '{0}'. Replace with corresponding <key> from"
                                   " opi_info.xml".format(name))
        self.file_access.write_xml_file(path, xml)
