import os
import pickle

import pandas as pd
from automatchnames import get_accepted_info_from_names_in_column
from pkg_resources import resource_filename
from taxa_lists import get_all_taxa

from climate_vars import occurences_with_accepted_names_csv, families_in_occurrences
from getting_malarial_regions import malaria_country_codes_csv
from large_file_storage import large_folders, data_download
from wcsp_distributions import distributions_csv

_inputs_path = resource_filename(__name__, 'inputs')

_temp_outputs_path = resource_filename(__name__, 'temp_outputs')

_output_path = resource_filename(__name__, 'outputs')
occurrences_in_malarial_countries_csv = os.path.join(large_folders, 'occurrences_in_malarial_countries.csv')
taxa_in_malarial_countries_occ_csv = os.path.join(_output_path, 'taxa_in_malarial_countries_occ.csv')
taxa_in_malarial_countries_dist_csv = os.path.join(_output_path, 'taxa_in_malarial_countries_dist.csv')
if not os.path.isdir(_inputs_path):
    os.mkdir(_inputs_path)
if not os.path.isdir(_temp_outputs_path):
    os.mkdir(_temp_outputs_path)
if not os.path.isdir(_output_path):
    os.mkdir(_output_path)


def get_taxa_in_malarial_countries_from_occurrences():
    """

    :return:
    """
    # The `countryCode` column is in ISO-3 character, from GBIF but GBIF country codes can be patchy.
    occ_df = pd.read_csv(occurences_with_accepted_names_csv)
    malaria_country_codes_df = pd.read_csv(malaria_country_codes_csv)

    malarial_occurrences = occ_df[occ_df['countryCode'].isin(malaria_country_codes_df['iso3_codes'].values)]
    malarial_occurrences.to_csv(occurrences_in_malarial_countries_csv)

    acc_taxa = get_all_taxa(families_of_interest=families_in_occurrences, accepted=True,
                            ranks=['Species', 'Subspecies', 'Variety'])
    malarial_taxa = acc_taxa[acc_taxa['accepted_name'].isin(malarial_occurrences['Accepted_Name'].values)]
    malarial_taxa_acc = get_accepted_info_from_names_in_column(malarial_taxa, 'accepted_name',
                                                               families_of_interest=families_in_occurrences)
    malarial_taxa_acc.to_csv(taxa_in_malarial_countries_occ_csv)


def get_taxa_in_malarial_countries_from_wcsp_data():
    # TODO: redo this with new df
    wcsp_dists = pd.read_csv(distributions_csv)

    malaria_country_codes_df = pd.read_csv(malaria_country_codes_csv)

    ids_in_malarial_regions = []
    for idx, row in wcsp_dists:
        if any(iso_code in malaria_country_codes_df['iso3_codes'].values for iso_code in list(row['iso3_codes'])):
            ids_in_malarial_regions.append(row['kew_id'])

    acc_taxa = get_all_taxa(families_of_interest=families_in_occurrences, accepted=True,
                            ranks=['Species', 'Subspecies', 'Variety'])
    family_taxa_in_malarial_regions = acc_taxa[acc_taxa['kew_id'].isin(ids_in_malarial_regions)]

    malarial_taxa_acc = get_accepted_info_from_names_in_column(family_taxa_in_malarial_regions, 'accepted_name',
                                                               families_of_interest=families_in_occurrences)
    malarial_taxa_acc.to_csv(taxa_in_malarial_countries_dist_csv)


def main():
    get_taxa_in_malarial_countries_from_wcsp_data()
    # get_taxa_in_malarial_countries_from_occurrences()


if __name__ == '__main__':
    main()
