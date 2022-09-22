import json
import os
import tempfile

from utils import checkout_version, install_version, print_version_string, run_command_in_poetry_environment


QUESTION_PROCESSING_SCRIPT_PATH = os.path.join(os.path.dirname(__file__), "process_question.py")


def process_questions_across_versions(
    octue_sdk_repo_path,
    parent_versions,
    child_versions,
    recording_file_path,
    results_file_path,
):
    os.chdir(octue_sdk_repo_path)

    with open(recording_file_path) as f:
        questions = f.readlines()

    for child_version in child_versions:
        print_version_string(child_version, perspective="child")
        checkout_version(child_version)
        install_version(child_version)

        for question in questions:
            parent_sdk_version = json.loads(question)["parent_sdk_version"]

            if parent_sdk_version not in parent_versions:
                continue

            with tempfile.NamedTemporaryFile() as temporary_file:
                with open(temporary_file.name, "w") as f:
                    f.write(question)

                process = run_command_in_poetry_environment(
                    f"python {QUESTION_PROCESSING_SCRIPT_PATH} {temporary_file.name} {results_file_path} {child_version}"
                )

                if process.returncode != 0:
                    print(
                        f"Questions from parent SDK version {parent_sdk_version} are incompatible with child SDK "
                        f"version {child_version}."
                    )
