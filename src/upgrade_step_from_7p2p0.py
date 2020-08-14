import socket
import os

from src.common_upgrades.change_macros_in_xml import ChangeMacrosInXML
from src.common_upgrades.utils.macro import Macro
from src.upgrade_step import UpgradeStep


class IgnoreRcpttSynoptics(UpgradeStep):
    """
    Adds "rcptt_*" files to .gitignore, so that test synoptics are no longer committed.
    """

    ERROR_CODE = -1
    SUCCESS_CODE = 0
    file_name = ".gitignore"
    text_content = ['*.py[co]',
                    'rcptt_*/',
                    'rcptt_*',
                    '*.swp',
                    '*~',
                    '.idea/',
                    '.project/']

    def perform(self, file_access, logger):
        """
        Perform the upgrade step
        Args:
            file_access (FileAccess): file access
            logger (LocalLogger): logger

        Returns: exit code 0 success; anything else fail

        """
        try:
            logger.info("Starting step ...")

            if not file_access.exists(self.file_name):
                # In case there isn't a .gitignore file, write new one
                print(".gitignore not found at " + self.file_name + ", making a new .gitignore")
                file_access.write_file(self.file_name, self.text_content, "w")
            else:
                # If existing .gitignore file is found, append to it
                if not file_access.line_exists(self.file_name, "rcptt_*\n"):
                    file_access.write_file(self.file_name, ["rcptt_*"], "a")

            logger.info("Step completed")
            return self.SUCCESS_CODE

        except Exception as e:
            logger.error("Unable to perform upgrade, caught error: {}".format(e))
            return self.ERROR_CODE
