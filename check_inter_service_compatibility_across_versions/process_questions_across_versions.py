import json
import os
import sys
import tempfile

from utils import checkout_version, install_version, print_version_string, run_command_in_poetry_environment


QUESTION_PROCESSING_SCRIPT_PATH = os.path.join(os.path.dirname(__file__), "process_question.py")

CHILD_VERSIONS = [
    "0.35.0",
    # "0.34.1",
    # "0.34.0",
    # "0.33.0",
    # "0.32.0",
    # "0.31.0",
    # "0.30.0",
    # "0.29.11",
    # "0.29.10",
    # "0.29.9",
    # "0.29.8",
    # "0.29.7",
    # "0.29.6",
    # "0.29.5",
    # "0.29.4",
    # "0.29.3",
    # "0.29.2",
    # "0.29.1",
    # "0.29.0",
    # "0.28.2",
    # "0.28.1",
    # "0.28.0",
    # "0.27.3",
    # "0.27.2",
    # "0.27.1",
    # "0.27.0",
    # "0.26.2",
    # "0.26.1",
    # "0.26.0",
    # "0.25.0",
    # "0.24.1",
    # "0.24.0",
    # "0.17.0",
    "0.16.0",
]


def process_questions_across_versions(recording_file_path):
    with open(recording_file_path) as f:
        questions = f.readlines()

    for child_version in CHILD_VERSIONS:
        print_version_string(child_version, perspective="child")
        checkout_version(child_version)
        install_version(child_version)

        for question in questions:
            with tempfile.NamedTemporaryFile() as temporary_file:
                with open(temporary_file.name, "w") as f:
                    f.write(question)

                process = run_command_in_poetry_environment(
                    f"python {QUESTION_PROCESSING_SCRIPT_PATH} {temporary_file.name}"
                )

                if process.returncode != 0:
                    parent_sdk_version = json.loads(question)["parent_sdk_version"]

                    print(
                        f"Questions from parent SDK version {parent_sdk_version} are incompatible with child SDK "
                        f"version {child_version}."
                    )


if __name__ == "__main__":
    if len(sys.argv) > 1:
        recording_file_path = sys.argv[1]
    else:
        recording_file_path = "recorded_questions.jsonl"

    process_questions_across_versions(recording_file_path)
