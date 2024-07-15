# TeamCooliest

## Installation

Create a conda environment from the `env.yml` file and activate it. This may be faster with [mamba](https://mamba.readthedocs.io/en/latest/).

```bash
conda env create -f env.yml
conda activate TeamCooliest
```

Install model as editable package:

```bash
pip install -e .
```

Run model from command line:

```bash
tc-model -h
```

Run GUI from command line

```bash
tc-gui
```

## File Structure

Subject to change.
It may be better to group parallel CFD and model cases than separate them in the `data` directory.

- data
  - CFD
  - model

- src
  - CFD
  - GUI
  - model

## Branch Organization

- main (runnable use case)
  - develop (merge subtask developments and test)
    - develop-gui
    - develop-cfd
    - develop-model

Individual user branches can stem from develop-{subtask}
