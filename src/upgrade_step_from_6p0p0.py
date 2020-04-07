import socket

from src.common_upgrades.change_macros_in_xml import ChangeMacrosInXML
from src.common_upgrades.utils.macro import Macro
from src.upgrade_step import UpgradeStep

class SetDanfysikDisableAutoonoffMacros(UpgradeStep):
    """
    Set the ALLOW_AUTO_ONOFF macro to true for EMU. When this macro is true, 
    settings will be displayed on the Danfysik OPI allowing automatic power turn on/off.
    """
    def perform(self, file_access, logger):
        try:
            hostname = socket.gethostname()
            ioc_name = "DFKPS"
            if hostname=="NDXEMU":
                macro_to_change = Macro("DISABLE_AUTOONOFF", "0")
                change_macros_in_xml = ChangeMacrosInXML(file_access, logger)
                change_macros_in_xml.change_specific_macros(ioc_name, macro_to_change)
            return 0
        except:
            return 1