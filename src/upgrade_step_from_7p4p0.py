import socket

from src.common_upgrades.change_macros_in_xml import ChangeMacrosInXML
from src.common_upgrades.utils.macro import Macro
from src.upgrade_step import UpgradeStep

class SetISOBUSForILM200(UpgradeStep):
    """
    Set the DISABLE_AUTONOFF macro to true for EMU or add it if not present. When this macro is true,
    settings will be displayed on the Danfysik OPI allowing automatic power turn on/off.
    """

    def get_isobus_value_and_add_at_symbol(isobus_value):
        return f"@{isobus_value}"

    def perform(self, file_access, logger):
        try:
            hostname = socket.gethostname()
            # IMAT want it blank as they are not using ISOBUS
            if hostname != "NDXIMAT":
                ioc_name = "ILM200"
                change_macros_in_xml = ChangeMacrosInXML(file_access, logger)
                change_macros_in_xml.add_macro(ioc_name, Macro("ISOBUS", "1"), "^[0-9]+$", "ISOBUS address (default: 1)", "1")
                get_isobus_value_and_add_at_symbol = lambda isobus_value: f"@{isobus_value}"
                change_macros_in_xml.manipulate_macro_values(ioc_name, [(Macro("ISOBUS"), get_isobus_value_and_add_at_symbol)])
            return 0
        except Exception as e:
            logger.error("Unable to perform upgrade, caught error: {}".format(e))
            return 1
