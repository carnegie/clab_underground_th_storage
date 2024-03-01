# Borehole thermal energy storage

## Getting started

### Clone the repository

Clone this repository recursively (this ensures that the submodules are also cloned):

```git clone https://github.com/awongel/borehole_TES --recursive```

### Set up the environment

The setup described below uses [conda](https://docs.conda.io/en/latest/miniconda.html) for easy package management.

   ```cd borehole_TES```

   ```conda env create -f clab_pypsa/env.yaml```

   ```conda activate pypsa_table```

### Install a solver

Per default, the solver [Gurobi](https://www.gurobi.com/) will be installed. It requires a license to be used (free for academics). See instructions on [PyPSA website](https://pypsa.readthedocs.io/en/latest/installation.html#getting-a-solver-for-optimisation) for open source and other commercial solvers.

If you use a different solver, make sure to change the field "solver" in you case input file as well!

## Run the model

### Case input file

The network is defined in a case input file. The base case is defined in

```BTES_base_case.xlsx```

### Run the optimization

The optimization is run with the following command:

```python clab_pypsa/run_pypsa.py -f CASE_FILE```

so for the base case:

```python clab_pypsa/run_pypsa.py -f BTES_base_case.xlsx```

## Scan cost range

To scan a cost range for a component (currently BTES discharger capital cost), use the script

```python scan_btes_costs.py```

## Plot results

A simple plot can be created with the jupyter notebook

```plot_results.ipynb```




