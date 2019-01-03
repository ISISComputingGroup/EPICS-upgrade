"""
Change to medium blob
"""

from src.common_upgrades.sql_utilities import run_sql
from src.upgrade_step import UpgradeStep


class UpgradeArchiveUseMediumBlob(UpgradeStep):
    """
    Upgrade the database to use medium blobs
    """

    def perform(self, file_access, logger):
        """
        Args:
            file_access (FileAccess): file access
            logger (LocalLogger): _logger

        Returns: exit code 0 success; anything else fail
        """
        return self.upgrade_archive_schema(logger)

    def upgrade_archive_schema(self, logger):
        """
        Flushes new privileges to the database.
        """
        try:
            run_sql(logger, "ALTER TABLE archive.sample MODIFY COLUMN array_val MEDIUMBLOB;")
            return 0
        except Exception as e:
            logger.error("Failed to update table: {}".format(e))
            return -1
