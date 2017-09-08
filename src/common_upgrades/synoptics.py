import os

from xml.dom import minidom
from xml.parsers.expat import ExpatError

from src.local_logger import LocalLogger

SYNOPTICS_PATH = "configurations\synoptics"


class Synoptics(object):
    """
    Manipulate an instrument's synoptics
    """

    def _get_synoptic_files(self, logger):
        """
        Get a list of synoptic files associated with this instrument
        
        Returns:
            List(String): A list of file paths associated with instrument synoptics
        :return: 
        """
        try:
            return [file for file in os.listdir(SYNOPTICS_PATH) if file.endswith('.xml')]
        except WindowsError as e:
            logger.error("Unable to find the synoptics directory")
            return []


    def update_opi_paths(self, paths_to_update):
        """
        Update the paths to OPIs in all synoptics

        Args:
            paths_to_update (Iterable(Tuple)): The OPI paths that need updating

        Returns: 
            exit code 0 success; anything else fail

        """
        for file in self._get_synoptic_files():
            pass