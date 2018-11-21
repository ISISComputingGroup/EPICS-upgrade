import os
import sys

from src.file_access import FileAccess
from src.local_logger import LocalLogger
from src.upgrade import Upgrade
from src.upgrade_step_from_4p3p1 import UpgradeStepFrom4p3p1
from src.upgrade_step_from_5p0p1 import UpgradeMotionSetpoints, UpgradeExpDatabase
from src.upgrade_step_from_5p1p0 import RemoveOldExpPopulator
from src.upgrade_step_noop import UpgradeStepNoOp

# A list of upgrade step tuples tuple is name of version to apply the upgrade to and upgrade class.
# The last step should have an upgrade class of None (this is how it knows it has reached the end)
# Upgrade steps will be executed in order from the configuration set in the configuration file.
# To add a step which does nothing use UpgradeStepNoOp this is often used to get from the latest dev
# configuration to the latest production configuration

# Upgrade from 4.3.1 only going forward.
UPGRADE_STEPS = [
    ("4.3.1", UpgradeStepFrom4p3p1()),
    ("4.3.1.1", UpgradeStepNoOp()),
    ("4.4.0", UpgradeStepNoOp()),
    ("4.4.1", UpgradeStepNoOp()),
    ("5.0.0", UpgradeStepNoOp()),
    ("5.0.1", UpgradeMotionSetpoints()),
    ("5.0.2", UpgradeExpDatabase()),
    ("5.1.0", RemoveOldExpPopulator()),
    ("5.2.0", None)
]

if __name__ == "__main__":

    config_root = os.path.abspath(os.path.join(os.environ["ICPCONFIGROOT"], os.pardir))
    log_dir = os.path.join(os.environ["ICPVARDIR"], "logs", "upgrade")

    logger = LocalLogger(log_dir)
    file_access = FileAccess(logger, config_root)

    upgrade = Upgrade(file_access=file_access, logger=logger, upgrade_steps=UPGRADE_STEPS)
    sys.exit(upgrade.upgrade())
