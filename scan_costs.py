import pandas as pd
import os
from table_pypsa.run_pypsa import build_network, run_pypsa
from table_pypsa.utilities.load_costs import load_costs
import argparse
import copy

# Get file name from command line argument
parser = argparse.ArgumentParser()
parser.add_argument('--file_name', '-f', help='Name of the base case file', required=True)
parser.add_argument('--tech_name', '-t', help='Name of the component to be scanned')
parser.add_argument('--cost_factors', '-c', help='Values of component attribute to be scanned')

def scan_costs(base_case_file, cost_factors, tech_name):

    network, case_dict, component_list, comp_attributes = build_network(base_case_file)

    for cost_factor in cost_factors:
        # Create deep copies of network and component_list
        network_copy = copy.deepcopy(network)
        component_list_copy = copy.deepcopy(component_list)

        if tech_name == "fossil":
            tech_names = ['natgas', 'oil']
        else:
            tech_names = [tech_name]

        for technology in tech_names:
            if not cost_factor == 1 and not technology == "nothing":
                # Run over all components that have tech_name in their name
                for tech_component in [comp['name'] for comp in component_list_copy if technology in comp['carrier']]:
                    for cost_parameter in ['capital_cost', 'marginal_cost']:
                        # Replace new costs in network_copy and component_list_copy
                        component_type = [getattr(network_copy, comp_type) for comp_type in ['links', 'generators', 'stores'] if tech_component in getattr(network_copy, comp_type).index][0]
                        print('Old {0} for {1}: {2}'.format(cost_parameter, tech_component, component_type.loc[tech_component, cost_parameter]))
                        component_type.loc[tech_component, cost_parameter] = cost_factor * component_type.loc[tech_component, cost_parameter]
                        print('New {0} for {1}: {2}'.format(cost_parameter, tech_component, component_type.loc[tech_component, cost_parameter]))
                        btes_indeces = [i for i in range(len(component_list_copy)) if tech_component in component_list_copy[i]['name']]
                        for btes_index in btes_indeces:
                            component_list_copy[btes_index][cost_parameter] = component_type.loc[tech_component, cost_parameter]
        
        # Run PyPSA with new costs
        run_pypsa(network_copy, base_case_file, case_dict, component_list_copy, outfile_suffix='_{0}_costsx{1}'.format(tech_name, str(cost_factor).replace('.', 'p')))

if __name__ == "__main__":
    args = parser.parse_args()
    base_case_file = args.file_name
    cost_factors = list(map(float, args.cost_factors.split(',')))
    tech_name = args.tech_name

    scan_costs(base_case_file, cost_factors, tech_name)