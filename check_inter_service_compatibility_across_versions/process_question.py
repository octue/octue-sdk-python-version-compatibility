import base64
import json
import os
import sys
import tempfile

from utils import ServicePatcher


def process_question(question_file_path, results_file_path, child_sdk_version):
    """Using a child of the given SDK version, process the given question from a parent of a certain version to check
    the compatibility of the two versions. The result of this is added to the results file at the given path.

    :param str question_file_path:
    :param str results_file_path:
    :param str child_sdk_version:
    :return None:
    """
    from mocks import MESSAGES, MockAnalysis, MockService
    from octue.resources import Datafile, Dataset, Manifest
    from octue.resources.service_backends import GCPPubSubBackend

    path = tempfile.NamedTemporaryFile().name

    output_manifest = Manifest(
        datasets={
            "my_dataset": Dataset(
                path=path,
                files=[
                    Datafile(path=os.path.join(path, "path-within-dataset", "a_test_file.csv")),
                    Datafile(path=os.path.join(path, "path-within-dataset", "another_test_file.csv")),
                ],
            )
        }
    )

    with open(question_file_path) as f:
        question = json.load(f)

    parent_sdk_version = question["parent_sdk_version"]
    print(f"Processing question from version {parent_sdk_version}... ", end="", flush=False)

    child = MockService(
        backend=GCPPubSubBackend(project_name="octue-amy"),
        run_function=lambda *args, **kwargs: MockAnalysis(output_values=[1, 2, 3, 4], output_manifest=output_manifest),
    )

    # Create the mock answer topic.
    MESSAGES[child.id + ".answers." + question["question"]["attributes"]["question_uuid"]] = []

    try:
        test_compatibility(question, child)
    except Exception as error:
        print("failed.")
        save_result(results_file_path, parent_sdk_version, child_sdk_version, compatible=False)
        raise error

    save_result(results_file_path, parent_sdk_version, child_sdk_version, compatible=True)
    print("succeeded.")


def test_compatibility(question, child):
    from octue.resources import Manifest

    # Check serialised input manifests can be deserialised.
    deserialised_question_data = json.loads(question["question"]["data"])
    Manifest.deserialise(deserialised_question_data["input_manifest"], from_string=True)

    # Encode the question data as it would be when received from Pub/Sub.
    question["question"]["data"] = base64.b64encode(question["question"]["data"].encode())

    # Check the rest of the question can be parsed.
    with ServicePatcher():
        child.serve()
        child.answer(question["question"])


def save_result(results_file_path, parent_sdk_version, child_sdk_version, compatible):
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
