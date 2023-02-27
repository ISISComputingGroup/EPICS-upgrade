import git


class RepoFactory:
    @staticmethod
    def get_repo(working_directory):
        # Check repo
        try:
            return git.Repo(working_directory, search_parent_directories=True)
        except Exception as e:
            # Not a valid repository
            raise git.NotUnderVersionControl(working_directory)


