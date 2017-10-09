"""
Script to install IBEX to various machines
"""

import argparse
import os
import socket

import subprocess

import shutil
import stat


INSTRUMENT_BASE_DIR = os.path.join(r"c:\Instrument")
APPS_BASE_DIR = os.path.join(INSTRUMENT_BASE_DIR, "Apps")
EPICS_PATH = os.path.join(APPS_BASE_DIR, "EPICS")
GUI_PATH = os.path.join(APPS_BASE_DIR, "Client")
PYTHON_PATH = os.path.join(APPS_BASE_DIR, "Python")
EPICS_UTILS_PATH = os.path.join(APPS_BASE_DIR, "EPICS_UTILS")
DESKTOP_TRAINING_FOLDER_PATH = os.path.join(os.environ["userprofile"], "desktop", "Mantid+IBEX training")
SETTINGS_CONFIG_FOLDER = os.path.join("Settings", "config")
SETTINGS_CONFIG_PATH = os.path.join(INSTRUMENT_BASE_DIR, SETTINGS_CONFIG_FOLDER)


SOURCE_FOLDER = os.path.join(os.path.dirname(os.path.realpath(__file__)), "resources")
SOURCE_MACHINE_SETTINGS_CONFIG_PATH = os.path.join(SOURCE_FOLDER, SETTINGS_CONFIG_FOLDER, "NDXOTHER")
SOURCE_MACHINE_SETTINGS_COMMON_PATH = os.path.join(SOURCE_FOLDER, SETTINGS_CONFIG_FOLDER, "common")


class ErrorInTask(Exception):
    """
    Exception if there is an error when running a task.
    """

    def __init__(self, message):
        self.message = message


class ErrorInRun(ErrorInTask):
    """
    Exception if there is an error when running a process.
    """
    def __init__(self, message):
        super(ErrorInRun, self).__init__(message)


class ErrorWithFile(ErrorInTask):
    """
    Exception if there is an error when doing something with a file
    """
    def __init__(self, message):
        super(ErrorWithFile, self).__init__(message)


class UserStop(Exception):
    """
    Exception when a task stops because of a user request
    """
    pass


class RunProcess(object):
    """
    Create a process runner to run a process.
    """
    def __init__(self, working_dir, executable_file, executable_directory=None, press_any_key=False):
        """
        Create a process that needs running

        Args:
            working_dir: working directory of the process
            executable_file: file of the process to run, e.g. a bat file
            executable_directory: the directory in which the executable file lives, if None, default, use working dir
            press_any_key: if true then press a key to finish
        """
        self._working_dir = working_dir
        self._bat_file = executable_file
        self._press_any_key = press_any_key
        if executable_directory is None:
            self._full_path_to_process_file = os.path.join(working_dir, executable_file)
        else:
            self._full_path_to_process_file = os.path.join(executable_directory, executable_file)

    def run(self):
        """
        Run the process

        Returns:
        Raises ErrorInRun: if there is a known problem with the run
        """
        try:
            print("    Running {0} ...".format(self._bat_file))

            if self._press_any_key:
                output = subprocess.Popen([self._full_path_to_process_file], cwd=self._working_dir,
                                          stdout=subprocess.PIPE,
                                          stderr=subprocess.STDOUT, stdin=subprocess.PIPE)
                output_lines, err = output.communicate(" ")
            else:
                output_lines = subprocess.check_output(
                    [self._full_path_to_process_file],
                    cwd=self._working_dir,
                    stderr=subprocess.STDOUT,
                    stdin=subprocess.PIPE)

            for line in output_lines.splitlines():
                print("    , {line}".format(line=line))
            print("    ... finished")
        except subprocess.CalledProcessError as ex:
            raise ErrorInRun("Command failed with error: {0}".format(ex))
        except WindowsError as ex:
            if ex.errno == 2:
                raise ErrorInRun("Command '{cmd}' not found in '{cwd}'".format(
                    cmd=self._bat_file, cwd=self._working_dir))
            raise ex


class Task(object):
    """
    Task to be performed for install.

    Confirms a step is to be run (if needed) and places the answer in do_step.
    Wraps the task in print statements so users can see when a task starts and ends.
    """

    def __init__(self, task_name, user_prompt):
        """
        Initialised.
        Args:
            task_name: the name of the task
            user_prompt: object allowing the user to be prompted for an answer
        """
        self._task = task_name
        self._user_prompt = user_prompt
        self.do_step = True

    def __enter__(self):
        self.do_step = self._user_prompt.confirm_step(self._task)
        print("{task} ...".format(task=self._task))
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val is None:
            print("... Done".format(task=self._task))


