from src.common_upgrades import change_pv_in_dashboard as dashboard
from src.file_access import FileAccess
from src.local_logger import LocalLogger
from src.upgrade_step import UpgradeStep


class UpgradeFrom25p2p1p1(UpgradeStep):
    """
    Add calculation to dashboard to display when in test clock
    """

    def perform(self, file_access: FileAccess, logger: LocalLogger) -> int:
        reader = dashboard.ChangePvInDashboard(file_access, logger)
        pass_fail = 0
        file = reader.read_file()
        l_cal_record = reader.get_record("$(P)CS:DASHBOARD:BANNER:MIDDLE:_LCAL", file)
        if l_cal_record is not None:
            l_cal_record.add_field("INDD", "$(P)DAE:DAETIMINGSOURCE CP MS")
            l_cal_record.add_field("EE", "DAE Test")
            l_cal_record.add_field("FF", "Internal Test Clock")
            l_cal_record.change_field("CALC", "A==1?BB:(DD==FF?EE:CC)")
            file = l_cal_record.update_record(file)
        else:
            pass_fail = 1

        v_cal_record = reader.get_record("$(P)CS:DASHBOARD:BANNER:MIDDLE:_VCAL", file)
        if v_cal_record is not None:
            v_cal_record.add_field("INDD", "$(P)DAE:DAETIMINGSOURCE CP MS")
            v_cal_record.add_field("EE", "Clock")
            v_cal_record.add_field("FF", "Internal Test Clock")
            v_cal_record.change_field("CALC", "A==1?BB:(DD==FF?EE:CC)")

            file = v_cal_record.update_record(file)
        else:
            pass_fail = 1

        reader.write_file(file)
        return pass_fail
