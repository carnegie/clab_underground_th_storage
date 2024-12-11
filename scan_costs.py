import pandas as pd
import os
from table_pypsa.run_pypsa import build_network, run_pypsa
from table_pypsa.utilities.load_costs import load_costs
import argparse
import copy
import pickle

# Get file name from command line argument
parser = argparse.ArgumentParser()
parser.add_argument('--file_name', '-f', help='Name of the base case file', required=True)
parser.add_argument('--tech_name', '-t', help='Name of the component to be scanned', required=True)
parser.add_argument('--cost_factors', '-c', help='Values of component attribute to be scanned', required=True)
parser.add_argument('--elec_cost', '-e', help='Set if electricity cost should be scanned', action='store_true')

def replace_electricity_costs(cost_factor, scan_tech, tech_comp, n):
    """
    Replace electricity costs time series of the buyer/seller to market with time series 
    obtained from optimization without underground thermal storage.
    """
    # Read electricity costs time series from optimization without underground thermal storage
    res_path = 'output_data/btes_base_case_orca_no_btes/btes_output_no_btes_{0}_costsx{1}.pickle'.format(scan_tech, str(cost_factor).replace('.','p'))
    with open(res_path, 'rb') as f:
        data = pickle.load(f)

        time_data = data['time results']
        electricity_costs = time_data[['electricity marginal cost']]
        n.snapshots = electricity_costs.index
        if tech_comp == 'const_generator':
            n.generators_t['marginal_cost'][tech_comp] = electricity_costs
        elif tech_comp == 'power_seller':
            n.links_t['marginal_cost'][tech_comp] = -1*electricity_costs
        else:
            raise ValueError('Invalid tech_comp value: {0}'.format(tech_comp))
        f.close()
    return electricity_costs


from concurrent.futures import ProcessPoolExecutor
import copy

def process_cost_factor(cost_factor, network, component_list, elec_cost, tech_name, case_dict, base_case_file):
    # Create shallow copies or lightweight deep copies
    network_copy = copy.deepcopy(network)
    component_list_copy = copy.deepcopy(component_list)

    # Determine the relevant technologies
    if elec_cost:
        tech_names = ['const_generator', 'power_seller']
    else:
        tech_names = {
            "fossil": ['natgas', 'oil'],
            "renewable": ['wind', 'solar', 'battery', 'hydrogen']
        }.get(tech_name, [tech_name])

    # Pre-filter components by tech_names
    filtered_components = {
        tech: [comp for comp in component_list_copy if tech in comp['carrier']]
        for tech in tech_names
    }

    for technology, components in filtered_components.items():
        if cost_factor == 1 or technology == "nothing":
            continue

        for tech_component in [comp['name'] for comp in components]:
            component_type = next(
                (getattr(network_copy, comp_type) for comp_type in ['links', 'generators', 'stores']
                 if tech_component in getattr(network_copy, comp_type).index), None
            )

            if component_type is None:
                continue

            for cost_parameter in ['capital_cost', 'marginal_cost']:
                old_cost = component_type.loc[tech_component, cost_parameter]
                print(f'Old {cost_parameter} for {tech_component}: {old_cost}')

                if elec_cost and cost_parameter == 'capital_cost':
                    continue

                if tech_name == "fossil" and cost_parameter == 'capital_cost':
                    continue

                if tech_name == "xxx":
                    base_costs = pd.read_csv(case_dict['costs_path'],index_col=[0, 1]).sort_index()
                    # Adjust for specific cases (replace temp files with in-memory operations)
                    base_costs.loc[(tech_component, 'fuel'), 'value'] *= cost_factor
                    costs = load_costs(base_costs, 'table_pypsa/utilities/cost_config.yaml', Nyears=case_dict['nyears'])
                    component_type.loc[tech_component, cost_parameter] = costs.at[(tech_component, cost_parameter)]
                else:
                    component_type.loc[tech_component, cost_parameter] *= cost_factor

                print(f'New {cost_parameter} for {tech_component}: {component_type.loc[tech_component, cost_parameter]}')

                # Update component_list_copy
                for comp in components:
                    if comp['name'] == tech_component:
                        comp[cost_parameter] = component_type.loc[tech_component, cost_parameter]

    # Run PyPSA with updated network and components
    run_pypsa(
        network_copy,
        base_case_file,
        case_dict,
        component_list_copy,
        outfile_suffix=f'_{tech_name}_costsx{str(cost_factor).replace(".", "p")}'
    )

def scan_costs(base_case_file, cost_factors, tech_name, elec_cost=False):
    """
    Scan costs of a specific technology in the network.
    """

    network, case_dict, component_list, comp_attributes = build_network(base_case_file)
    # Parallelize the outer loop
    with ProcessPoolExecutor() as executor:
        futures = [
            executor.submit(
                process_cost_factor,
                cost_factor, network, component_list, elec_cost, tech_name, case_dict, base_case_file
            )
            for cost_factor in cost_factors
        ]
        results = [future.result() for future in futures]

if __name__ == "__main__":
    args = parser.parse_args()
    base_case_file = args.file_name
    cost_factors = list(map(float, args.cost_factors.split(',')))
    tech_name = args.tech_name
    elec_cost = args.elec_cost

    scan_costs(base_case_file, cost_factors, tech_name, elec_cost)