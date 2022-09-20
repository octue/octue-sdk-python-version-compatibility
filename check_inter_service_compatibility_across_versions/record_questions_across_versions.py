import os
import subprocess
import sys

from utils import checkout_version, get_poetry_environment_activation_script_path, install_version, print_version_string


QUESTION_RECORDING_SCRIPT_PATH = os.path.join(os.path.dirname(__file__), "record_question.py")

VERSIONS = (
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

    for version in VERSIONS:
        print_version_string(version, perspective="parent")
        checkout_version(version)
        install_version(version)

        subprocess.run(
            f"source {get_poetry_environment_activation_script_path()} && python {QUESTION_RECORDING_SCRIPT_PATH} "
            f"{recording_file_path}",
            shell=True,
        )


if __name__ == "__main__":
    if len(sys.argv) > 1:
        recording_file_path = sys.argv[1]
    else:
        recording_file_path = "recorded_questions.jsonl"

    record_questions_across_versions(recording_file_path)
