import os

import click

from inter_service_compatibility.process_questions_across_versions import process_questions_across_versions
from inter_service_compatibility.record_questions_across_versions import record_questions_across_versions


VERSIONS_TO_CHECK = [
    "0.52.0",
    "0.51.0",
    "0.50.1",
    "0.50.0",
    "0.49.2",
    "0.49.1",
    "0.49.0",
    "0.48.0",
    "0.47.2",
    "0.47.1",
    "0.47.0",
    "0.46.3",
    "0.46.2",
    "0.46.1",
    "0.46.0",
    "0.45.0",
    "0.44.0",
    "0.43.7",
    "0.43.6",
    "0.43.5",
    "0.43.4",
    "0.43.3",
    "0.43.2",
    "0.43.1",
    "0.43.0",
    "0.42.1",
    "0.42.0",
    "0.41.1",
    "0.41.0",
    "0.40.2",
    "0.40.1",
    "0.40.0",
    "0.39.0",
    "0.38.1",
    "0.38.0",
    "0.37.0",
    "0.36.0",
    "0.35.0",
    "0.34.1",
    "0.34.0",
    "0.33.0",
    "0.32.0",
    "0.31.0",
    "0.30.0",
]


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
def octue_compatibility_cli():
    """Check communication compatibility between services running different versions of the Octue SDK."""


@octue_compatibility_cli.command()
@click.option(
    "--octue-sdk-repo-path",
    type=click.Path(file_okay=False, exists=True),
    default=".",
    show_default=True,
    help="The path to a local clone of the `octue-sdk-python` repository.",
)
@click.option(
    "--parent-versions",
    type=str,
    default=None,
    help="A comma-separated list of parent versions to record questions from e.g. '0.35.0,0.36.0'. The default is all "
    "versions of the SDK from 0.16.0 upwards.",
)
@click.option(
    "--questions-file",
    type=click.Path(dir_okay=False),
    default="recorded_questions.jsonl",
    show_default=True,
    help="The path to a JSONL (JSON lines) file to record questions from different Octue SDK versions.",
)
@click.option(
    "-v",
    "--verbose",
    default=False,
    is_flag=True,
    show_default=True,
    help="If provided, show all shell output.",
)
def record_questions(octue_sdk_repo_path, parent_versions, questions_file, verbose):
    """Record questions from parents running each of the given Octue SDK versions into a file for later processing."""
    parent_versions = parse_versions_or_get_defaults(parent_versions)

    record_questions_across_versions(
        octue_sdk_repo_path=octue_sdk_repo_path,
        parent_versions=parent_versions,
        recording_file_path=questions_file,
        verbose=verbose,
    )


@octue_compatibility_cli.command()
@click.option(
    "--octue-sdk-repo-path",
    type=click.Path(file_okay=False, exists=True),
    default=".",
    show_default=True,
    help="The path to a local clone of the `octue-sdk-python` repository.",
)
@click.option(
    "--parent-versions",
    type=str,
    default=None,
    help="A comma-separated list of parent versions to test (i.e. process questions from) e.g. '0.35.0,0.36.0'. The "
    "default is all versions of the SDK from 0.16.0 upwards.",
)
@click.option(
    "--child-versions",
    type=str,
    default=None,
    show_default=True,
    help="A comma-separated list of child versions to test (i.e. process questions in) e.g. '0.35.0,0.36.0'. The "
    "default is all versions of the SDK from 0.16.0 upwards.",
)
@click.option(
    "--untagged-child-version-branches",
    type=str,
    default=None,
    show_default=True,
    help="A comma-separated list of untagged child versions mapped to their branches. This option allows unreleased "
    "version candidates to have their compatibility tested against released versions by providing the branch to check "
    "out when testing them.",
)
@click.option(
    "--questions-file",
    type=click.Path(exists=True, dir_okay=False),
    default="recorded_questions.jsonl",
    show_default=True,
    help="The path to the JSONL (JSON lines) file containing recorded questions from different Octue SDK versions.",
)
@click.option(
    "--results-file",
    type=click.Path(dir_okay=False),
    default="version_compatibility_results.json",
    show_default=True,
    help="The path to a JSON file to store the results in.",
)
@click.option(
    "-v",
    "--verbose",
    default=False,
    is_flag=True,
    show_default=True,
    help="If provided, show all shell output.",
)
def process_questions(
    octue_sdk_repo_path,
    parent_versions,
    child_versions,
    untagged_child_version_branches,
    questions_file,
    results_file,
    verbose,
):
    """Attempt to process each question from the questions file in a child running each specified version of the Octue
    SDK. Each parent-child version combination is marked as compatible if processing succeeds or incompatible if
    processing fails. The results are stored in a JSON file.
    """
    parent_versions = parse_versions_or_get_defaults(parent_versions)
    child_versions = parse_versions_or_get_defaults(child_versions)

    if untagged_child_version_branches:
        raw_untagged_child_version_branches = untagged_child_version_branches.split(",")
        untagged_child_version_branches = {}

        for element in raw_untagged_child_version_branches:
            version, branch = element.split("=")
            untagged_child_version_branches[version] = branch

    process_questions_across_versions(
        octue_sdk_repo_path=octue_sdk_repo_path,
        parent_versions=parent_versions,
        child_versions=child_versions,
        recording_file_path=os.path.abspath(questions_file),
        results_file_path=os.path.abspath(os.path.join(os.getcwd(), results_file)),
        untagged_child_version_branches=untagged_child_version_branches,
        verbose=verbose,
    )


def parse_versions_or_get_defaults(versions):
    """Parse a comma-separated string of semantic versions to a list or get the default versions if none are given.

    :param str|None versions: a comma-separated str of semantic versions
    :return list(str):
    """
    if versions:
        return versions.split(",")
    return VERSIONS_TO_CHECK


if __name__ == "__main__":
    octue_compatibility_cli()
