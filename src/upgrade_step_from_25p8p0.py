from src.file_access import FileAccess
from src.local_logger import LocalLogger
from src.upgrade_step import UpgradeStep
import os


class UpgradeFrom25p8p0(UpgradeStep):
    """
    Adds a task to run the following script at 1 minute intervals:
    C:\Instrument\Apps\EPICS\ISIS\inst_servers\master\scripts\copy_bluesky_runs.bat
    """

    def perform(self, file_access: FileAccess, logger: LocalLogger):
        os.system('schtasks /Create /SC MINUTE /TN "bluesky_copier" /TR "C:\\Instrument\\Apps\\'
                  'EPICS\\ISIS\\inst_servers\\master\\scripts\\copy_bluesky_runs.vbs"')

