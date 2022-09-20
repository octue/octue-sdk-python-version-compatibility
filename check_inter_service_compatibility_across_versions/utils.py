import os
import subprocess
from unittest.mock import patch


class ServicePatcher:
    def __init__(self, patches=None):
        from old_mocks import MockSubscriber, MockSubscription, MockTopic

        self.patches = patches or [
            patch("octue.cloud.pub_sub.service.Topic", new=MockTopic),
            patch("octue.cloud.pub_sub.service.Subscription", new=MockSubscription),
            patch("google.cloud.pubsub_v1.SubscriberClient", new=MockSubscriber),
        ]

    def __enter__(self):
        """Start the patches and return the mocks they produce.

        :return list(unittest.mock.MagicMock):
        """
        return [patch.start() for patch in self.patches]

    def __exit__(self, *args, **kwargs):
        """Stop the patches.

        :return None:
        """
        for p in self.patches:
            p.stop()


def print_version_string(version, perspective):
    version_string = f"\n{perspective.upper()} VERSION {version}"
    print(version_string)
    print("=" * (len(version_string) - 1))


def checkout_version(version):
    print("Checking out version...")
    checkout_process = subprocess.run(["git", "checkout", version], capture_output=True)

    if checkout_process.returncode != 0:
        raise ChildProcessError(
            f"Git checkout of version {version} failed.\n\n{checkout_process.stdout.decode()}\n\n"
            f"{checkout_process.stderr.decode()}"
        )


def install_version(version):
    print("Installing version...")
    install_process = subprocess.run(["poetry", "install", "--all-extras"], capture_output=True)

    if install_process.returncode != 0:
        raise ChildProcessError(
            f"Installation of version {version} failed.\n\n{install_process.stdout.decode()}\n\n"
            f"{install_process.stderr.decode()}"
        )


def get_poetry_environment_activation_script_path():
    poetry_env_path = subprocess.run(["poetry", "env", "info", "--path"], capture_output=True).stdout.decode().strip()
    return os.path.join(poetry_env_path, "bin", "activate")


def run_command_in_poetry_environment(command):
    return subprocess.run(f"source {get_poetry_environment_activation_script_path()} && {command}", shell=True)
