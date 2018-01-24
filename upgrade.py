import os
import sys

from src.file_access import FileAccess
from src.local_logger import LocalLogger
from src.upgrade import Upgrade
from src.upgrade_step_from_3p2p1 import UpgradeStepFrom3p2p1
from src.upgrade_step_from_3p2p1p1 import UpgradeStepFrom3p2p1p1
from src.upgrade_step_from_3p2p1p2 import UpgradeStepFrom3p2p1p2
from src.upgrade_step_from_4p1p0 import UpgradeStepFrom4p1p0
from src.upgrade_step_noop import UpgradeStepNoOp

# A list of upgrade step tuples tuple is name of version to apply the upgrade to and upgrade class.
# The last step should have an upgrade class of None (this is how it knows it has reached the end)
# Upgrade steps will be executed in order from the configuration set in the configuration file.
# To add a step which does nothing use UpgradeStepNoOp this is often used to get from the latest dev
# configuration to the latest production configuration
UPGRADE_STEPS = [
    ("3.2.1", UpgradeStepFrom3p2p1()),
    ("3.2.1.1", UpgradeStepFrom3p2p1p1()),
    ("3.2.1.2", UpgradeStepFrom3p2p1p2()),
    ("4.0.0", UpgradeStepNoOp()),
    ("4.1.0", UpgradeStepFrom4p1p0()),
    ("4.1.0.1", UpgradeStepNoOp()),
    ("4.2.0.0", None),
]

if __name__ == "__main__":

    config_root = os.path.abspath(os.path.join(os.environ["ICPCONFIGROOT"], os.pardir))
    log_dir = os.path.join(os.environ["ICPVARDIR"], "logs", "upgrade")

    logger = LocalLogger(log_dir)
    file_access = FileAccess(logger, config_root)

    upgrade = Upgrade(file_access=file_access, logger=logger, upgrade_steps=UPGRADE_STEPS)
    sys.exit(upgrade.upgrade())
