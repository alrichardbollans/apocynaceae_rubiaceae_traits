import os

import numpy as np
import pandas as pd
from automatchnames import get_accepted_info_from_names_in_column, get_accepted_info_from_ids_in_column
from pkg_resources import resource_filename

from large_file_storage import large_folders

_inputs_path = os.path.join(large_folders, 'occ_climate_vars/')
clean_occurences_with_clim_vars_csv = os.path.join(_inputs_path, 'occ_with_climate_vars.csv')
_occurrences_with_accepted_names_csv = os.path.join(_inputs_path, 'occurences_with_accepted_names.csv')
occurrences_with_clim_and_accepted_names_csv = os.path.join(_inputs_path, 'occurrences_with_clim_and_accepted_names.csv')

_output_path = resource_filename(__name__, 'outputs')
compiled_climate_vars_csv = os.path.join(_output_path, 'compiled_climate_vars.csv')

if not os.path.isdir(_output_path):
    os.mkdir(_output_path)

# Imported variables and new names for them
climate_vars_and_names = {'Beck_KG_V1_present': 'Beck_KG_V1_present',
                          'CHELSA_bio1_1981.2010_V.2.1': 'mean_annual_air_temperature',
                          'CHELSA_bio4_1981.2010_V.2.1': 'temp_seasonality',
                          'CHELSA_bio10_1981.2010_V.2.1': 'bio10',
                          'CHELSA_bio11_1981.2010_V.2.1': 'bio11',
                          'CHELSA_bio12_1981.2010_V.2.1': 'annual_precipitation_amount',
                          'CHELSA_bio15_1981.2010_V.2.1': 'bio15',
                          'CHELSA_bio16_1981.2010_V.2.1': 'bio16',
                          'CHELSA_bio17_1981.2010_V.2.1': 'bio17',
                          'gmted_breakline': 'breakline_elevation',
                          'gmted_elevation': 'elevation',
                          'gmted_slope': 'slope',
                          'soil_nitrogen': 'soil_nitrogen',
                          'soil_ph': 'soil_ph',
                          'soil_soc': 'soil_soc',
                          'soil_depth': 'soil_depth',
                          'soil_ocs': 'soil_ocs',
                          'water_capacity': 'water_capacity',
                          'decimalLatitude': 'latitude',
                          'decimalLongitude': 'longitude'
                          }
# All final variables
all_climate_names = list(climate_vars_and_names.values()) + ['koppen_geiger_mode',
                                                             'koppen_geiger_all']
all_climate_names.remove('Beck_KG_V1_present')
families_in_occurrences = ['Apocynaceae', 'Rubiaceae', 'Celastraceae']


def read_and_clean_occurences() -> pd.DataFrame:
    """
    Get accepted info for occurrences. This only needs updating with new occurrences
    rather than when new cliamte data is added
    :return:
    """
    # TODO: remove close occs re: autocorrelation

    clim_occ_df = pd.read_csv(clean_occurences_with_clim_vars_csv)
    print(clim_occ_df.columns)

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

    acc_df = acc_df[['fullname', 'Accepted_Name', 'Accepted_ID', 'Accepted_Rank',
                     'Accepted_Species', 'Accepted_Species_ID']]
    acc_df.to_csv(_occurrences_with_accepted_names_csv)

    return acc_df


def get_climate_df():
    occ_df = pd.read_csv(clean_occurences_with_clim_vars_csv)[
        ['species', 'fullname', 'countryCode', 'coordinateUncertaintyInMeters',
         'year', 'individualCount', 'gbifID', 'basisOfRecord', 'institutionCode', 'establishmentMeans',
         'is_cultivated_observation', 'sourceID'] + list(climate_vars_and_names.keys())]
    occ_df.rename(columns=climate_vars_and_names, inplace=True)
    print(occ_df.head())
    print(occ_df.columns)

    # Read accepted info and merge with climate data
    acc_info = pd.read_csv(_occurrences_with_accepted_names_csv).drop_duplicates(subset='fullname')
    acc_occ_df = pd.merge(occ_df, acc_info, on='fullname')
    # Output occurrences with climate vars and accepted names
    acc_occ_df.to_csv(occurrences_with_clim_and_accepted_names_csv)

    dfs = []
    grouped = acc_occ_df.groupby(['Accepted_ID'])
    for c in list(climate_vars_and_names.values()):
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
    merged['koppen_geiger_mode'] = acc_occ_df.groupby(['Accepted_ID'])['Beck_KG_V1_present'].agg(
        lambda x: np.random.choice(x.mode(dropna=True)))

    merged['koppen_geiger_all'] = acc_occ_df.groupby(['Accepted_ID'])[
        'Beck_KG_V1_present'].unique().apply(
        list).values

    merged.drop(columns='Beck_KG_V1_present', inplace=True)
    out_df = pd.merge(merged, acc_info, on='Accepted_ID')

    out_df.to_csv(compiled_climate_vars_csv)


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

    # read_and_clean_occurences()

    get_climate_df()


if __name__ == '__main__':
    main()
