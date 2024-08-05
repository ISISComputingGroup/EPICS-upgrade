import os

from src.common_upgrades.utils.constants import SCRIPTS_ROOT
from src.upgrade_step import UpgradeStep


class UpgradeStepCheckInitInst(UpgradeStep):
    """An upgrade step to check if the instrument uses the old style of loading in pre and post cmd.
    This old style is via API.__localmod in init_<inst>.py in the Instrument/Settings/config/NDX<inst>/Python folder.
    """

    def search_files(self, files, root, file_access):
        """Search files from a root folder for pre and post cmd methods.

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
                    return (
                        "Pre or post cmd methods found in {} these will now no longer be hooked into the command. Please ensure they are hooked using the new style of inserting these methods, "
                        "see https://github.com/ISISComputingGroup/ibex_user_manual/wiki/Pre-and-Post-Command-Hooks".format(
                            search_file.name
                        )
                    )
        return 0

    def search_folder(self, folder, file_access):
        """Search folders for the search string.

        Args:
            folder (str): The folder to search through.
            file_access (FileAccess): file access

        Returns: 0 if pre and post cmd methods in old style are not present; error message if they are.
        """
        file_returns = ""
        for root, _, files in os.walk(folder):
            # Search files for pre and post cmd methods
            file_search_return = self.search_files(files, root, file_access)
            if file_search_return != 0:
                file_returns += "{}\n".format(file_search_return)
        return 0 if file_returns == "" else file_returns

    def perform(self, file_access, logger):
        """Check if file exists and if the file includes pre and post cmd methods.

        Args:
            file_access (FileAccess): file access
            logger (LocalLogger): logger

        Returns: 0 if pre and post cmd methods in old style are not present; error message if they are.

        """
        return self.search_folder(SCRIPTS_ROOT, file_access)
