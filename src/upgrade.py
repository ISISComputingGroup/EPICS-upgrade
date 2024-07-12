import os

from src.common_upgrades.sql_utilities import SqlConnection

VERSION_FILENAME = os.path.join("configurations", "config_version.txt")


class UpgradeError(Exception):
    """There is an error in the upgrade
    """

    pass


class Upgrade(object):
    """Use upgrade steps to upgrade a configuration
    """

    def __init__(self, file_access, logger, upgrade_steps, git_repo):
        """Constructor

        Args:
            file_access (FileAccess): an object to interact with files
            logger (LocalLogger): an object to log data
            upgrade_steps: steps to perform an upgrade from scratch
            git_repo: git repository to perform committing, tagging on version upgrade.
        """
        self._file_access = file_access
        self._logger = logger
        if len(upgrade_steps) == 0:
            raise UpgradeError()
        if None not in [y for x, y in upgrade_steps]:
            raise UpgradeError()
        self._upgrade_steps = upgrade_steps
        self._git_repo = git_repo

    def get_version_number(self):
        """Find the current version number of the repository. If there is no version number the
        repository is considered unversioned and the lowest version is written to the repository

        Returns: the version number
        """
        try:
            for line in self._file_access.open_file(VERSION_FILENAME):
                return line.strip()
        except IOError:
            initial_version_number = self._upgrade_steps[0][0]
            self._file_access.write_version_number(initial_version_number, VERSION_FILENAME)
            return initial_version_number

    def upgrade(self):
        """Perform an upgrade on the configuration directory

        Returns: status code 0 for success; not 0 for failure

        """
        current_version = self.get_version_number()
        self._logger.info("Config at initial version {0}".format(current_version))
        upgrade = False
        final_upgrade_version = None
        with SqlConnection():
            for version, upgrade_step in self._upgrade_steps:
                if version == current_version:
                    upgrade = True
                    if upgrade_step is None:
                        self._logger.info("Current config is on latest version, no upgrade needed")

                if upgrade:
                    final_upgrade_version = version
                    if upgrade_step is not None:
                        self._logger.info("Upgrading from {0}".format(version))
                        self._logger.info("-------------------------")
                        result = upgrade_step.perform(self._file_access, self._logger)
                        if result != 0:
                            return result
                        self._file_access.write_version_number(version, VERSION_FILENAME)
                        self._commit_tag_and_push(version)

        if upgrade:
            self._file_access.write_version_number(final_upgrade_version, VERSION_FILENAME)
            self._logger.info("Finished upgrade. Now on version {0}".format(final_upgrade_version))
            self._commit_tag_and_push(final_upgrade_version, final=True)
            return 0
        else:
            self._logger.error("Unknown version number {0}".format(current_version))
            return -1

    def _commit_tag_and_push(self, version, final=False):
        self._git_repo.git.add(A=True)
        commit_message = f"IBEX Upgrade {'from' if not final else 'to'} {version}"
        self._git_repo.index.commit(commit_message)
        tag_name = f"{self._git_repo.active_branch}_{version}{'_upgrade' if not final else ''}"
        self._git_repo.create_tag(tag_name, message=commit_message, force=True)
        self._git_repo.remote(name="origin").push()
