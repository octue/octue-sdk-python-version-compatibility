import json
import os
import tempfile

from .utils import checkout_version, install_version, print_version_string, run_command_in_poetry_environment


QUESTION_PROCESSING_SCRIPT_PATH = os.path.join(os.path.dirname(__file__), "process_question.py")


def process_questions_across_versions(
    octue_sdk_repo_path,
    parent_versions,
    child_versions,
    recording_file_path,
    results_file_path,
    untagged_child_version_branches=None,
    verbose=False,
):
    """Checkout and install the given child versions of the Octue SDK and process questions from the given parent
    versions to check if the parent-child combination is compatible. The results are recorded in a file.

    :param str octue_sdk_repo_path:
    :param list parent_versions:
    :param list child_versions:
    :param str recording_file_path:
    :param str results_file_path:
    :param dict|None untagged_child_version_branches: a mapping of branch names to untagged child versions
    :param bool verbose:
    :return None:
    """
    os.chdir(octue_sdk_repo_path)

    with open(recording_file_path) as f:
        questions = f.readlines()

    if not questions:
        raise ValueError("No questions have been found in the questions file at %r.", recording_file_path)

    for child_version in child_versions:
        print_version_string(child_version, perspective="child")

        if untagged_child_version_branches and child_version in untagged_child_version_branches:
            branch_name = untagged_child_version_branches[child_version]
            print(f"Using {branch_name!r} branch instead of version {child_version}.")
            checkout_version(branch_name, capture_output=not verbose)
        else:
            checkout_version(child_version, capture_output=not verbose)

        install_version(child_version, capture_output=not verbose)

        for question in questions:
            parent_sdk_version = json.loads(question)["parent_sdk_version"]

            if verbose and parent_sdk_version not in parent_versions:
                print(f"Version {parent_sdk_version!r} not included in {parent_versions!r}.")
                continue

            with tempfile.NamedTemporaryFile() as temporary_file:
                with open(temporary_file.name, "w") as f:
                    f.write(question)

                process = run_command_in_poetry_environment(
                    f"python {QUESTION_PROCESSING_SCRIPT_PATH} {temporary_file.name} {results_file_path} {child_version}",
                )

                if process.returncode != 0:
                    print(
                        f"Questions from parent SDK version {parent_sdk_version} maybe be incompatible with child SDK "
                        f"version {child_version}.\n{process.stdout or ''}\n{process.stderr or ''}"
                    )
