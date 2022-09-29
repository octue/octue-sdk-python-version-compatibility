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

### Pre-requisites
 - `poetry` installed on your system
 - An up-to-date clone of the `octue-sdk-python` repo
 - An up-to-date clone of this repo
 - Change directory into this repo

### Recording questions from parents
You can record questions from parents running different versions of Octue SDK by using the `record-questions` CLI
command.

```shell
python cli.py record-questions --help
```

```
Usage: cli.py record-questions [OPTIONS]

  Record questions from parents running each of the given Octue SDK versions
  into a file for later processing.

Options:
  --octue-sdk-repo-path DIRECTORY
                                  The path to a local clone of the `octue-sdk-
                                  python` repository.  [default: .]

  --parent-versions TEXT          A comma-separated list of parent versions to
                                  record questions from e.g. '0.35.0,0.36.0'.
                                  The default is all versions of the SDK from
                                  0.16.0 upwards.

  --questions-file FILE           The path to a JSONL (JSON lines) file to
                                  record questions from different Octue SDK
                                  versions.  [default:
                                  recorded_questions.jsonl]

  -h, --help                      Show this message and exit.
```

### Processing questions in children
You can process any number of questions that have already been recorded to a file by the
`record_questions_across_versions.py` script by using the `process-questions` CLI command. Running it should take around
40 mins to 1 hour and produce a matrix of compatibilities in an output JSON file. The rows are the parent version, the
columns are the child version, and the elements are a boolean indicating whether a question from the parent can be
processed by the child.

```shell
python cli.py process-questions --help
```

```
Usage: cli.py process-questions [OPTIONS]

  Attempt to process each question from the questions file in a child
  running each specified version of the Octue SDK. Each parent-child version
  combination is marked as compatible if processing succeeds or incompatible
  if processing fails. The results are stored in a JSON file.

Options:
  --octue-sdk-repo-path DIRECTORY
                                  The path to a local clone of the `octue-sdk-
                                  python` repository.  [default: .]

  --parent-versions TEXT          A comma-separated list of parent versions to
                                  test (i.e. process questions from) e.g.
                                  '0.35.0,0.36.0'. The default is all versions
                                  of the SDK from 0.16.0 upwards.

  --child-versions TEXT           A comma-separated list of child versions to
                                  test (i.e. process questions in) e.g.
                                  '0.35.0,0.36.0'. The default is all versions
                                  of the SDK from 0.16.0 upwards.

  --untagged-child-version-branches TEXT
                                  A comma-separated list of untagged child
                                  versions mapped to their branches. This
                                  option allows unreleased version candidates
                                  to have their compatibility tested against
                                  released versions by providing the branch to
                                  check out when testing them.

  --questions-file FILE           The path to the JSONL (JSON lines) file
                                  containing recorded questions from different
                                  Octue SDK versions.  [default:
                                  recorded_questions.jsonl]

  --results-file FILE             The path to a JSON file to store the results
                                  in.  [default:
                                  version_compatibility_results.json]

  -h, --help                      Show this message and exit.
```
