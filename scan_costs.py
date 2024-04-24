import pandas as pd
import os
from table_pypsa.run_pypsa import build_network, run_pypsa
from table_pypsa.utilities.load_costs import load_costs
import argparse

# Get file name from command line argument
parser = argparse.ArgumentParser()
parser.add_argument('--file_name', '-f',help='Name of the base case file', required=True)
parser.add_argument('--cost_values', '-c',help='Values of component attribute to be scanned')
parser.add_argument('--tech_component', '-t',help='Name of the component to be scanned')
parser.add_argument('--cost_parameter', '-p',help='Attribute of the component to be scanned')



def main():
    args = parser.parse_args()
    base_case_file = args.file_name
    cost_values = list(map(int, args.cost_values.split(',')))
    tech_component = args.tech_component
    cost_parameter = args.cost_parameter

    network, case_dict, component_list, comp_attributes = build_network(base_case_file)


    for component_cost in cost_values:

        # Read in costs
        base_costs = pd.read_csv(case_dict['costs_path'],index_col=[0, 1]).sort_index()

        if not component_cost == base_costs.loc[(tech_component, cost_parameter), 'value']:

            # Replace 'value' when parameter is cost_parameter and technology is tech_component
            base_costs.loc[(tech_component, cost_parameter), 'value'] = component_cost
            # Write costs to temporary file
            base_costs.to_csv('temp_costs.csv')
            # Load new costs
            costs = load_costs('temp_costs.csv', 'table_pypsa/utilities/cost_config.yaml', Nyears=case_dict['nyears'])
            # Remove temporary file
            os.remove('temp_costs.csv')

            # Replace corresponding component attributes
            if cost_parameter == 'investment':
                replace_attr = 'capital_cost'
            elif cost_parameter == 'fuel':
                replace_attr = 'marginal_cost'
            else:
                replace_attr = cost_parameter

            if tech_component == 'gas':
                replace_component = 'CCGT'
            else:
                replace_component = tech_component

            # Replace new costs in network and component list
            component_type = [getattr(network, comp_type) for comp_type in ['links', 'generators', 'stores'] if replace_component in getattr(network, comp_type).index][0]
            component_type.loc[replace_component, replace_attr] = costs.at[(replace_component, replace_attr)]
            btes_index = [i for i in range(len(component_list)) if component_list[i]['name'] == replace_component][0]
            component_list[btes_index][replace_attr] = costs.at[(replace_component, replace_attr)]
        else:
            if os.path.exists(case_dict['output_path']+case_dict['case_name']+case_dict['filename_prefix']):
                continue

        # Run PyPSA with new costs
        run_pypsa(network, base_case_file, case_dict, component_list, outfile_suffix='_{0}'.format(int(component_cost)))


if __name__ == "__main__":
    main()