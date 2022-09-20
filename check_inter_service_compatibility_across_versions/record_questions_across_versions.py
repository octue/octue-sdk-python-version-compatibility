import os
import sys

from utils import checkout_version, install_version, print_version_string, run_command_in_poetry_environment


QUESTION_RECORDING_SCRIPT_PATH = os.path.join(os.path.dirname(__file__), "record_question.py")

PARENT_VERSIONS = (
    "0.35.0",
    "0.34.1",
    "0.34.0",
    "0.33.0",
    "0.32.0",
    "0.31.0",
    "0.30.0",
    "0.29.11",
    "0.29.10",
    "0.29.9",
    "0.29.8",
    "0.29.7",
    "0.29.6",
    "0.29.5",
    "0.29.4",
    "0.29.3",
    "0.29.2",
    "0.29.1",
    "0.29.0",
    "0.28.2",
    "0.28.1",
    "0.28.0",
    "0.27.3",
    "0.27.2",
    "0.27.1",
    "0.27.0",
    "0.26.2",
    "0.26.1",
    "0.26.0",
    "0.25.0",
    "0.24.1",
    "0.24.0",
    "0.17.0",
    "0.16.0",  # The first version installable using `poetry` is `0.16.0`.
)


def record_questions_across_versions(recording_file_path):
    """Checkout, install, and record questions from the versions of `octue` given in `VERSIONS`. Questions are recorded
    to the file given in the `record_questions.py` script.

    :param str recording_file_path:
    :return None:
    """

    for parent_version in PARENT_VERSIONS:
        print_version_string(parent_version, perspective="parent")
        checkout_version(parent_version)
        install_version(parent_version)
        run_command_in_poetry_environment(f"python {QUESTION_RECORDING_SCRIPT_PATH} {recording_file_path}")


if __name__ == "__main__":
    os.chdir(sys.argv[1])

    if len(sys.argv) > 2:
        recording_file_path = sys.argv[2]
    else:
        recording_file_path = "recorded_questions.jsonl"

    record_questions_across_versions(recording_file_path)
