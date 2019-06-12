from src.upgrade_step import UpgradeStep
from src.common_upgrades.change_pvs_in_xml import ChangePVsInXML


class ChangeJawsManager(UpgradeStep):
    """
    Step that changes the PVs associated with the jawsmanager as they have been renamed.
    """

    def perform(self, file_access, logger):
        try:
            changer = ChangePVsInXML(file_access, logger)
            changer.change_pv_name("GEMJAWSET", "JAWMAN")
        except Exception as e:
            logger.error("Unable perform upgrade, caught error: {}".format(e))
            return -1

        return 0
