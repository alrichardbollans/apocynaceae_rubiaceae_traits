import os

import pandas as pd
from pkg_resources import resource_filename

### Inputs
from manually_collected_data import manual_morph_data_output, manual_habit_data_output
from morphological_vars import temp_outputs_path, try_spine_temp_output_accepted_csv, try_hair_temp_output_accepted_csv, \
    try_no_spine_temp_output_accepted_csv, prepare_try_data
from cleaning import compile_hits
from powo_searches import search_powo, create_presence_absence_data

spine_powo_search_temp_output_accepted_csv = os.path.join(temp_outputs_path, 'spines_powo' + '_accepted.csv')
hairs_powo_search_temp_output_accepted_csv = os.path.join(temp_outputs_path, 'hairs_powo' + '_accepted.csv')

### Outputs
output_path = resource_filename(__name__, 'outputs')
spines_output_csv = os.path.join(output_path, 'spines_hits.csv')
no_spines_output_csv = os.path.join(output_path, 'no_spines_hits.csv')

hairy_output_csv = os.path.join(output_path, 'hairy_hits.csv')
habits_output_csv = os.path.join(output_path, 'habits.csv')


def get_powo_hairs_and_spines():
    # Get spine powo hits
    search_powo(['spine', 'thorn', 'spikes'],
                spine_powo_search_temp_output_accepted_csv,
                characteristics_to_search=['leaf', 'inflorescence', 'appearance', 'fruit'],
                families_of_interest=['Rubiaceae', 'Apocynaceae'], filters=['genera', 'species', 'infraspecies'])

    # Get powo hair hits
    search_powo(['hairs', 'hairy', 'pubescent'],
                hairs_powo_search_temp_output_accepted_csv,
                characteristics_to_search=['leaf', 'inflorescence', 'appearance'],
                families_of_interest=['Rubiaceae', 'Apocynaceae'], filters=['genera', 'species', 'infraspecies'])


def output_compiled_data():
    # Manually collected data
    acc_manual_data = pd.read_csv(manual_morph_data_output)
    # Spines
    powo_spine_hits = pd.read_csv(spine_powo_search_temp_output_accepted_csv)

    # Spines are often reported as 'absent'
    # List accepted ids of such cases to remove
    spine_ids_for_absence = ['34290-1', '2257-1', '2425-1', '2469-1', '2560-1', '331696-2', '2171-1',
                             '2218-1',
                             '2298-1',
                             '2180-1',
                             '2516-1',
                             '2198-1',
                             '2377-1', '328992-2'
                             ]
    powo_presence_spine_hits, powo_absence_spine_hits = create_presence_absence_data(powo_spine_hits,
                                                                                     accepted_ids_of_absence=spine_ids_for_absence)

    manual_spine_hits = acc_manual_data[acc_manual_data['spines'] == 'y'].copy()
    manual_spine_hits['Manual_snippet'] = manual_spine_hits['spines']
    try_spine_hits = pd.read_csv(try_spine_temp_output_accepted_csv)
    all_spine_dfs = [manual_spine_hits, try_spine_hits, powo_presence_spine_hits]
    compile_hits(all_spine_dfs, spines_output_csv)

    taxa_with_spines = []
    for d in all_spine_dfs:
        taxa_with_spines += d["Accepted_Name"].unique().tolist()

    # No spines
    try_no_spine_hits = pd.read_csv(try_no_spine_temp_output_accepted_csv)
    manual_no_spines_hits = acc_manual_data[acc_manual_data['spines'] == 'x'].copy()
    manual_no_spines_hits['Manual_snippet'] = manual_no_spines_hits['spines']

    # Remove no spines hits which are in spines hits as we consider spines on any plant part
    # and no spines may indicate no spine on particular part
    powo_absence_spine_hits = powo_absence_spine_hits[~powo_absence_spine_hits["Accepted_Name"].isin(taxa_with_spines)]
    manual_no_spines_hits = manual_no_spines_hits[~manual_no_spines_hits["Accepted_Name"].isin(taxa_with_spines)]
    try_no_spine_hits = try_no_spine_hits[~try_no_spine_hits["Accepted_Name"].isin(taxa_with_spines)]

    compile_hits([powo_absence_spine_hits, manual_no_spines_hits, try_no_spine_hits], no_spines_output_csv)

    # Hairs
    powo_hair_hits = pd.read_csv(hairs_powo_search_temp_output_accepted_csv)
    try_hair_hits = pd.read_csv(try_hair_temp_output_accepted_csv)

    all_hair_hits = [powo_hair_hits, try_hair_hits]
    compile_hits(all_hair_hits, hairy_output_csv)

    # Habit
    habits = pd.read_csv(manual_habit_data_output)
    habits.to_csv(habits_output_csv)


def main():
    if not os.path.isdir(temp_outputs_path):
        os.mkdir(temp_outputs_path)
    if not os.path.isdir(output_path):
        os.mkdir(output_path)
    get_powo_hairs_and_spines()
    prepare_try_data()
    output_compiled_data()


if __name__ == '__main__':
    main()
