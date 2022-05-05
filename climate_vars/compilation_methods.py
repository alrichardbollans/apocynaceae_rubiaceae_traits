import os

import numpy as np
import pandas as pd
from automatchnames import get_accepted_info_from_names_in_column
from pkg_resources import resource_filename

_inputs_path = '/home/atp/Documents/work life/Kew/large folders/occ_climate_vars/'
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


# TODO: Clean before appending rasters (e.g. remove duplicate ids)

def clean_occurences():
    pass


def get_taxa_in_malarial_regions():
    # The `countryCode` column is in ISO-3 character.
    pass


def get_climate_df():
    # TODO: Get accepted info for celastraceae

    clim_occ_df = pd.read_csv(clean_occurences_with_clim_vars_csv)

    print(clim_occ_df.head())
    print(clim_occ_df.columns)
    dfs = []
    for c in ['CHELSA_bio1_1981.2010_V.2.1', 'CHELSA_bio12_1981.2010_V.2.1',
              'nitrogen_0.5cm_mean', 'phh2o_0.5cm_mean', 'soc_0.5cm_mean', 'gmted_breakline', 'decimalLatitude',
              'decimalLongitude']:
        # We take median of occurences in order to mitigate outliers
        # This still has the possible issue of being biased towards where people take samples
        avg = pd.DataFrame(clim_occ_df.groupby([clim_occ_df['fullname']])[c].median())

        dfs.append(avg)

    for df in dfs:
        print(len(df))
    merged = pd.merge(dfs[0], dfs[1], on='fullname')
    for i in range(len(dfs)):
        if i > 1:
            merged = pd.merge(merged, dfs[i], on='fullname')

    # Get mode of koppengeiger classification.
    # In case of multiple modes, select one at random
    merged['koppen_geiger2_mode'] = clim_occ_df.groupby([clim_occ_df['fullname']])['Beck_KG_V1_present'].agg(
        lambda x: np.random.choice(x.mode(dropna=True)))

    merged['koppen_geiger2_all'] = clim_occ_df.groupby([clim_occ_df['fullname']])[
        'Beck_KG_V1_present'].unique().apply(
        list).values

    merged.rename(columns=_rename_dict, inplace=True)
    merged['fullname'] = merged.index
    acc_merged = get_accepted_info_from_names_in_column(merged, 'fullname',
                                                        families_of_interest=['Apocynaceae', 'Rubiaceae'])
    acc_merged.to_csv(compiled_climate_vars_csv)


def get_clean_occ_df():
    occ_df = pd.read_csv(clean_occurences_with_clim_vars_csv)
    acc_df = get_accepted_info_from_names_in_column(occ_df, 'fullname',
                                                    families_of_interest=['Apocynaceae', 'Rubiaceae'])
    acc_df.to_csv(occurences_with_accepted_names_csv)


def test_occs():
    sp_occ = pd.read_csv(clean_occurences_with_clim_vars_csv)
    dups = sp_occ[sp_occ.duplicated(subset=['gbifID'])]
    print(dups)
    if len(dups.index) > 0:
        raise ValueError


def main():
    # test_occs()
    # get_clean_occ_df()
    get_climate_df()


if __name__ == '__main__':
    main()
