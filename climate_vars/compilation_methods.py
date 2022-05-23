import os

import numpy as np
import pandas as pd
from automatchnames import get_accepted_info_from_names_in_column, get_accepted_info_from_ids_in_column
from pkg_resources import resource_filename

from large_file_storage import large_folders

_inputs_path = os.path.join(large_folders, 'occ_climate_vars/')
clean_native_occurences_with_clim_vars_csv = os.path.join(_inputs_path, 'native', 'occ_with_climate_vars.csv')
clean_introd_occurences_with_clim_vars_csv = os.path.join(_inputs_path, 'introduced', 'occ_with_climate_vars.csv')

occurrences_with_accepted_names_csv = os.path.join(_inputs_path, 'occurences_with_accepted_names.csv')
native_occurrences_with_clim_and_accepted_names_csv = os.path.join(_inputs_path,
                                                                   'native_occurrences_with_clim_and_accepted_names.csv')
introd_occurrences_with_clim_and_accepted_names_csv = os.path.join(_inputs_path,
                                                                   'introd_occurrences_with_clim_and_accepted_names.csv')

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
# All final variables
all_climate_names = initial_climate_vars + ['koppen_geiger_mode',
                                            'koppen_geiger_all']
all_climate_names.remove('Beck_KG_V1_present')
families_in_occurrences = ['Apocynaceae', 'Rubiaceae', 'Celastraceae']


def read_and_clean_occurences() -> pd.DataFrame:
    """
    Get accepted info for occurrences. This only needs updating with new occurrences
    rather than when new cliamte data is added
    :return:
    """

    native_occ_df = pd.read_csv(clean_native_occurences_with_clim_vars_csv)
    introd_occ_df = pd.read_csv(clean_introd_occurences_with_clim_vars_csv)

    occ_df = pd.concat([native_occ_df, introd_occ_df])
    print(occ_df[occ_df['gbifID'].duplicated(keep="first")])
    print(occ_df)
    occ_df.drop_duplicates(subset=['gbifID'], keep='first', inplace=True)
    print(occ_df)
    # print(occ_df.columns)

    acc_df = get_accepted_info_from_names_in_column(occ_df, 'fullname',
                                                    families_of_interest=families_in_occurrences)

    acc_df = acc_df[['fullname', 'Accepted_Name', 'Accepted_ID', 'Accepted_Rank',
                     'Accepted_Species', 'Accepted_Species_ID']]
    acc_df.to_csv(occurrences_with_accepted_names_csv)

    return acc_df


def get_climate_df():
    native_occ_df = pd.read_csv(clean_native_occurences_with_clim_vars_csv)[
        ['species', 'fullname', 'countryCode', 'coordinateUncertaintyInMeters',
         'year', 'individualCount', 'gbifID', 'basisOfRecord', 'institutionCode', 'establishmentMeans',
         'is_cultivated_observation', 'sourceID'] + initial_climate_vars]
    introd_occ_df = pd.read_csv(clean_introd_occurences_with_clim_vars_csv)[
        ['species', 'fullname', 'countryCode', 'coordinateUncertaintyInMeters',
         'year', 'individualCount', 'gbifID', 'basisOfRecord', 'institutionCode', 'establishmentMeans',
         'is_cultivated_observation', 'sourceID'] + initial_climate_vars]

    print(native_occ_df.head())
    print(len(native_occ_df.index))
    print(introd_occ_df.head())
    print(len(introd_occ_df.index))

    # Read accepted info and merge with climate data
    acc_info = pd.read_csv(occurrences_with_accepted_names_csv).drop_duplicates(subset='fullname')
    cols_to_drop = [c for c in acc_info.columns if 'Unnamed' in c]
    acc_info.drop(columns=cols_to_drop, inplace=True)
    native_acc_occ_df = pd.merge(native_occ_df, acc_info, on='fullname')
    introd_acc_occ_df = pd.merge(introd_occ_df, acc_info, on='fullname')

    print(native_acc_occ_df.head())
    print(len(native_acc_occ_df.index))
    print(introd_acc_occ_df.head())
    print(len(introd_acc_occ_df.index))

    # Output occurrences with climate vars and accepted names
    native_acc_occ_df.to_csv(native_occurrences_with_clim_and_accepted_names_csv)
    introd_acc_occ_df.to_csv(introd_occurrences_with_clim_and_accepted_names_csv)

    # Get dataframe with native occurrences plus introduced occurrences where no native data has been found

    introd_occ_not_in_native = introd_acc_occ_df[
        ~introd_acc_occ_df['Accepted_ID'].isin(native_acc_occ_df['Accepted_ID'].values)]
    occ_df_native_priority = pd.concat([native_acc_occ_df, introd_occ_not_in_native])

    dfs = []
    grouped = occ_df_native_priority.groupby(['Accepted_ID'])
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
    merged['koppen_geiger_mode'] = occ_df_native_priority.groupby(['Accepted_ID'])['Beck_KG_V1_present'].agg(
        lambda x: np.random.choice(x.mode(dropna=True)))

    merged['koppen_geiger_all'] = occ_df_native_priority.groupby(['Accepted_ID'])[
        'Beck_KG_V1_present'].unique().apply(
        list).values

    merged.drop(columns='Beck_KG_V1_present', inplace=True)
    out_df = pd.merge(merged, acc_info, on='Accepted_ID')

    out_df.to_csv(compiled_climate_vars_csv)


def main():
    # read_and_clean_occurences()

    get_climate_df()


if __name__ == '__main__':
    main()
