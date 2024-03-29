import importlib.metadata
import json
import os
import sys
import tempfile
from unittest.mock import patch

from mocks import MockService
from octue.resources import Manifest
from octue.resources.service_backends import GCPPubSubBackend
from octue.utils.encoders import OctueJSONEncoder
from utils import ServicePatcher


class QuestionRecorder:
    def __init__(self):
        self.question = None

    def __call__(self, topic, data, retry, *args, **attributes):
        self.question = {"data": data.decode(), "attributes": attributes}


def record_question(recording_file_path):
    """Record a question produced by the current version of `octue` to the file at `RECORDING_FILE`. The question is
    recorded at the point of publishing to Pub/Sub.

    :param str recording_file_path:
    :return None:
    """
    backend = GCPPubSubBackend(project_name="my-project")
    child = MockService(backend=backend)

    # Avoid the mock child answering the question (only the question is needed here, not the response).
    child.answer = lambda *args, **kwargs: None

    parent = MockService(backend=backend, children={child.id: child})

    with tempfile.TemporaryDirectory() as temporary_directory:
        os.mkdir(os.path.join(temporary_directory, "path-within-dataset"))

        datafile_0_path = os.path.join(temporary_directory, "path-within-dataset", "a_test_file.csv")
        with open(datafile_0_path, "w") as f:
            f.write("blah")

        datafile_1_path = os.path.join(temporary_directory, "path-within-dataset", "another_test_file.csv")
        with open(datafile_1_path, "w") as f:
            f.write("blah")

        input_manifest = Manifest(datasets={"my_dataset": temporary_directory})

        service_patcher = ServicePatcher()
        publish_patch, question_recorder = _get_and_start_publish_patch()
        service_patcher.patches.append(publish_patch)

        with ServicePatcher():
            child.serve()

            parent.ask(
                child.id,
                input_values={"height": 4, "width": 72},
                input_manifest=input_manifest,
                allow_local_files=True,
            )

        serialised_question = json.dumps(
            {
                "parent_sdk_version": importlib.metadata.version("octue"),
                "question": question_recorder.question,
            },
            cls=OctueJSONEncoder,
        )

        with open(recording_file_path, "a") as f:
            f.write(serialised_question + "\n")


def _get_and_start_publish_patch():
    """Patch the mock publisher's `publish` method with a `QuestionRecorder` instance so questions are accessible in
    their just-before-sending form. This function facilitates patching `MockPublisher` across a wide range of previous
    versions of `octue`.

    :return (unittest.mock._patch, QuestionRecorder): the patch and the recorder are returned
    """
    publish_patch = patch("mocks.MockPublisher.publish", QuestionRecorder())
    return publish_patch, publish_patch.start()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        recording_file_path = sys.argv[1]
    else:
        recording_file_path = "recorded_questions.jsonl"

    print(f"Creating and recording question to {os.path.abspath(recording_file_path)!r}...")
    record_question(recording_file_path)
