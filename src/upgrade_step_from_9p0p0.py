import socket
from src.upgrade_step import UpgradeStep


class ChangeLETCollimatorCmd(UpgradeStep):
    """
    Change the LET/MERLIN collimator code to load in the new LET/MERLIN-specific db file.
    """

    def perform(self, file_access, logger):
        try:
            hostname = socket.gethostname()
            if hostname == "NDXLET" or hostname == "NDXMERLIN":
                file_access.write_file("configurations\\galil\\oscillatingCollimator.cmd", [
                    r'dbLoadRecords("$(MOTOREXT)/db/oscillatingCollimator_Let.db", "P=$(MYPVPREFIX)MOT:, O=$(COLLIMATOR_PV_PREFIX), M=MTR$(CNUM_PADDED)$(MNUM_PADDED), D=DMC$(CNUM_PADDED), AXIS=$(MOTOR_NUMBER), OTYP=$(OTYP=asynFloat64)")\n'],
                                       mode="a")

            return 0
        except Exception as e:
            logger.error("Unable to perform upgrade, caught error: {}".format(e))
            return 1


class RenameGalilMulCmd(UpgradeStep):
    """
    Rename all galilmul1.cmd -> galilmul01.cmd 
    """

    def perform(self, file_access, logger):
        try:
            file_access.rename_file("configurations\\galilmul\\galilmul1.cmd",
                                    "configurations\\galilmul\\galilmul01.cmd")
            file_access.rename_file("configurations\\galilmul\\galilmul2.cmd",
                                    "configurations\\galilmul\\galilmul02.cmd")

            return 0
        except Exception as e:
            pass


class ReEnableConfigCheckSans2d(UpgradeStep):
    """
    Reminder to turn on config checker
    """

    def perform(self, file_access, logger):
        hostname = socket.gethostname()
        if "SANS2D" in hostname:
            print("Renable the config check for SANS2D in https://github.com/ISISComputingGroup/InstrumentChecker "
                  " run_tests.py line 119(line might have changed) to proceed further")
            ans = input("Have you re-enabled the config checker for SANS2D?")
            while ans.lower() != "y":
                ans = input("Have you re-enabled the config checker for SANS2D?")
