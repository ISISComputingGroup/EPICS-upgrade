import logging

import git

from src.common_upgrades import change_pv_in_dashboard as dashboard
from src.file_access import FileAccess
from src.upgrade_step import UpgradeStep



class UpgradeFrom25p2p1p1(UpgradeStep):
    """
    Add calculation to dashboard to display when in test clock
    """

    def perform(self, file_access: FileAccess, logger: logging.Logger) -> int:
        file = dashboard.read_file()
        l_cal_record = dashboard.get_record("$(P)CS:DASHBOARD:BANNER:MIDDLE:_LCAL", file)
        l_cal_record.add_field("INDD", "$(P)DAE:DAETIMINGSOURCE CP MS")
        l_cal_record.add_field("EE", "DAE Test")
        l_cal_record.add_field("FF", "Internal Test Clock")
        l_cal_record.change_field("CALC", "A==1?BB:(DD==FF?EE:CC)")
        file_with_first_record = l_cal_record.update_record(file)
        
        v_cal_record = dashboard.get_record("$(P)CS:DASHBOARD:BANNER:MIDDLE:_VCAL", file_with_first_record)
        v_cal_record.add_field("INDD", "$(P)DAE:DAETIMINGSOURCE CP MS")
        v_cal_record.add_field("EE", "Clock")
        v_cal_record.add_field("FF", "Internal Test Clock")
        v_cal_record.change_field("CALC", "A==1?BB:(DD==FF?EE:CC)")
        
        output_file = v_cal_record.update_record(file_with_first_record)
        dashboard.write_file(output_file)