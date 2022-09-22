import os

import click
from process_questions_across_versions import process_questions_across_versions


VERSIONS_TO_CHECK = [
    "0.37.0",
    "0.36.0",
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
    "0.23.6",
    "0.23.5",
    "0.23.4",
    "0.23.3",
    "0.23.2",
    "0.23.1",
    "0.23.0",
    "0.22.1",
    "0.22.0",
    "0.21.0",
    "0.20.0",
    "0.19.0",
    "0.18.2",
    "0.18.1",
    "0.18.0",
    "0.17.0",
    "0.16.0",
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
def process_questions(octue_sdk_repo_path, parent_versions, child_versions, questions_file, results_file):
    """Attempt to process each question from the questions file in a child running each specified version of the Octue
    SDK. Each parent-child version combination is marked as compatible if processing succeeds or incompatible if
    processing fails. The results are stored in a JSON file.
    """
    if parent_versions:
        parent_versions = parent_versions.split(",")
    else:
        parent_versions = VERSIONS_TO_CHECK

    if child_versions:
        child_versions = child_versions.split(",")
    else:
        child_versions = VERSIONS_TO_CHECK

    process_questions_across_versions(
        octue_sdk_repo_path,
        parent_versions=parent_versions,
        child_versions=child_versions,
        recording_file_path=os.path.abspath(questions_file),
        results_file_path=os.path.abspath(os.path.join(os.getcwd(), results_file)),
    )


if __name__ == "__main__":
    octue_compatibility_cli()