class FileUtils(object):
    """
    Various utilities for interacting with the file system
    """

    def delete_if_exists(self, path):
        """
        Delete a file path if it exists
        Args:
            path: path to delete

        Returns:

        Raises ErrorWithFile: if it can not delete a file

        """
        def on_error_make_read_write(func, path, exc_info):
            """
            If there is an error then make file read write and try again
            Args:
                func: function it was in
                path: path it had troubles with
                exc_info: exception information

            Returns:

            """
            if exc_info[0] is WindowsError:
                try:
                    os.chmod(path, stat.S_IRWXU)
                    os.remove(path)
                    return
                except Exception as ex:
                    pass
            raise ErrorWithFile(
                "Failed to delete file {file} from epics because: {error}".format(file=path, error=str(exc_info)))

        if os.path.isdir(path):
            shutil.rmtree(path, onerror=on_error_make_read_write)

    def mkdir_recursive(self, path):
        """
        Make a directory and all its ancestors
        Args:
            path: path of directory

        Returns:

        """
        sub_path = os.path.dirname(path)
        if not os.path.exists(sub_path):
            self.mkdir_recursive(sub_path)
        if not os.path.exists(path):
            os.mkdir(path)


class UpgradeInstrument(object):
    """
    Class to upgrade the instrument installation to the given version of IBEX.
    """

    def __init__(self, user_prompt, server_source_dir, client_source_dir, file_utils=FileUtils()):
        """
        Initializer.
        Args:
            user_prompt: a object to allow prompting of the user
            server_source_dir: directory to install ibex server from
            client_source_dir: directory to install ibex client from
            file_utils : collection of file utilities
        """
        self._prompt = user_prompt
        self._server_source_dir = server_source_dir
        self._client_source_dir = client_source_dir
        self._file_utils = file_utils

    def _get_machine_name(self):
        """
        Finds the machine name

        Returns:

        """
        self._machine_name = socket.gethostname()

    def _stop_ibex_server(self):
        """
        Stop the current IBEX server running. Current this can not be run because it kills any python
        processes including this one.

        Returns:

        """
        # with Task("Stopping IBEX server", self._prompt):
        #     RunProcess(EPICS_PATH, "stop_ibex_server.bat").run()
        pass

    def _remove_old_ibex(self):
        """
        Removes older versions of IBEX server, client, genie_python and epics utils
        Returns:

        """
        with Task("Removing old version of IBEX", self._prompt) as task:
            if task.do_step:
                for path in (EPICS_PATH, PYTHON_PATH, GUI_PATH, EPICS_UTILS_PATH):
                    self._file_utils.delete_if_exists(path)

    def _clean_up_desktop_ibex_training_folder(self):
        """
        Remove training folder from the desktop
        Returns:

        """
        with Task("Removing training folder on desktop ...", self._prompt) as task:
            if task.do_step:
                self._file_utils.delete_if_exists(DESKTOP_TRAINING_FOLDER_PATH)

    def _remove_settings(self):
        """
        remove old settings
        Returns:

        """
        with Task("Removing old settings file", self._prompt) as task:
            if task.do_step:
                self._file_utils.delete_if_exists(SETTINGS_CONFIG_PATH)

    def _install_settings(self):
        """
        Install new settings from the current folder
        Returns:

        """
        with Task("Install settings", self._prompt) as task:
            if task.do_step:
                self._file_utils.mkdir_recursive(SETTINGS_CONFIG_PATH)
                settings_path = os.path.join(SETTINGS_CONFIG_PATH, self._machine_name)

                shutil.copytree(SOURCE_MACHINE_SETTINGS_CONFIG_PATH, settings_path)

                inst_name = self._machine_name.lower()
                for p in ["ndx", "nde"]:
                    if inst_name.startswith(p):
                        inst_name = inst_name.lower()[len(p):]
                        break
                inst_name = inst_name.replace("-", "_")
                shutil.move(os.path.join(settings_path, "Python", "init_inst_name.py"),
                            os.path.join(settings_path, "Python", "init_{inst_name}.py".format(inst_name=inst_name)))

                shutil.copytree(SOURCE_MACHINE_SETTINGS_COMMON_PATH, os.path.join(SETTINGS_CONFIG_PATH, "common"))

    def _upgrade_notepad_pp(self):
        """
        Install (start installation of) notepad ++
        Returns:

        """
        with Task("Upgrading Notepad++. Please follow system dialogs", self._prompt) as task:
            if task.do_step:
                RunProcess(r"C:\Program Files (x86)\Notepad++\updater", "GUP.exe").run()

    def _install_ibex_server(self, with_utils):
        """
        Install ibex server.
        Args:
            with_utils: True also install epics utils using icp binaries; False don't

        Returns:

        """
        with Task("Installing IBEX Server", self._prompt) as task:
            if task.do_step:
                self._file_utils.mkdir_recursive(APPS_BASE_DIR)
                RunProcess(self._server_source_dir, "install_to_inst.bat").run()
                if with_utils and self._prompt.confirm_step("install icp binaries"):
                    RunProcess(EPICS_PATH, "create_icp_binaries.bat").run()

    def _install_ibex_client(self):
        """
        Install the ibex client (which also installs genie python).
        Returns:

        """
        with Task("Installing IBEX GUI", self._prompt) as task:
            if task.do_step:
                self._file_utils.mkdir_recursive(APPS_BASE_DIR)
                RunProcess(self._client_source_dir, "install_client.bat", press_any_key=True).run()

    def _start_ibex_server(self):
        """
        Start the ibex server. Can not do this because it would kill the current python process.
        Returns:

        """
        # with Task("Starting IBEX server..."):
        #    RunProcess(EPICS_PATH, "start_ibex_server.bat").run()
        pass

    def _check_upgrade_testing_machine(self):
        """
        Print information about the current upgrade and prompt the user
        Returns:
        Raises UserStop: when the user doesn't want to continue

        """
        print("Upgrade {0} as a Training Machine".format(self._machine_name))
        print("    Server source: {0}".format(self._server_source_dir))
        print("    Client source: {0}".format(self._client_source_dir))
        answer = self._prompt.prompt("Continue? [Y/N]", ["Y", "N"], "Y")
        if answer != "Y":
            raise UserStop()

    def run_test_upgrade(self):
        """
        Run a complete test upgrade on the current system
        Returns:

        """
        self._get_machine_name()
        self._check_upgrade_testing_machine()
        self._stop_ibex_server()
        self._remove_old_ibex()
        self._clean_up_desktop_ibex_training_folder()
        self._remove_settings()
        self._install_settings()
        self._install_ibex_server(True)
        self._install_ibex_client()
        self._upgrade_notepad_pp()


