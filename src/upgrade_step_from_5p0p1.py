from src.common_upgrades.change_macro_in_globals import ChangeMacroInGlobals
from src.common_upgrades.change_macros_in_xml import ChangeMacrosInXML
import os

from src.common_upgrades.utils.macro import Macro
from src.upgrade_step import UpgradeStep


class UpgradeStepFrom5p0p1(UpgradeStep):
    ERROR_CODE = -1
    SUCCESS_CODE = 0
    LOAD_MOTION_SP_DB_INSTRUCTION = 'dbLoadRecords("$(MOTIONSETPOINTS)/db/motionSetPoints.db"'
    LOAD_INPOS_DB_INSTRUCTION = 'dbLoadRecordsLoop("$(MOTIONSETPOINTS)/db/inPos.db"'

    """
    Change the PIMOT macros from BAUD1 and PORT1 to BAUD and PORT respectively.
    """

    def perform(self, file_access, logger):
        """
        Args:
            file_access (FileAccess): file access
            logger (LocalLogger): logger

        Returns: exit code 0 success; anything else fail
        """
        motor_dirs = ["galil", "mclennan", "SM300_01"]

        for motor in motor_dirs:
            file_name = os.path.join("configurations", motor, "motionSetPoints.cmd")
            if file_access.exists(file_name):
                try:
                    content = file_access.open_file(file_name)
                    self.append_load_inpos_instructions(content)
                    file_access.write_file(file_name, content)
                except OSError:
                    return self.ERROR_CODE

        return self.SUCCESS_CODE

    def append_load_inpos_instructions(self, content):
        """
        For each dbLoadRecord instruction loading a motionSetPoint.db read from the input file, add an equivalent line
        to load the inPos.db with same macros.
        Args:
            file_access: The file access utility
            content: The content of the motionSetPoint file
        """
        lines_to_add = []
        for line in content:
            if self.LOAD_MOTION_SP_DB_INSTRUCTION in line:
                line = line.replace(self.LOAD_MOTION_SP_DB_INSTRUCTION, self.LOAD_INPOS_DB_INSTRUCTION)
                line = line[:-1] + ',"NUMPOS", 0, 30)'
                lines_to_add.append(line)

        for line in lines_to_add:
            content.append(line)
