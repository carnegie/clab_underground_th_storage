import pandas as pd
import os
from table_pypsa.run_pypsa import build_network, run_pypsa
from table_pypsa.utilities.load_costs import load_costs
import argparse

# Get file name from command line argument
parser = argparse.ArgumentParser()
parser.add_argument('--file_name', '-f',help='Name of the base case file', required=True)


def main():

    base_case_file = parser.parse_args().file_name
    network, case_dict, component_list, comp_attributes = build_network(base_case_file)


    for btes_discharge_cost in [250., 600., 950.]:

        if not btes_discharge_cost == 250.:
            # Replace btes_discharge cost with loop value
            base_costs = pd.read_csv(case_dict['costs_path'],index_col=[0, 1]).sort_index()
            # Replace 'value' when parameter is 'investment' and technology 'btes_discharge' with new value
            base_costs.loc[('BTES_discharger', 'investment'), 'value'] = btes_discharge_cost
            # Write costs to temporary file
            base_costs.to_csv('temp_costs.csv')
            # Load new costs
            costs = load_costs('temp_costs.csv', 'table_pypsa/utilities/cost_config.yaml', Nyears=case_dict['nyears'])
            # Remove temporary file
            os.remove('temp_costs.csv')
    
            # Replace new costs in network and component list
            network.links.loc['BTES_discharger', 'capital_cost'] = costs.at[('BTES_discharger', 'capital_cost')]
            btes_index = [i for i in range(len(component_list)) if component_list[i]['name'] == 'BTES_discharger'][0]
            component_list[btes_index]['capital_cost'] = costs.at[('BTES_discharger', 'capital_cost')]
            btes_discharge_cost = int(btes_discharge_cost)

        else:
            if os.path.exists(case_dict['output_path']+case_dict['case_name']+case_dict['filename_prefix']):
                continue

        # Run PyPSA with new costs
        run_pypsa(network, base_case_file, case_dict, component_list, outfile_suffix='_{0}'.format(btes_discharge_cost))


if __name__ == "__main__":
    main()