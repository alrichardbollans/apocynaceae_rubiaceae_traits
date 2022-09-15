import os

import numpy as np
import pandas as pd
from pkg_resources import resource_filename

from large_file_storage import large_folders

_inputs_path = os.path.join(large_folders, 'occ_climate_vars/')
input_occurrences_with_clim_vars_csv = os.path.join(_inputs_path, 'occ_with_climate_vars.csv')

_output_path = resource_filename(__name__, 'outputs')
compiled_climate_vars_csv = os.path.join(_output_path, 'compiled_climate_vars.csv')
mean_regional_bioclimatic_vars_csv = os.path.join(_output_path, 'mean_regional_bioclimatic_vars.csv')

if not os.path.isdir(_output_path):
    os.mkdir(_output_path)

# Imported variables and new names for them
initial_climate_vars = ['Beck_KG_V1_present',
                        'mean_air_temp',
                        'temp_seasonality',
                        'bio10',
                        'bio11',
                        'precip_amount',
                        'precip_seasonality',
                        'bio16',
                        'bio17',
                        'breakline_elevation',
                        'elevation',
                        'slope',
                        'soil_nitrogen',
                        'soil_ph',
                        'soil_soc',
                        'soil_depth',
                        'soil_ocs',
                        'water_capacity',
                        'latitude',
                        'longitude'
                        ]
_climate_names = initial_climate_vars + ['koppen_geiger_mode',
                                         'koppen_geiger_all']
_climate_names.remove('Beck_KG_V1_present')

renaming = {'koppen_geiger_mode': 'kg_mode',
            'koppen_geiger_all': 'kg_all',
            'mean_air_temp': 'bio1',
            'temp_seasonality': 'bio4',
            'precip_amount': 'bio12',
            'precip_seasonality': 'bio15',
            'breakline_elevation': 'brkl_elevation',
            'water_capacity': 'soil_water_cap'
            }
# All final variables
all_climate_names = [renaming.get(n, n) for n in _climate_names]


def get_climate_df():
    acc_columns = ['Accepted_Name', 'Accepted_Species', 'Accepted_Species_ID',
                   'Accepted_ID', 'Accepted_Rank']
    columns_to_import = initial_climate_vars + acc_columns

    occ_df = pd.read_csv(input_occurrences_with_clim_vars_csv)[columns_to_import]

    dfs = []

    grouped = occ_df.groupby('Accepted_ID')
    for c in initial_climate_vars:
        # We take median of occurrences in order to mitigate outliers
        # This still has the possible issue of being biased towards where people take samples
        avg = pd.DataFrame(grouped[c].median())

        dfs.append(avg)

    for df in dfs:
        if len(df) != len(dfs[0]):
            print(len(df))
            print(len(dfs[0]))
            raise ValueError
    merged = pd.merge(dfs[0], dfs[1], on='Accepted_ID')
    for i in range(len(dfs)):
        if i > 1:
            merged = pd.merge(merged, dfs[i], on='Accepted_ID')

    # Get mode of koppengeiger classification.
    # In case of multiple modes, select one at random
    merged['koppen_geiger_mode'] = occ_df.groupby(['Accepted_ID'])['Beck_KG_V1_present'].agg(
        lambda x: np.random.choice(x.mode(dropna=True)))

    merged['koppen_geiger_all'] = occ_df.groupby(['Accepted_ID'])[
        'Beck_KG_V1_present'].unique().apply(
        list).values

    merged.drop(columns='Beck_KG_V1_present', inplace=True)

    # Get accepted info back from occurrences
    merged.reset_index(inplace=True)
    merged = merged.rename(columns={'index': 'Accepted_ID'})

    occ_acc_info = occ_df[acc_columns].drop_duplicates(subset=['Accepted_ID'], keep='first')
    out_df = pd.merge(occ_acc_info, merged, on='Accepted_ID')

    out_df.rename(columns=renaming, inplace=True)

    out_df.to_csv(compiled_climate_vars_csv)


def main():
    get_climate_df()


if __name__ == '__main__':
    main()
