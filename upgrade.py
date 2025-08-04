import os
import sys

from src.file_access import FileAccess
from src.git_utils import RepoFactory
from src.local_logger import LocalLogger
from src.upgrade import Upgrade
from src.upgrade_step_add_meta_tag import UpgradeStepAddMetaXmlElement
from src.upgrade_step_from_6p0p0 import SetDanfysikDisableAutoonoffMacros
from src.upgrade_step_from_7p2p0 import (
    ChangeReflOPITarget,
    IgnoreRcpttSynoptics,
    UpgradeMotionSetPoints,
)
from src.upgrade_step_from_7p4p0 import SetISOBUSForILM200
from src.upgrade_step_from_9p0p0 import ChangeLETCollimatorCmd
from src.upgrade_step_from_10p0p0 import RemoveReflDeviceScreen
from src.upgrade_step_from_11p0p0 import RenameMercurySoftwarePressureControlMacros
from src.upgrade_step_from_12p0p0 import UpgradeJawsForPositionAutosave
from src.upgrade_step_from_12p0p1 import AddOscCollimMovingIndicator
from src.upgrade_step_from_12p0p2 import UpgradeFrom12p0p2
from src.upgrade_step_from_12p0p3 import UpgradeFrom12p0p3
from src.upgrade_step_from_15p0p0 import UpgradeFrom15p0p0
from src.upgrade_step_from_25p2p1 import UpgradeFrom25p2p1
from src.upgrade_step_from_25p2p1p1 import UpgradeFrom25p2p1p1
from src.upgrade_step_noop import UpgradeStepNoOp

# A list of upgrade step tuples tuple is name of version to apply the upgrade to and upgrade class.
# The last step should have an upgrade class of None (this is how it knows it has reached the end)
# Upgrade steps will be executed in order from the configuration set in the configuration file.
# To add a step which does nothing use UpgradeStepNoOp this is often used to get from the latest dev
# configuration to the latest production configuration

# Do not consider dropping the previous last entry even if adding a new step that does nothing.
# Though that version may not have been deployed to any instruments, the config version will exist
# on a system test build server and probably some developer's machines too

# also make sure that the  config_version.txt  in the master configurations git repository
# on control-svcs used for creating a new instrument settings area is at least the lowest
# versions below or else you will not be able to upgrade a newly created instrument

# Upgrade from 6.0.0 only going forward.
UPGRADE_STEPS = [
    # (from this version, use this function to get to next version)
    ("6.0.0", SetDanfysikDisableAutoonoffMacros()),
    ("6.0.0.1", UpgradeStepNoOp()),
    ("7.0.0", UpgradeStepNoOp()),
    ("7.1.0", UpgradeStepNoOp()),
    ("7.2.0", IgnoreRcpttSynoptics()),
    (
        "7.2.1",
        UpgradeStepNoOp(),
    ),  # This is in the correct order as 7.2.1 happened before the upgrade of the motion setpoints
    ("7.2.0.1", UpgradeMotionSetPoints()),
    ("7.2.0.2", UpgradeStepNoOp()),
    ("7.2.1.1", ChangeReflOPITarget()),
    ("7.2.1.2", UpgradeStepNoOp()),
    ("7.3.0", UpgradeStepNoOp()),
    ("7.3.1", UpgradeStepAddMetaXmlElement("configuresBlockGWAndArchiver", "false")),
    ("7.4.0", UpgradeStepNoOp()),
    ("7.4.1", SetISOBUSForILM200()),
    ("7.4.1.1", UpgradeStepNoOp()),
    ("8.0.0", UpgradeStepNoOp()),
    ("9.0.0", ChangeLETCollimatorCmd()),
    ("9.0.1", UpgradeStepNoOp()),
    ("10.0.0", RemoveReflDeviceScreen()),
    ("11.0.0", UpgradeStepNoOp()),
    ("11.0.1", UpgradeStepNoOp()),
    ("11.1.0", RenameMercurySoftwarePressureControlMacros()),
    ("12.0.0", UpgradeJawsForPositionAutosave()),
    ("12.0.1", AddOscCollimMovingIndicator()),
    ("12.0.2", UpgradeFrom12p0p2()),
    ("12.0.3", UpgradeFrom12p0p3()),
    ("13.0.0", UpgradeStepNoOp()),
    ("13.0.1", UpgradeStepNoOp()),
    ("14.0.0", UpgradeStepNoOp()),
    ("15.0.0", UpgradeFrom15p0p0()),
    ("15.0.1", UpgradeStepNoOp()),
    ("25.2.0", UpgradeStepNoOp()),
    ("25.2.1", UpgradeFrom25p2p1()),
    ("25.2.1.1", UpgradeFrom25p2p1p1()),
    ("25.2.2", None),
    # to add step see README.md
]

if __name__ == "__main__":
    config_root = os.path.abspath(os.path.join(os.environ["ICPCONFIGROOT"], os.pardir))
    log_dir = os.path.join(os.environ["ICPVARDIR"], "logs", "upgrade")

    logger = LocalLogger(log_dir)
    file_access = FileAccess(logger, config_root)
    git_repo = RepoFactory.get_repo(config_root)

    upgrade = Upgrade(
        file_access=file_access,
        logger=logger,
        upgrade_steps=UPGRADE_STEPS,
        git_repo=git_repo,
    )
    sys.exit(upgrade.upgrade())
