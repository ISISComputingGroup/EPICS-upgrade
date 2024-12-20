import os

from src.common_upgrades.sql_utilities import SqlConnection, run_sql_file
from src.common_upgrades.utils.constants import EPICS_ROOT
from src.file_access import FileAccess
from src.local_logger import LocalLogger
from src.upgrade_step import UpgradeStep


class UpgradeFrom12p0p2(UpgradeStep):
    """add sql tables for JMS2RDB"""

    def perform(self, file_access: FileAccess, logger: LocalLogger) -> int:
        # add JMS2RDB Tables
        try:
            file = os.path.join(EPICS_ROOT, "CSS", "master", "AlarmJMS2RDB", "MySQL-Log-DDL.sql")
            logger.info("Updating JMS2RDB schema")
            with SqlConnection():
                return run_sql_file(logger, file)
        except Exception as e:
            logger.error("Unable to perform upgrade, caught error: {}".format(e))
            return 1
