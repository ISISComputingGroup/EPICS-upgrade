from src.upgrade_step import UpgradeStep
from .file_access import FileAccess
from .local_logger import LocalLogger


class UpgradeStepNoOp(UpgradeStep):
    """
    An upgrade step that does nothing. This can be used to add a upgrade to the latest production version.
    """

    def perform(self, file_access, logger):
        """
        No nothing return sucess

        Args:
            file_access (FileAccess): file access
            logger (LocalLogger): logger

        Returns: exit code 0 success

        """
        return 0
