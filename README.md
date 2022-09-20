# Octue SDK Python - Version Compatibility

Scripts for automated checking of inter-service compatibility between different versions of the Octue Python SDK
(`octue`).

## Library breaking changes vs. inter-service communication breaking changes
`octue` is a beta package that's version controlled using semantic versioning, meaning that changes in the minor version
number indicated a breaking change in the package. There are two types of breaking changes to keep track of:
- Breaking changes to the public interface of the SDK - i.e. classes, methods, functions, and the CLI from the package
  when it's used as a library that are imported or otherwise explicitly used. These changes are fairly easy to keep
  track of
- Breaking changes to communication between services running different versions of the SDK - i.e. changing message
  formats, message parsing, and object serialisation/deserialisation (e.g. manifests). These changes are harder to keep
  track of because, sometimes, changes made to non-public parts of the SDK (that therefore don't constitute a breaking
  change to the public interface and high-level use of the package) can break communication between services running
  different versions.

## Testing version compatibility between services
This repository provides scripts that automatically test communication between services running different versions. It
does this by producing questions for each version given to it and checking whether an error is raised when each question
is processed by each version.

## Why isn't the code contained in this repository in the `octue-sdk-python` repository instead?
The scripts have to be version controlled separately to `octue-sdk-python` because each version of `octue` has to be
checked out before it's installed for testing, meaning the scripts disappear as soon as a non-latest version is checked
out.

## Usage
Ensure `poetry` is installed on your system. Then, run:

```shell
git clone https://github.com/octue/octue-sdk-python-version-compatibility.git
cd check_inter_service_compatibility_across_versions
python record_questions_across_versions.py <path-to-octue-sdk-python-repo> <path-for-recorded-questions.jsonl>
python process_questions_across_versions.py <path-to-octue-sdk-python-repo> <path-for-recorded-questions.jsonl>
```

When this has finished (it should take around 40 mins to 1 hour), a matrix of compatibilities will be available in
`version_compatibility_results.json`. The rows are the parent version, the columns are the child version, and the
elements are a boolean indicating whether a question from the parent can be processed by the child.
