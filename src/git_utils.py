# ruff: noqa: ANN205, ANN001
import git


class RepoFactory:
    @staticmethod
    def get_repo(working_directory: str):
        # Check repo
        try:
            return git.Repo(working_directory, search_parent_directories=True)
        except Exception:
            # Not a valid repository
            raise Exception(working_directory + " is not under version control")
