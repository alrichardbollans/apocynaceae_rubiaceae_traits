import ast
import os
from typing import List

import geopandas
import numpy as np
import pandas as pd
# Add progress bar to apply method
from automatchnames import get_accepted_info_from_names_in_column
from tqdm import tqdm

tqdm.pandas()
from pkg_resources import resource_filename

from large_file_storage import plant_occurences
from wcsp_distributions import distributions_csv

_inputs_path = resource_filename(__name__, 'inputs')
tdwg3_shpfile = os.path.join(_inputs_path, 'wgsrpd-master', 'level3', 'level3.shp')

_standard_cleaned_csv = os.path.join(plant_occurences, 'outputs', 'standard_cleaned_occurrences.csv')

accepted_name_info_of_occurrences_csv = os.path.join(plant_occurences, 'outputs', 'occurences_with_accepted_names.csv')

final_occurrence_output_dir = resource_filename(__name__, 'outputs')
final_occurrence_output_csv = os.path.join(final_occurrence_output_dir, 'cleaned_occurrences.csv')


def read_my_occs():
    families_in_occurrences = ['Apocynaceae', 'Rubiaceae', 'Celastraceae']
    standard_occ_df = pd.read_csv(_standard_cleaned_csv)
    read_occurences_and_output_acc_names(standard_occ_df, accepted_name_info_of_occurrences_csv,
                                         families_in_occurrences=families_in_occurrences)


def read_occurences_and_output_acc_names(occ_df: pd.DataFrame, out_csv: str = None,
                                         families_in_occurrences: List[str] = None) -> pd.DataFrame:
    """
    Get accepted info for occurrences.
    :return:
    """

    print('Getting accepted info for occurrences:')
    print(occ_df)
    occ_df = occ_df.drop_duplicates(subset=['gbifID'], keep='first')

    acc_df = get_accepted_info_from_names_in_column(occ_df, 'fullname',
                                                    families_of_interest=families_in_occurrences)

    if out_csv is not None:
        acc_df.to_csv(accepted_name_info_of_occurrences_csv)

    return acc_df


def get_tdwg_regions_for_occurrences(occ_df: pd.DataFrame) -> geopandas.GeoDataFrame:
    ##### GET TDWG regions for occurrences

    print('Getting tdwg regions for each occurrence')
    # changing to a GeoDataFrame to create geometry series
    occ_gp = geopandas.GeoDataFrame(occ_df,
                                    geometry=geopandas.points_from_xy(occ_df['decimalLongitude'],
                                                                      occ_df['decimalLatitude']))

    ## Add shapefile
    # set the filepath and load in a shapefile
    map_df = geopandas.read_file(tdwg3_shpfile)

    occ_gp['tdwg3_region'] = ''
    for idx in range(map_df.shape[0]):
        # For every address, find if they reside within a province
        pip = occ_gp.within(map_df.loc[idx, 'geometry'])
        if pip.sum() > 0:  # we found where some of the addresses reside at map_df.loc[idx]
            occ_gp.loc[pip, 'tdwg3_region'] = map_df.loc[idx, 'LEVEL3_COD']

    print(occ_gp)
    return occ_gp


def match_taxa_to_wcsp_regions(occ_df_with_tdwg_regions: geopandas.GeoDataFrame,
                               output_csv: str = None,
                               tdwg3_region_col_name: str = 'tdwg3_region'):
    print('Getting native/introduced data for taxa')
    ### Match taxa to wcsp regions
    distro_df = pd.read_csv(distributions_csv)[
        ['native_tdwg3_codes', 'intro_tdwg3_codes', 'extinct_tdwg3_codes', 'Accepted_ID']]
    merged = pd.merge(occ_df_with_tdwg_regions, distro_df, on='Accepted_ID')

    merged['within_native'] = merged.progress_apply(
        lambda x: 1 if x[tdwg3_region_col_name] in ast.literal_eval(x['native_tdwg3_codes']) else 0, axis=1)

    merged['within_introduced'] = merged.progress_apply(
        lambda x: 1 if x[tdwg3_region_col_name] in ast.literal_eval(x['intro_tdwg3_codes']) else 0, axis=1)

    if output_csv is not None:
        merged.to_csv(output_csv)
    return merged


def clean_occurrences_by_tdwg_regions(occ_df: pd.DataFrame,
                                      families_in_occurrences: List[str] = None,
                                      output_csv: str = None):
    occ_with_acc_info = read_occurences_and_output_acc_names(occ_df, families_in_occurrences=families_in_occurrences)
    occ_with_tdwg = get_tdwg_regions_for_occurrences(occ_with_acc_info)
    matched_tdwg_info = match_taxa_to_wcsp_regions(occ_with_tdwg)

    print('Prioritising native')
    occ_in_native = matched_tdwg_info[(matched_tdwg_info['within_native'] == 1)]
    occ_in_introduced = matched_tdwg_info[(matched_tdwg_info['within_introduced'] == 1)]

    introd_occ_not_in_native = occ_in_introduced[
        ~occ_in_introduced['Accepted_ID'].isin(occ_in_native['Accepted_ID'].values)]
    occ_df_native_priority = pd.concat([occ_in_native, introd_occ_not_in_native])

    if output_csv is not None:
        occ_df_native_priority.to_csv(output_csv)

    return occ_df_native_priority


if __name__ == '__main__':
    var_occ_df = pd.read_csv(os.path.join(plant_occurences, 'outputs', 'cleaned_vari_occurences.csv'))
    cinch = pd.read_csv('unittests/test_inputs/occs_which_should_be_removed.csv')
    clean_occurrences_by_tdwg_regions(var_occ_df, families_in_occurrences=['Apocynaceae', 'Rubiaceae', 'Celastraceae'],
                                      output_csv='test.csv')
