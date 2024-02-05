import base64
import json
import logging
import os
import sys
import tempfile

import packaging.version

from utils import ServicePatcher


logger = logging.getLogger(__name__)


def process_question(question_file_path, results_file_path, child_sdk_version):
    """Using a child of the given SDK version, process the given question from a parent of a certain version to check
    the compatibility of the two versions. The result of this is added to the results file at the given path.

    :param str question_file_path:
    :param str results_file_path:
    :param str child_sdk_version:
    :return None:
    """
    from mocks import MESSAGES, MockService
    from octue.resources import Manifest
    from octue.resources.service_backends import GCPPubSubBackend

    with tempfile.TemporaryDirectory() as temporary_directory:
        os.mkdir(os.path.join(temporary_directory, "path-within-dataset"))

        datafile_0_path = os.path.join(temporary_directory, "path-within-dataset", "a_test_file.csv")
        with open(datafile_0_path, "w") as f:
            f.write("blah")

        datafile_1_path = os.path.join(temporary_directory, "path-within-dataset", "another_test_file.csv")
        with open(datafile_1_path, "w") as f:
            f.write("blah")

        output_manifest = Manifest(datasets={"output_dataset": temporary_directory})

        with open(question_file_path) as f:
            question = json.load(f)

        parent_sdk_version = question["parent_sdk_version"]
        print(f"Processing question from version {parent_sdk_version}... ", end="", flush=False)

        if question_crosses_0_51_0_divide(parent_sdk_version, child_sdk_version):
            error = TypeError("Services with version >= 0.51.0 are incompatible with services below this.")
            save_incompatible_result_and_raise(results_file_path, parent_sdk_version, child_sdk_version, error)

        child = MockService(
            backend=GCPPubSubBackend(project_name="octue-amy"),
            run_function=create_run_function(output_manifest),
        )

        # Create the mock answer topic.
        answer_topic_name = (
            child.id.replace("/", ".").replace(":", ".")
            + ".answers."
            + question["question"]["attributes"]["question_uuid"]
        )

        if not answer_topic_name.startswith("octue.services"):
            answer_topic_name = "octue.services." + answer_topic_name

        MESSAGES[answer_topic_name] = []

        try:
            test_compatibility(question, child)
        except Exception as error:
            save_incompatible_result_and_raise(results_file_path, parent_sdk_version, child_sdk_version, error)

        save_compatible_result(results_file_path, parent_sdk_version, child_sdk_version)


def create_run_function(output_manifest):
    """Create a run function that sends log messages back to the parent and produces simple output values and an output
    manifest.

    :return callable: the run function
    """
    from octue import Runner

    def mock_app(analysis):
        logger.info("Starting analysis.")
        analysis.output_values = [1, 2, 3, 4]
        analysis.output_manifest = output_manifest
        logger.info("Finished analysis.")

    twine = """
        {
            "input_values_schema": {
                "type": "object",
                "required": []
            },
            "input_manifest": {
                "datasets": {
                    "my_dataset": {}
                }
            },
            "output_values_schema": {},
            "output_manifest": {
                "datasets": {
                    "output_dataset": {}
                }
            }
        }
    """

    return Runner(app_src=mock_app, twine=twine).run


def test_compatibility(question, child):
    from octue.resources import Manifest

    # Check serialised input manifests can be deserialised.
    deserialised_question_data = json.loads(question["question"]["data"])

    try:
        Manifest.deserialise(deserialised_question_data["input_manifest"], from_string=True)
    except TypeError:
        Manifest.deserialise(deserialised_question_data["input_manifest"])

    # Encode the question data as it would be when received from Pub/Sub.
    question["question"]["data"] = base64.b64encode(question["question"]["data"].encode())

    # Check the rest of the question can be parsed.
    with ServicePatcher():
        child.serve()
        child.answer(question["question"])


def question_crosses_0_51_0_divide(parent_sdk_version, child_sdk_version):
    return (
        packaging.version.parse(parent_sdk_version) >= packaging.version.parse("0.51.0")
        and packaging.version.parse(child_sdk_version) < packaging.version.parse("0.51.0")
    ) or (
        packaging.version.parse(child_sdk_version) >= packaging.version.parse("0.51.0")
        and packaging.version.parse(parent_sdk_version) < packaging.version.parse("0.51.0")
    )


def save_incompatible_result_and_raise(results_file_path, parent_sdk_version, child_sdk_version, error):
    print("failed.")
    _save_result(results_file_path, parent_sdk_version, child_sdk_version, compatible=False)
    raise error


def save_compatible_result(results_file_path, parent_sdk_version, child_sdk_version):
    print("succeeded.")
    _save_result(results_file_path, parent_sdk_version, child_sdk_version, compatible=True)


def _save_result(results_file_path, parent_sdk_version, child_sdk_version, compatible):
    try:
        with open(results_file_path, "r") as f:
            results = json.load(f)
    except FileNotFoundError:
        results = {}

    parent_row = results.get(parent_sdk_version, {})
    parent_row[child_sdk_version] = compatible
    results[parent_sdk_version] = parent_row

    with open(results_file_path, "w") as f:
        json.dump(results, f)


if __name__ == "__main__":
    question_file_path, results_file_path, child_sdk_version = sys.argv[1:4]
    process_question(question_file_path, results_file_path, child_sdk_version)
