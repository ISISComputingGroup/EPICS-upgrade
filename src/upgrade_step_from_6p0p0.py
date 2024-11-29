import socket

from src.common_upgrades.change_macros_in_xml import ChangeMacrosInXML
from src.common_upgrades.utils.macro import Macro
from src.file_access import FileAccess
from src.local_logger import LocalLogger
from src.upgrade_step import UpgradeStep


class SetDanfysikDisableAutoonoffMacros(UpgradeStep):
    """Set the DISABLE_AUTONOFF macro to true for EMU or add it if not present. When this macro
    is true, settings will be displayed on the Danfysik OPI allowing automatic power turn on/off.
    """

    def perform(self, file_access: FileAccess, logger: LocalLogger) -> int:
        try:
            hostname = socket.gethostname()
            ioc_name = "DFKPS"
            if hostname == "NDXEMU":
                change_macros_in_xml = ChangeMacrosInXML(file_access, logger)
                change_macros_in_xml.add_macro(
                    ioc_name,
                    Macro("DISABLE_AUTOONOFF", "0"),
                    "^(0|1)$",
                    "Disable automatic PSU on/off feature",
                    "1",
                )
                change_macros_in_xml.change_macros(
                    ioc_name,
                    [(Macro("DISABLE_AUTOONOFF"), Macro("DISABLE_AUTOONOFF", "0"))],
                )
            return 0
        except Exception as e:
            logger.error("Unable to perform upgrade, caught error: {}".format(e))
            return 1
