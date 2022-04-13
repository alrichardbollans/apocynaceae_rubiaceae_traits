import os

import pandas as pd
from pkg_resources import resource_filename

from cleaning import compile_hits

from manually_collected_data import encoded_traits_csv
from metabolite_vars import rub_apoc_alkaloid_hits_output_csv
from powo_searches import search_powo

### Inputs
_inputs_path = resource_filename(__name__, 'inputs')

### Temp outputs
_temp_outputs_path = resource_filename(__name__, 'temp_outputs')
_powo_search_temp_output_accepted_csv = os.path.join(_temp_outputs_path, 'powo_alkaloids_accepted.csv')
_manual_hit_temp_output = os.path.join(_temp_outputs_path, 'manual_alkaloids_accepted.csv')

### Outputs
_output_path = resource_filename(__name__, 'outputs')
output_alkaloid_csv = os.path.join(_output_path, 'list_plants_with_alkaloids.csv')


def get_powo_alkaloids():
    search_powo(['alkaloid'],
                _powo_search_temp_output_accepted_csv, families_of_interest=['Rubiaceae', 'Apocynaceae'],
                filters=['species', 'infraspecies'])


def get_manual_hits():
    trait_table = pd.read_csv(encoded_traits_csv)
    alk_hits = trait_table[trait_table['Alkaloids'] == 1]
    alk_hits = alk_hits[[
        'Alkaloids', 'Accepted_Name', 'Accepted_Species', 'Accepted_Species_ID', 'Accepted_ID', 'Accepted_Rank',
        'Family']]
    alk_hits['Source'] = 'Manual'
    alk_hits.to_csv(_manual_hit_temp_output)


def main():
    if not os.path.isdir(_temp_outputs_path):
        os.mkdir(_temp_outputs_path)
    if not os.path.isdir(_output_path):
        os.mkdir(_output_path)
    get_powo_alkaloids()
    powo_hits = pd.read_csv(_powo_search_temp_output_accepted_csv)
    manual_hits = pd.read_csv(_manual_hit_temp_output)
    alk_metabolite_hits = pd.read_csv(rub_apoc_alkaloid_hits_output_csv)

    compile_hits([powo_hits, alk_metabolite_hits, manual_hits], output_alkaloid_csv)


if __name__ == '__main__':
    main()
