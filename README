# Seqera Platform Tools

## extract_metadata.py

This script can be used to extract workflow/run metadata (e.g. date created, submitted, completed, params used, etc) from Seqera Platform into a JSON file.

The script interacts with the Seqera Platform CLI to extract workflow metadata.
It is designed to be run from the command line, accepting parameters to specify
the workspace, workflow ID, and output path for the resulting JSON.

### Usage

```
python extract_metadata.py -w <workspace_name> -id <workflow_id> -o <output_file.json>

Arguments:
    -w, --workspace     The name of the workspace on the Seqera Platform.
    -id, --workflow_id  The unique identifier for the workflow.
    -o, --output        The path to the output JSON file that will be created with workflow information.

Example:
    python extract_metadata.py -w myworkspace -id 12345 -o workflow_details.json
```

### Requirements

1. You will need to have an account on Seqera Platform (see [Plans and pricing](https://cloud.tower.nf/pricing/)).

2. The script interacts with Seqera Platform using the `seqerakit` package. You must have this installed in your
   environment with `pip install seqerakit`.

`seqerakit` requires the following dependencies:

a. [Seqera Platform CLI](https://github.com/seqeralabs/tower-cli#1-installation)

b. [Python (`>=3.8`)](https://www.python.org/downloads/)

c. [PyYAML](https://pypi.org/project/PyYAML/)

You can find more info on the `seqerakit` package [here](https://github.com/seqeralabs/seqera-kit#-seqerakit).

3. You will need to create a Seqera Platform access token using the [Seqera Platform](https://tower.nf/) web interface via the **Your Tokens** page in your profile.

`seqerakit` reads this token from the environment variable `TOWER_ACCESS_TOKEN`. Please export it into your terminal as shown below:

```bash
export TOWER_ACCESS_TOKEN=<your access token>
```
