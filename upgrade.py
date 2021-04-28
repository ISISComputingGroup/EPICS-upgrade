import os
import sys

from src.file_access import FileAccess
from src.local_logger import LocalLogger
from src.upgrade import Upgrade
from src.upgrade_step_from_6p0p0 import SetDanfysikDisableAutoonoffMacros
from src.upgrade_step_from_7p2p0 import IgnoreRcpttSynoptics, UpgradeMotionSetPoints, ChangeReflOPITarget
from src.upgrade_step_from_7p4p0 import SetISOBUSForILM200
from src.upgrade_step_noop import UpgradeStepNoOp
from src.upgrade_step_add_meta_tag import UpgradeStepAddMetaXmlElement

# A list of upgrade step tuples tuple is name of version to apply the upgrade to and upgrade class.
# The last step should have an upgrade class of None (this is how it knows it has reached the end)
# Upgrade steps will be executed in order from the configuration set in the configuration file.
# To add a step which does nothing use UpgradeStepNoOp this is often used to get from the latest dev
# configuration to the latest production configuration

# Upgrade from 6.0.0 only going forward.
UPGRADE_STEPS = [
    # (from this version, use this function to get to next version)
    ("6.0.0", SetDanfysikDisableAutoonoffMacros()),
    ("6.0.0.1", UpgradeStepNoOp()),
    ("7.0.0", UpgradeStepNoOp()),
    ("7.1.0", UpgradeStepNoOp()),
    ("7.2.0", IgnoreRcpttSynoptics()),
    ("7.2.1", UpgradeStepNoOp()), # This is in the correct order as 7.2.1 happened before the upgrade of the motion setpoints
    ("7.2.0.1", UpgradeMotionSetPoints()),
    ("7.2.0.2", UpgradeStepNoOp()),
    ("7.2.1.1", ChangeReflOPITarget()),
    ("7.2.1.2", UpgradeStepNoOp()),
    ("7.3.0", UpgradeStepNoOp()),
    ("7.3.1", UpgradeStepAddMetaXmlElement("configuresBlockGWAndArchiver", "false")),
    ("7.4.0", UpgradeStepNoOp()),
    ("7.4.1", SetISOBUSForILM200()),
    ("7.4.1.1", None)

    # to add step see https://github.com/ISISComputingGroup/ibex_developers_manual/wiki/Config-Upgrader#adding-an-upgrade-step
]

if __name__ == "__main__":
    config_root = os.path.abspath(os.path.join(os.environ["ICPCONFIGROOT"], os.pardir))
    log_dir = os.path.join(os.environ["ICPVARDIR"], "logs", "upgrade")

    logger = LocalLogger(log_dir)
    file_access = FileAccess(logger, config_root)

    upgrade = Upgrade(file_access=file_access, logger=logger, upgrade_steps=UPGRADE_STEPS)
    sys.exit(upgrade.upgrade())
