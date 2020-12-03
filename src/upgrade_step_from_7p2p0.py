import os

from src.upgrade_step import UpgradeStep
from src.common_upgrades.change_pvs_in_xml import ChangePVsInXML
from src.common_upgrades.utils.constants import MOTION_SET_POINTS_FOLDER
from src.file_access import CachingFileAccess
from future.builtins import input

ERROR_CODE = -1
SUCCESS_CODE = 0


class IgnoreRcpttSynoptics(UpgradeStep):
    """
    Adds "rcptt_*" files to .gitignore, so that test synoptics are no longer committed.
    """

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
            return SUCCESS_CODE

        except Exception as e:
            logger.error("Unable to perform upgrade, caught error: {}".format(e))
            return ERROR_CODE


class UpgradeMotionSetPoints(UpgradeStep):
    """
    Changes blocks to point at renamed PVs. Warns about changed setup.
    """

    def perform(self, file_access, logger):
        """
        Perform the upgrade step
        Args:
            file_access (FileAccess): file access
            logger (LocalLogger): logger

        Returns: exit code 0 success; anything else fail
        """
        try:
            logger.info("Changing motion set point PVs")

            with CachingFileAccess(file_access):

                changer = ChangePVsInXML(file_access, logger)

                changer.change_pv_name("COORD1", "COORD0")
                changer.change_pv_name("COORD2", "COORD1")

                changer.change_pv_name("COORD0:NO_OFFSET", "COORD0:NO_OFF")
                changer.change_pv_name("COORD1:NO_OFFSET", "COORD1:NO_OFF")

                changer.change_pv_name("COORD0:RBV:OFFSET", "COORD0:RBV:OFF")
                changer.change_pv_name("COORD1:RBV:OFFSET", "COORD1:RBV:OFF")

                changer.change_pv_name("COORD0:LOOKUP:SET:RBV", "COORD0:SET:RBV")
                changer.change_pv_name("COORD1:LOOKUP:SET:RBV", "COORD1:SET:RBV")

                if file_access.exists(MOTION_SET_POINTS_FOLDER):
                    print("")
                    print(
                        "{} folder exists. Motion set point configuration has changed significantly"
                        " in this version and must be manually fixed".format(MOTION_SET_POINTS_FOLDER)
                    )
                    print(
                        "See https://github.com/ISISComputingGroup/ibex_developers_manual/"
                        "wiki/Motion-Set-points#upgrading-from-720 for how to do this"
                    )
                    input("Press any key to confirm this is done.")
                    print("")

                # CoordX:MTR is gone, hard to automatically replace so just raise as issue
                if changer.get_number_of_instances_of_pv(["COORD0:MTR", "COORD1:MTR"]) > 0:
                    print("The PV COORDX:MTR has been found in a config/synoptic but no longer exists")
                    print("Manually replace with a reference to the underlying axis and rerun the upgrade")
                    raise RuntimeError("Underlying motor references")

            return SUCCESS_CODE

        except Exception as e:
            logger.error("Unable to perform upgrade, caught error: {}".format(e))
            return ERROR_CODE


class ChangeReflOPITarget(UpgradeStep):

    REFL_OPI_TARGET_OLD = "Reflectometry Front Panel"
    REFL_OPI_TARGET_NEW = "Reflectometry OPI"

    def perform(self, file_access, logger):
        """
        Perform the upgrade step
        Args:
            file_access (FileAccess): file access
            logger (LocalLogger): logger

        Returns: exit code 0 success; anything else fail

        """

        try:
            logger.info("Changing OPI target for reflectometry device screen")
            configs_dir = os.getenv("ICPCONFIGROOT")
            device_screens_file = os.path.join(configs_dir, "devices", "screens.xml")

            if file_access.exists(device_screens_file):
                try:
                    content = file_access.open_file(device_screens_file)
                    content = [line.replace(self.REFL_OPI_TARGET_OLD, self.REFL_OPI_TARGET_NEW) for line in content]
                    file_access.write_file(device_screens_file, content)
                except OSError:
                    return ERROR_CODE

            logger.info("Step completed")
            return SUCCESS_CODE

        except Exception as e:
            logger.error("Unable to perform upgrade, caught error: {}".format(e))
            return ERROR_CODE