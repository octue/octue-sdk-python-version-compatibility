import os

from .utils import checkout_version, install_version, print_version_string, run_command_in_poetry_environment


QUESTION_RECORDING_SCRIPT_PATH = os.path.join(os.path.dirname(__file__), "record_question.py")


def record_questions_across_versions(octue_sdk_repo_path, parent_versions, recording_file_path):
    """Checkout and install the given parent versions of the Octue SDK and record questions from them to the given file.

    :param str octue_sdk_repo_path:
    :param list parent_versions:
    :param str recording_file_path:
    :return None:
    """
    os.chdir(octue_sdk_repo_path)

    for parent_version in parent_versions:
        print_version_string(parent_version, perspective="parent")
        checkout_version(parent_version)
        install_version(parent_version)
        run_command_in_poetry_environment(f"python {QUESTION_RECORDING_SCRIPT_PATH} {recording_file_path}")
