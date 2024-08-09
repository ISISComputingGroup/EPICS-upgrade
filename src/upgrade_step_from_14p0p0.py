import socket

from src.common_upgrades.change_macros_in_xml import ChangeMacrosInXML
from src.common_upgrades.utils.macro import Macro
from src.file_access import FileAccess
from src.local_logger import LocalLogger
from src.upgrade_step import UpgradeStep


class UpgradeFrom14p0p0(UpgradeStep):
    """Set CARDS0 macro for all instruments,
     except ARGUS/CHRONUS in which it is configured differently already"""

    def perform(self, file_access: FileAccess, logger: LocalLogger) -> int:
        try:
            hostname = socket.gethostname()
            # Make sure we do not perform this on ARGUS/CHRONUS where the macro is already present
            if hostname not in ["NDXARGUS", "NDXCHRONUS"]:
                ioc_name = "CAENV895"
                change_macros_in_xml = ChangeMacrosInXML(file_access, logger)
                change_macros_in_xml.add_macro(
                    ioc_name,
                    Macro("CARDS", "6"),
                    "^[0-9]+$",
                    "Number of cards in crate 0, leave blank if this crate does not exist",
                    "Yes",
                )
            return 0
        except Exception as e:
            logger.error("Unable to perform upgrade, caught error: {}".format(e))
            return 1
