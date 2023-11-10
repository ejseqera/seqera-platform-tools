"""
This script interacts with the Seqera Platform CLI to extract workflow metadata in a JSON file.
It is designed to be run from the command line, accepting parameters to specify
the workspace, workflow ID, and output path for the resulting JSON.

The script relies on the seqerakit package to interact with the CLI using Python and must
be run in an environment where this package is installed and properly configured. To install,
run `pip install seqerakit` in your environment.

Usage:
    python extract_metadata.py -w <workspace_name> -id <workflow_id> -o <output_file.json>

Arguments:
    -w, --workspace     The name of the workspace on the Seqera Platform.
    -id, --workflow_id  The unique identifier for the workflow.
    -o, --output        The path to the output JSON file that will be created with workflow information.

Example:
    python extract_metadata.py -w myworkspace -id 12345 -o workflow_details.json

Note: Ensure that the `TOWER_ACCESS_TOKEN` has been set in your environment before running the script.
"""

from seqerakit import seqeraplatform
import argparse
import json
import tarfile
from typing import Any, Dict, List
from argparse import Namespace
import logging


def parse_args() -> Namespace:
    """
    Parse command-line arguments.

    Returns:
        Namespace: An argparse.Namespace object containing the arguments 'output',
        'workspace', and 'workflow_id'.
    """
    parser = argparse.ArgumentParser(
        description="Extract and process Seqera Platform workflow metadata."
    )
    parser.add_argument(
        "-l",
        "--log_level",
        default="INFO",
        choices=("CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"),
        help="The desired log level (default: INFO).",
        type=str.upper,
    )
    parser.add_argument(
        "-o", "--output", type=str, required=True, help="Output filename for JSON file"
    )
    parser.add_argument(
        "-w",
        "--workspace",
        type=str,
        required=True,
        help="Seqera Platform workspace name",
    )
    parser.add_argument(
        "-id",
        "--workflow_id",
        type=str,
        required=True,
        help="Seqera Platform workflow ID",
    )
    return parser.parse_args()


def get_runs_dump(
    seqera: seqeraplatform.SeqeraPlatform, workflow_id: str, workspace: str
) -> str:
    """
    Run the `tw runs dump` command for a given workflow ID within a workspace and download archive as a tar.gz file.

    Args:
        seqera (SeqeraPlatform): An instance of the SeqeraPlatform class that interacts with the Seqera Platform CLI.
        workflow_id (str): The ID of the workflow to retrieve run data for.
        workspace (str): The name of the workspace in which the workflow was run.

    Returns:
        str: The name of the downloaded tar.gz file.
    """
    output_file = f"{workflow_id}.tar.gz"
    seqera.runs("dump", "-id", workflow_id, "-o", output_file, "-w", workspace)
    return output_file


def extract_workflow_data(tar_file: str, *file_names: str) -> Dict[str, Any]:
    """
    Extract specified files from the tar archive generated by `tw runs dump` and load their contents as JSON.

    Args:
        tar_file (str): The path to the tar.gz file from `tw runs dump` to extract.
        *file_names (str): The names of the files to extract from the tar archive as variable arguments
    Returns:
        dict: A dictionary where keys are the file names and values are the loaded JSON data.
    """
    with tarfile.open(tar_file, "r:gz") as tar:
        extracted_data = {}
        for member in tar.getmembers():
            if member.name in file_names:
                extracted_data[member.name] = json.load(tar.extractfile(member))
        return extracted_data


def parse_json(json_data: Dict[str, Any], keys_list: List[str]) -> Dict[str, Any]:
    """
    Parse a JSON object and return the values for the specified keys, including nested keys.

    Args:
        json_data (dict): The JSON input data to parse.
        keys_list (list): A list of keys to extract values from the JSON data. Nested keys should be
                          denoted with a period.

    Returns:
        dict: A dictionary of extracted key-value pairs from the JSON data.
    """
    update_dict = {}
    for key in keys_list:
        try:
            value = json_data
            for part in key.split("."):
                value = value.get(part)
                if value is None:
                    break
            else:
                update_dict[key] = value
        except (KeyError, TypeError):
            update_dict[key] = None
    return update_dict


def main():
    args = parse_args()
    logging.basicConfig(level=args.log_level)

    seqera = seqeraplatform.SeqeraPlatform()

    logging.info("Getting workflow run data...")
    tar_file = get_runs_dump(seqera, args.workflow_id, args.workspace)

    logging.info("Extracting workflow metadata...")
    extracted_data = extract_workflow_data(
        tar_file, "workflow-load.json", "workflow.json"
    )
    workflow_load = extracted_data.get("workflow-load.json")
    workflow = extracted_data.get("workflow.json")

    if workflow_load is None or workflow is None:
        raise ValueError("Required workflow files not found in the tar archive.")

    # Specify keys for the required metadata fields for each workflow file
    workflow_load_keys = [
        "cpuEfficiency",
        "memoryEfficiency",
        "cost",
        "readBytes",
        "writeBytes",
        "peakCpus",
        "peakMemory",
        "dateCreated",
        "lastUpdated",
    ]

    workflow_keys = [
        "status",
        "repository",
        "id",
        "submit",
        "start",
        "complete",
        "dateCreated",
        "lastUpdated",
        "runName",
        "projectName",
        "commitId",
        "sessionId",
        "userName",
        "commandLine",
        "params",
        "configFiles",
        "configText",
        "duration",
        "params.input",
        "params.outdir",
    ]

    # Get json data from both input files into one dictionary
    logging.info("Parsing workflow metadata...")
    json_data = {
        **parse_json(workflow_load, workflow_load_keys),
        **parse_json(workflow, workflow_keys),
    }

    logging.info("Writing workflow metadata to JSON file...")
    with open(args.output, "w") as outfile:
        json.dump(json_data, outfile, indent=4)

    logging.info(f"Workflow metadata written to {args.output}.")


if __name__ == "__main__":
    main()
