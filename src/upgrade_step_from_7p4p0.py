import socket

from src.common_upgrades.change_macros_in_xml import ChangeMacrosInXML
from src.common_upgrades.utils.macro import Macro
from src.file_access import FileAccess
from src.local_logger import LocalLogger
from src.upgrade_step import UpgradeStep


class SetISOBUSForILM200(UpgradeStep):
    """Set the ILM200 ISOBUS value to None for IMAT as they are the first to not use ISOBUS
    on the ILM200."""

    def perform(self, file_access: FileAccess, logger: LocalLogger) -> int:
        try:
            hostname = socket.gethostname()
            # IMAT want it blank as they are not using ISOBUS
            if hostname == "NDXIMAT":
                ioc_name = "ILM200"
                change_macros_in_xml = ChangeMacrosInXML(file_access, logger)
                change_macros_in_xml.add_macro(
                    ioc_name,
                    Macro("USE_ISOBUS", "No"),
                    "^(Yes|No)$",
                    "Whether to use ISOBUS for communications (default: Yes)",
                    "Yes",
                )
            return 0
        except Exception as e:
            logger.error("Unable to perform upgrade, caught error: {}".format(e))
            return 1
