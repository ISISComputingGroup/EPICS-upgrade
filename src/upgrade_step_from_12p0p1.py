# ruff: noqa: E501
import os
import socket

from src.file_access import FileAccess
from src.local_logger import LocalLogger
from src.upgrade_step import UpgradeStep


class AddOscCollimMovingIndicator(UpgradeStep):
    """Update oscillatingCollimator.cmd on LET and MERLIN to load stability check DB"""

    path = os.path.join("configurations", "galil", "oscillatingCollimator.cmd")
    new_lines = [
        "\n# load stability check DB",
        r'dbLoadRecords("$(UTILITIES)/db/check_stability.db", "P=$(MYPVPREFIX)MOT:,INP_VAL=$(MYPVPREFIX)MOT:DMC01:Galil0Bi5_STATUS,SP=$(MYPVPREFIX)MOT:DMC01:Galil0Bi5_STATUS,NSAMP=100,TOLERANCE=$(TOLERANCE=0)")\n',
    ]

    def perform(self, file_access: FileAccess, logger: LocalLogger) -> int:
        try:
            hostname = socket.gethostname()
            if hostname == "NDXLET" or hostname == "NDXMERLIN":
                file_access.write_file(self.path, self.new_lines, mode="a")
            return 0
        except Exception as e:
            logger.error("Unable to perform upgrade, caught error: {}".format(e))
            return 1
