import pandas as pd
import os
from clab_pypsa.run_pypsa import build_network, run_pypsa
from clab_pypsa.utilities.load_costs import load_costs


def main():

    base_case_file = 'BTES_base_case.xlsx'
    network, case_dict, component_list, comp_attributes = build_network(base_case_file)


    for btes_discharge_cost in [200., 250., 500., 950., 1200.]:

        if not btes_discharge_cost == 250.:
            # Replace btes_discharge cost with loop value
            base_costs = pd.read_csv(case_dict['costs_path'],index_col=[0, 1]).sort_index()
            pd.set_option('display.max_rows', None)
            # Replace 'value' when parameter is 'investment' and technology 'btes_discharge' with new value
            base_costs.loc[('BTES_discharger', 'investment'), 'value'] = btes_discharge_cost
            # Load new costs
            costs = load_costs(base_costs, 'clab_pypsa/utilities/cost_config.yaml')
    
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