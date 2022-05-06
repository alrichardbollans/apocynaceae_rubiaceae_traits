import os

import numpy as np
import pandas as pd
from automatchnames import get_accepted_info_from_names_in_column
from pkg_resources import resource_filename

from large_file_storage import large_folders

_inputs_path = os.path.join(large_folders,'occ_climate_vars/')
clean_occurences_with_clim_vars_csv = os.path.join(_inputs_path, 'occ_with_climate_vars.csv')
occurences_with_accepted_names_csv = os.path.join(_inputs_path, 'occurences_with_accepted_names.csv')

_output_path = resource_filename(__name__, 'outputs')
compiled_climate_vars_csv = os.path.join(_output_path, 'compiled_climate_vars.csv')

if not os.path.isdir(_output_path):
    os.mkdir(_output_path)

_rename_dict = {'CHELSA_bio1_1981.2010_V.2.1': 'mean_annual_air_temperature',
                'CHELSA_bio12_1981.2010_V.2.1': 'annual_precipitation_amount',
                'nitrogen_0.5cm_mean': 'soil_nitrogen', 'phh2o_0.5cm_mean': 'soil_ph',
                'soc_0.5cm_mean': 'soil_soc', 'gmted_breakline': 'breakline_elevation'}

families_in_occurrences = ['Apocynaceae', 'Rubiaceae', 'Celastraceae']


def read_and_clean_occurences() -> pd.DataFrame:
    clim_occ_df = pd.read_csv(clean_occurences_with_clim_vars_csv)[
        ['species', 'fullname', 'decimalLongitude', 'decimalLatitude', 'countryCode', 'coordinateUncertaintyInMeters',
         'year', 'individualCount', 'gbifID', 'basisOfRecord', 'institutionCode', 'establishmentMeans',
         'is_cultivated_observation', 'sourceID', 'Beck_KG_V1_present', 'CHELSA_bio1_1981.2010_V.2.1',
         'CHELSA_bio12_1981.2010_V.2.1', 'gmted_breakline', 'nitrogen_0.5cm_mean', 'phh2o_0.5cm_mean',
         'soc_0.5cm_mean']]
    clim_occ_df.rename(columns=_rename_dict, inplace=True)
    # Coord uncertainty 20000
    clean_df = clim_occ_df[clim_occ_df['coordinateUncertaintyInMeters'] <= 20000]

    ## Years
    clean_df = clean_df[clean_df['year'] >= 1945]

    ## long and lat
    clean_df = clean_df[~((clean_df['decimalLongitude'] == 0) & (clean_df['decimalLatitude'] == 0))]

    clean_df = clean_df[(clean_df['decimalLongitude'] != clean_df['decimalLatitude'])]

    # na lat long
    clean_df = clean_df[~((clean_df['decimalLongitude'].isna()) | (clean_df['decimalLatitude'].isna()))]

    ### CLimate values

    acc_df = get_accepted_info_from_names_in_column(clean_df, 'fullname',
                                                    families_of_interest=families_in_occurrences)
    acc_df.to_csv(occurences_with_accepted_names_csv)

    return acc_df


def get_climate_df(clean_acc_df: pd.DataFrame):

    print(clean_acc_df.head())
    print(clean_acc_df.columns)
    dfs = []
    for c in list(_rename_dict.values()) + ['decimalLatitude',
                                            'decimalLongitude']:
        # We take median of occurrences in order to mitigate outliers
        # This still has the possible issue of being biased towards where people take samples
        avg = pd.DataFrame(clean_acc_df.groupby([clean_acc_df['fullname']])[c].median())

        dfs.append(avg)

    for df in dfs:
        print(len(df))
    merged = pd.merge(dfs[0], dfs[1], on='fullname')
    for i in range(len(dfs)):
        if i > 1:
            merged = pd.merge(merged, dfs[i], on='fullname')

    # Get mode of koppengeiger classification.
    # In case of multiple modes, select one at random
    merged['koppen_geiger2_mode'] = clean_acc_df.groupby([clean_acc_df['fullname']])['Beck_KG_V1_present'].agg(
        lambda x: np.random.choice(x.mode(dropna=True)))

    merged['koppen_geiger2_all'] = clean_acc_df.groupby([clean_acc_df['fullname']])[
        'Beck_KG_V1_present'].unique().apply(
        list).values

    merged['fullname'] = merged.index

    merged.to_csv(compiled_climate_vars_csv)


def test_occs():
    test_dir = resource_filename(__name__, 'tests')
    occ_df = pd.read_csv(clean_occurences_with_clim_vars_csv)
    dups = occ_df[occ_df.duplicated(subset=['gbifID'])]
    print(dups)
    if len(dups.index) > 0:
        raise ValueError

    # Coord uncertainty 20000
    print('coord uncertainty clean')
    uncertain = occ_df[occ_df['coordinateUncertaintyInMeters'] > 20000]
    uncertain.to_csv(os.path.join(test_dir, 'bad_coord_examples.csv'))
    print(len(occ_df.index))
    # clim_occ_df = clim_occ_df[clim_occ_df['coordinateUncertaintyInMeters'] <= 20000]

    print(len(occ_df.index))

    ## Years
    uncertain = occ_df[occ_df['year'] < 1945]
    uncertain.to_csv(os.path.join(test_dir, 'bad_year_examples.csv'))

    ## 0 long and lat
    uncertain = occ_df[(occ_df['decimalLongitude'] == 0) & (occ_df['decimalLatitude'] == 0)]
    uncertain.to_csv(os.path.join(test_dir, 'bad_zerolatlong_examples.csv'))

    uncertain = occ_df[(occ_df['decimalLongitude'] == occ_df['decimalLatitude'])]
    uncertain.to_csv(os.path.join(test_dir, 'bad_eqlatlong_examples.csv'))

    # na lat long
    uncertain = occ_df[(occ_df['decimalLongitude'].isna()) | (occ_df['decimalLatitude'].isna())]
    uncertain.to_csv(os.path.join(test_dir, 'bad_nalatlong_examples.csv'))

    # na codes
    uncertain = occ_df[(occ_df['countryCode'].isna())]
    uncertain.to_csv(os.path.join(test_dir, 'bad_naccode_examples.csv'))


def main():
    # test_occs()
    acc_occ_df = read_and_clean_occurences()
    get_climate_df(acc_occ_df)


if __name__ == '__main__':
    main()
