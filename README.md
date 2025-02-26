# Borehole thermal energy storage

## Getting started

### Clone the repository

Clone this repository recursively (this ensures that the submodules are also cloned):

```git clone https://github.com/carnegie/clab_underground_th_storage.git --recursive```

### Set up the environment

The setup described below uses [conda](https://docs.conda.io/en/latest/miniconda.html) for easy package management.

   ```cd clab_underground_th_storage```

   ```conda env create -f table_pypsa/env.yaml```

   ```conda activate table_pypsa_env```

### Install a solver

Per default, the solver [Gurobi](https://www.gurobi.com/) will be installed. It requires a license to be used (free for academics). See instructions on [PyPSA website](https://pypsa.readthedocs.io/en/latest/installation.html#getting-a-solver-for-optimisation) for open source and other commercial solvers.

If you use a different solver, make sure to change the field "solver" in you case input file as well!

## Run the model

### Case input file

The network is defined in a case input file. The input files for this paper are defined in

```input_files/case_files/```

### Data input files

Wind and solar capacity factors are obtained with [Atlite](https://github.com/PyPSA/atlite).

[Cleaned demand data](https://github.com/truggles/EIA_Cleaned_Hourly_Electricity_Demand_Data/tree/v1.4) for the US is obtained with a scanning and imputation tool based on EIA data.

The hourly electricity cost is obtained from an optimization of the base case without the undergound thermal storage in the system (see ```input_files/case_files/BTES_base_case_no_btes.xlsx```).

All of these files can be found in 
```input_files/```

### Run the optimization

The optimization for a single input file is run with the following command:

```python table_pypsa/run_pypsa.py -f CASE_FILE```

so for the base case:

```python table_pypsa/run_pypsa.py -f input_files/case_files/BTES_base_case.xlsx```


## Scan cost range

To scan a range of cost factors (all costs of all components of this technology will be scaled by the cost factor) for a technology, use the script

```python scan_costs.py -f CASE_FILE -t TECHNOLOGY -c COST_FACTORS```

where
 - ```CASE_FILE``` is the input case file to run the cost scan on
 - ```TECHNOLOGY``` is the technology for which the cost is scaled
 - ```COST_FACTORS``` are the cost factors (or cost factor) by which the technology cost is scaled in a comma-separated list.

For example to scan the BTES costs by 0.2 and 0.5 based on the base case (giving two output files), do

```python scan_costs.py -f input_files/case_files/BTES_base_case.xlsx -t BTES -c 0.2,0.5```

All price-maker results are obtained with this cost scan (Fig.2 and price-maker results in Fig.3).
To produce the smooth cost range scans, we ran the cost scan with the following value: 1e-6, 0.08, 0.16, 0.25, 0.33, 0.41, 0.49, 0.58, 0.66, 0.74, 0.82, 0.91, 0.99, 1.07, 1.15, 1.24, 1.32, 1.4, 1.48, 1.57, 1.65.

## Price-taker results

For the price taker results, we first need to obtain the electricity costs from the price-maker cases without underground thermal storage in the system with

```python table_pypsa/run_pypsa.py -f input_files/case_files/BTES_base_case_no_btes.xlsx```

For the scans where the costs of fossil generators or renewables were varied (SI Fig. 2), do

```python scan_costs.py -f input_files/case_files/BTES_base_case_no_btes.xlsx -t TECHNOLOGY -c COST_VALUES```
where TECHNOLOGY is either ```fossil``` or ```renewable``` and COST_VALUES are the same as listed above.

To then run the price-taker cases, for the scan of underground thermal storage (Fig. 3), do

```python scan_costs.py -f input_files/case_files/BTES_price_taker.xlsx -t BTES -c COST_VALUES```

 and for the scan of fossil and renewables (SI Fig. 2)

```python scan_costs.py -f input_files/case_files/BTES_price_taker.xlsx -t TECHNOLOGY -c COST_VALUES --elec_cost```

where TECHNOLOGY is either ```fossil``` or ```renewable``` and COST_VALUES are the same as listed above.


## Plot results

Plots of the system costs and dispatch (Fig.2) can be created with the jupyter notebook

```plot_results.ipynb```

Plots of the price taker/price maker comparison (Fig.3) can be created with the jupyter notebook

```plot_price_taker.ipynb```

[![DOI](https://zenodo.org/badge/608204677.svg)](https://doi.org/10.5281/zenodo.14928612)
