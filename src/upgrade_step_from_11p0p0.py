# ruff: noqa: E501
import socket

from src.common_upgrades.change_macros_in_xml import ChangeMacrosInXML
from src.common_upgrades.change_pvs_in_xml import ChangePVsInXML
from src.common_upgrades.utils.macro import Macro
from src.file_access import FileAccess
from src.local_logger import LocalLogger
from src.upgrade_step import UpgradeStep


class RenameMercurySoftwarePressureControlMacros(UpgradeStep):
    """SPC_... macro names have been adjusted to FLOW_SPC... names to differentiate them
    from the new VTI Software Pressure Control macros that have been added with the new logic.

    Rename the old macros to the new ones.
    """

    rename_macros = [
        (Macro("FULL_AUTO_PRESSURE_1"), Macro("FLOW_SPC_PRESSURE_1")),
        (Macro("FULL_AUTO_PRESSURE_2"), Macro("FLOW_SPC_PRESSURE_2")),
        (Macro("FULL_AUTO_PRESSURE_3"), Macro("FLOW_SPC_PRESSURE_3")),
        (Macro("FULL_AUTO_PRESSURE_4"), Macro("FLOW_SPC_PRESSURE_4")),
        (Macro("FULL_AUTO_MIN_PRESSURE"), Macro("FLOW_SPC_MIN_PRESSURE")),
        (Macro("FULL_AUTO_MAX_PRESSURE"), Macro("FLOW_SPC_MAX_PRESSURE")),
        (Macro("FULL_AUTO_TEMP_DEADBAND"), Macro("FLOW_SPC_TEMP_DEADBAND")),
        (Macro("FULL_AUTO_OFFSET"), Macro("FLOW_SPC_OFFSET")),
        (Macro("FULL_AUTO_OFFSET_DURATION"), Macro("FLOW_SPC_OFFSET_DURATION")),
        (Macro("FULL_AUTO_GAIN"), Macro("FLOW_SPC_GAIN")),
    ]

    new_macros = [
        (
            Macro("SPC_TYPE_1"),
            "^(FLOW|VTI|NONE)$",
            "Software pressure control method to use on Temperature 1",
            "NONE",
        ),
        (
            Macro("SPC_TYPE_2"),
            "^(FLOW|VTI|NONE)$",
            "Software pressure control method to use on Temperature 2",
            "NONE",
        ),
        (
            Macro("SPC_TYPE_3"),
            "^(FLOW|VTI|NONE)$",
            "Software pressure control method to use on Temperature 3",
            "NONE",
        ),
        (
            Macro("SPC_TYPE_4"),
            "^(FLOW|VTI|NONE)$",
            "Software pressure control method to use on Temperature 4",
            "NONE",
        ),
        (
            Macro("FLOW_SPC_TABLE_FILE"),
            r"^\.*$",
            "File to load to related temperature to pressure from calibration directory other_devices.",
            "little_blue_cryostat.txt",
        ),
        (
            Macro("VTI_SPC_PRESSURE_1"),
            "^[1,2]$",
            "VTI software pressure control: The index of the pressure card to control with temp1.",
            "",
        ),
        (
            Macro("VTI_SPC_PRESSURE_2"),
            "^[1,2]$",
            "VTI software pressure control: The index of the pressure card to control with temp2.",
            "",
        ),
        (
            Macro("VTI_SPC_PRESSURE_3"),
            "^[1,2]$",
            "VTI software pressure control: The index of the pressure card to control with temp3.",
            "",
        ),
        (
            Macro("VTI_SPC_PRESSURE_4"),
            "^[1,2]$",
            "VTI software pressure control: The index of the pressure card to control with temp4.",
            "",
        ),
        (
            Macro("VTI_SPC_MIN_PRESSURE"),
            r"^[0-9]+\.?[0-9]*$",
            "VTI software pressure control: minimum pressure allowed.",
            "0.0",
        ),
        (
            Macro("VTI_SPC_MAX_PRESSURE"),
            r"^[0-9]+\.?[0-9]*$",
            "VTI software pressure control: maximum pressure allowed.",
            "0.0",
        ),
        (
            Macro("VTI_SPC_PRESSURE_CONSTANT"),
            r"^[0-9]+\.?[0-9]*$",
            "VTI software pressure control: constant pressure to use when below cutoff point.",
            "5.0",
        ),
        (
            Macro("VTI_SPC_PRESSURE_MAX_LKUP"),
            r"^\.*$",
            "VTI software pressure control: Filename for temp-based lookup table when above cutoff point.",
            "None.txt",
        ),
        (
            Macro("VTI_SPC_TEMP_CUTOFF_POINT"),
            r"^[0-9]+\.?[0-9]*$",
            "VTI software pressure control: temperature to switch between using a user-set constant and a linear interpolation function.",
            "5.0",
        ),
        (
            Macro("VTI_SPC_TEMP_SCALE"),
            r"^[0-9]+\.?[0-9]*$",
            "VTI software pressure control: amount to scale temp by to further control P vs T dependence.",
            "2.0",
        ),
        (
            Macro("VTI_SPC_SET_DELAY"),
            r"^[0-9]+\.?[0-9]*$",
            "VTI software pressure control: delay between making adjustments to the pressure setpoint in seconds.",
            "10.0",
        ),
    ]

    def perform(self, file_access: FileAccess, logger: LocalLogger) -> int:
        try:
            hostname = socket.gethostname()
            ioc_name = "MERCURY_01"
            if hostname == "NDXPOLREF":
                change_macros_in_xml = ChangeMacrosInXML(file_access, logger)
                change_macros_in_xml.change_macros(ioc_name, self.rename_macros)
                for macro in self.new_macros:
                    change_macros_in_xml.add_macro(ioc_name, macro[0], macro[1], macro[2], macro[3])
                change_pvs_in_xml = ChangePVsInXML(file_access, logger)
                change_pvs_in_xml.change_pv_name("FULL_AUTO", "SPC")
            return 0
        except Exception as e:
            logger.error("Unable to perform upgrade, caught error: {}".format(e))
            return 1
