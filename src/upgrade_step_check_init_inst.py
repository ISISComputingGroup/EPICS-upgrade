from src.file_access import FileAccess
from src.local_logger import LocalLogger
from src.upgrade_step import UpgradeStep
from src.common_upgrades.utils.constants import CONFIG_ROOT
import os
# from io import open


class UpgradeStepCheckInitInst(UpgradeStep):
    """
    An upgrade step to check if the instrument uses the old style of loading in pre and post cmd.
    This old style is via API.__localmod in init_<inst>.py in the Instrument/Settings/config/NDX<inst>/Python folder. 
    """

    def search_files(self, files, root, file_access):
        """
        Search files from a root folder for pre and post cmd methods.

        Args:
            files (List[str]): The names of the files in the root directory.
            root (str): The root directory of the files.
            file_access (FileAccess): file access
        
        Returns: 0 if pre and post cmd methods in old style are not present; error message if they are.
        """
        for file_name in files:
            if file_name.startswith("init_"):
                search_file = open(os.path.join(root, file_name))
                search_file_contents = search_file.read()
                if "precmd" in search_file_contents or "postcmd" in search_file_contents:
                    return "Pre or post cmd methods found in {} convert to new style of inserting these methods".format(search_file.name)
        return 0

    def search_folder(self, folder, file_access):
        """
        Recursively search folders for the search string.

        Args:
            folder (str): The folder to search through.
            file_access (FileAccess): file access
        
        Returns: 0 if pre and post cmd methods in old style are not present; error message if they are.
        """
        root, dirs, files = os.walk(folder)
        # Search files for pre and post cmd methods
        file_search_return = self.search_files(files, root, file_access)
        if file_search_return != 0:
            return file_search_return
        # Recurse to search in further directories
        for directory in dirs:
            directories_search_return = self.search_folder(os.path.join(root, directory), file_access)
            if directories_search_return != 0:
                return directories_search_return
        return 0


    def perform(self, file_access, logger):
        """
        Check if file exists and if the file includes pre and post cmd methods. 

        Args:
            file_access (FileAccess): file access
            logger (LocalLogger): logger

        Returns: 0 if pre and post cmd methods in old style are not present; error message if they are.

        """
        return self.search_folder(os.path.join(CONFIG_ROOT, "Python"), file_access)
        