class UserPrompt(object):
    """
    A user pormpt object to ask the user questions.
    """
    def __init__(self, automatic, confirm_steps):
        """
        Initializer.
        Args:
            automatic: should the prompt ignore the user and use default responses
            confirm_steps: should the user confirm a step before running it; setting automatic overides this
        """
        self._automatic = automatic
        self._confirm_steps = confirm_steps

    def prompt(self, prompt_text, possibles, default, case_sensitive=False):
        """
        Prompt the user for an answer and check that answer. If in auto mode just answer the default
        Args:
            prompt_text: Text to prompt
            possibles: allowed answers
            default: default answer if in automatic mode
            case_sensitive: is the answer case sensitive

        Returns: answer from possibles

        """
        if self._automatic:
            print("{prompt} : {default}".format(prompt=prompt_text, default=default))
            return default

        return self._get_user_answer(prompt_text, possibles, case_sensitive)

    def _get_user_answer(self, prompt_text, possibles, case_sensitive=False):
        while True:
            answer = raw_input(prompt_text).strip()
            for possible in possibles:
                if answer == possible or (case_sensitive and possible.lower() == answer.lower()):
                    return possible
            print("Answer is not allowed can be one of ({0})".format(possibles))

    def confirm_step(self, step_text):
        """
        Confirm that a step should be done if in confirm steps mode
        Args:
            step_text: the text for the step

        Returns: true if step should continue; False otherwise

        """
        if not self._confirm_steps or self._automatic:
            return True
        return self._get_user_answer("Do step '{0}'? : ".format(step_text), ("Y", "N")) == "Y"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Upgrade the instrument.')

    parser.add_argument("--release_dir", dest="release_dir", default=None,
                        help="directory from which the client and server should be installed")
    parser.add_argument("--server_dir", default=None, help="Directory from which IBEX server should be installed")
    parser.add_argument("--client_dir", default=None, help="Directory from which IBEX client should be installed")
    parser.add_argument("--confirm_step", default=False, action="store_true",
                        help="Confirm each major action before performing it")
    parser.add_argument("--quiet", default=False, action="store_true",
                        help="Do not ask any questions just to the default.")

    args = parser.parse_args()

    if (args.release_dir is None) and (args.server_dir is None or args.client_dir is None):
        print("You must specify either the release directory or BOTH the server and client directories.")
        exit(2)

    if args.release_dir is None:
        server_dir = args.server_dir
        client_dir = args.client_dir
    else:
        server_dir = os.path.join(args.release_dir, "EPICS")
        client_dir = os.path.join(args.release_dir, "Client")

    prompt = UserPrompt(args.quiet, args.confirm_step)
    upgrade_instrument = UpgradeInstrument(prompt, server_dir, client_dir)

    try:
        upgrade_instrument.run_test_upgrade()
    except UserStop:
        print ("Stopping upgrade")
        exit(0)
    except ErrorInTask as error_in_run_ex:
        print("Error in upgrade: {0}".format(error_in_run_ex.message))
        exit(1)

    print ("Finished upgrade")
