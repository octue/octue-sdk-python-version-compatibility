import base64
import json
import os
import sys
import tempfile

from utils import ServicePatcher


class MockAnalysis:
    """A mock Analysis object with just the output strands.

    :param any output_values:
    :param octue.resources.manifest.Manifest|None output_manifest:
    :return None:
    """

    def __init__(self, output_values="Hello! It worked!", output_manifest=None):
        self.output_values = output_values
        self.output_manifest = output_manifest


def process_question():
    from octue.resources import Datafile, Dataset, Manifest
    from octue.resources.service_backends import GCPPubSubBackend

    try:
        from octue.cloud.emulators._pub_sub import MESSAGES, MockService
    except ModuleNotFoundError:
        try:
            from old_mocks import MESSAGES, MockService
        except ModuleNotFoundError:
            from octue.cloud.emulators.pub_sub import MESSAGES, MockService

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

    question_file_path, results_file_path, child_sdk_version = sys.argv[1:4]

    with open(question_file_path) as f:
        question = json.load(f)

    parent_sdk_version = question["parent_sdk_version"]
    print(f"Processing question from version {parent_sdk_version}... ", end="", flush=False)
    question["question"]["data"] = base64.b64encode(question["question"]["data"].encode())

    backend = GCPPubSubBackend(project_name="octue-amy")
    child = MockService(backend=backend, run_function=lambda: None)
    MESSAGES[child.id + ".answers." + question["question"]["attributes"]["question_uuid"]] = []

    try:
        # Check serialised input manifests can be parsed.
        deserialised_question_data = json.loads(base64.b64decode(question["question"]["data"]).decode())
        Manifest.deserialise(json.loads(deserialised_question_data["input_manifest"]))

        # Check the rest of the question can be parsed.
        with ServicePatcher():
            child.serve()
            child.run_function = lambda *args, **kwargs: MockAnalysis(
                output_values=[1, 2, 3, 4],
                output_manifest=output_manifest,
            )
            child.answer(question["question"])

        save_result(results_file_path, parent_sdk_version, child_sdk_version, compatible=True)
        print("succeeded.")

    except Exception as error:
        print("failed.")
        save_result(results_file_path, parent_sdk_version, child_sdk_version, compatible=False)
        raise error


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
    process_question()
