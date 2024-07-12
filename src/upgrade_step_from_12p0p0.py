import os
import re

from src.common_upgrades.utils.constants import SUPPORT_ROOT
from src.file_access import FileAccess
from src.local_logger import LocalLogger
from src.upgrade_step import UpgradeStep


class UpgradeJawsForPositionAutosave(UpgradeStep):
    """Update all batch files that load a database file using 'slits.template' to support autosave."""

    def perform(self, file_access: FileAccess, logger: LocalLogger):
        result = 0

        # Get database files using 'slits.template'.
        database_files = []
        for path in file_access.get_file_paths(SUPPORT_ROOT, ".substitutions"):
            if file_access.file_contains(path, "slits.template"):
                database_files.append(os.path.basename(path).split(".")[0] + ".db")

        logger.info(f"Database files using slits.template: {' '.join(database_files)}")

        # Check if batch files load any of the database files.
        for path in file_access.get_file_paths(file_access.config_base, ".cmd"):
            logger.info(f"Checking '{path}'")

            # Read file.
            contents = file_access.open_file(path)

            # Check and add macros.
            new_contents = []
            for line in contents:
                new_line = line

                if (
                    any(
                        re.search(rf"[\\|\/|\"]{database_file}", line)
                        for database_file in database_files
                    )
                    and "dbLoadRecords" in line
                    and "IFINIT_FROM_AS" not in line
                    and "IFNOTINIT_FROM_AS" not in line
                ):
                    logger.info(f"Adding macros to {line}")
                    new_line = re.sub(
                        r"\,?\"\)$",
                        ',IFINIT_FROM_AS=$(IFINIT_JAWS_FROM_AS=#),IFNOTINIT_FROM_AS=$(IFNOTINIT_JAWS_FROM_AS=)")',
                        new_line,
                    )

                    if new_line == line:
                        logger.error(
                            f"Failed to modify {line}, check to see if it needs to be manually changed."
                        )
                        result = -1

                new_contents.append(new_line)

            # Write if there are any changes.
            if contents != new_contents:
                file_access.write_file(path, new_contents)

        return result
