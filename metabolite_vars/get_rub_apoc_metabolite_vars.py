import os

import pandas as pd
from automatchnames import remove_whitespace_at_beginning_and_end, get_accepted_info_from_names_in_column
from pkg_resources import resource_filename
from taxa_lists import get_all_taxa

from metabolite_searches import get_metabolites_for_taxa, output_alkaloids_from_metabolites, get_compound_hits_for_taxa, \
    get_antibac_metabolite_hits_for_taxa, recheck_taxa, output_steroids_from_metabolites, \
    output_cardenolides_from_metabolites
from cleaning import compile_hits

_input_path = resource_filename(__name__, 'inputs')
manual_steroid_input = os.path.join(_input_path, 'MPNS - Apocynaceae, cardenolides and steroids.csv')


_temp_output_path = resource_filename(__name__, 'temp_outputs')
_rub_apoc_steroid_hits_knapsack_output_csv = os.path.join(_temp_output_path, 'rub_apocs_steroid_knapsack.csv')
_rub_apoc_cardenolide_hits_knapsack_output_csv = os.path.join(_temp_output_path, 'rub_apocs_card_knapsack.csv')

_rub_apoc_steroid_hits_manual_output_csv = os.path.join(_temp_output_path, 'rub_apocs_steroid_manual.csv')
_rub_apoc_cardenolide_hits_manual_output_csv = os.path.join(_temp_output_path, 'rub_apocs_card_manual.csv')

_output_path = resource_filename(__name__, 'outputs')

rubiaceae_apocynaceae_metabolites_output_csv = os.path.join(_output_path, 'rub_apocs_metabolites.csv')
_rubiaceae_apocynaceae_alks_output_csv = os.path.join(_output_path, 'rub_apocs_alkaloids.csv')
_rubiaceae_apocynaceae_steroid_output_csv = os.path.join(_output_path, 'rub_apocs_steroids.csv')
_rubiaceae_apocynaceae_cardenolide_output_csv = os.path.join(_output_path, 'rub_apocs_cardenolides.csv')



rub_apoc_alkaloid_hits_output_csv = os.path.join(_output_path, 'rub_apocs_alkaloid_hits.csv')
rub_apoc_steroid_hits_output_csv = os.path.join(_output_path, 'rub_apocs_steroid_hits.csv')
rub_apoc_cardenolide_hits_output_csv = os.path.join(_output_path, 'rub_apocs_cardenolides_hits.csv')

rub_apoc_antibac_metabolites_output_csv = os.path.join(_output_path, 'rub_apocs_antibac_metabolites.csv')
_check_output_csv = os.path.join(_output_path, 'rechecked_taxa.csv')


def get_rub_apoc_metabolites():
    data = get_all_taxa(families_of_interest=['Apocynaceae', 'Rubiaceae'], accepted=True)

    ranks_to_use = ["Species", "Variety", "Subspecies"]

    taxa = data.loc[data["rank"].isin(ranks_to_use)]

    taxa_list = taxa["taxon_name"].values

    get_metabolites_for_taxa(taxa_list, output_csv=rubiaceae_apocynaceae_metabolites_output_csv)


def get_rub_apoc_alkaloid_hits():
    metabolites_to_check = pd.read_csv(rubiaceae_apocynaceae_metabolites_output_csv).columns.tolist()

    alks_df = output_alkaloids_from_metabolites(metabolites_to_check, _rubiaceae_apocynaceae_alks_output_csv)

    rubs_apoc_metas_data = pd.read_csv(rubiaceae_apocynaceae_metabolites_output_csv)
    get_compound_hits_for_taxa('alks', rubs_apoc_metas_data, alks_df, rub_apoc_alkaloid_hits_output_csv,
                               fams=['Rubiaceae', 'Apocynaceae'])


def get_rub_apoc_knapsack_steroid_hits():
    metabolites_to_check = pd.read_csv(rubiaceae_apocynaceae_metabolites_output_csv).columns.tolist()

    steroid_df = output_steroids_from_metabolites(metabolites_to_check, _rubiaceae_apocynaceae_steroid_output_csv)

    rubs_apoc_metas_data = pd.read_csv(rubiaceae_apocynaceae_metabolites_output_csv)
    get_compound_hits_for_taxa('steroids', rubs_apoc_metas_data, steroid_df, _rub_apoc_steroid_hits_knapsack_output_csv,
                               fams=['Rubiaceae', 'Apocynaceae'])


def get_rub_apoc_knapsack_cardenolide_hits():
    metabolites_to_check = pd.read_csv(rubiaceae_apocynaceae_metabolites_output_csv).columns.tolist()

    card_df = output_cardenolides_from_metabolites(metabolites_to_check, _rubiaceae_apocynaceae_cardenolide_output_csv)

    rubs_apoc_metas_data = pd.read_csv(rubiaceae_apocynaceae_metabolites_output_csv)
    get_compound_hits_for_taxa('cardenolides', rubs_apoc_metas_data, card_df, _rub_apoc_cardenolide_hits_knapsack_output_csv,
                               fams=['Rubiaceae', 'Apocynaceae'])


def summarise_metabolites():
    metas_data = pd.read_csv(rubiaceae_apocynaceae_metabolites_output_csv)
    summ = metas_data.describe()
    print(summ)
    worthwhile_metabolites = [x for x in summ.columns if summ[x]['mean'] > 0.001]
    print(worthwhile_metabolites)


def get_rub_apoc_antibac_metabolite_hits():
    all_metas_data = pd.read_csv(rubiaceae_apocynaceae_metabolites_output_csv)
    get_antibac_metabolite_hits_for_taxa(all_metas_data, rub_apoc_antibac_metabolites_output_csv,
                                         fams=['Rubiaceae', 'Apocynaceae'])


def get_manual_steroid_card_hits():
    manual_df = pd.read_csv(manual_steroid_input,encoding='windows-1252')
    yes_no_column = 'Cardenolides/Steroids?'
    manual_df[yes_no_column] = manual_df[yes_no_column].apply(remove_whitespace_at_beginning_and_end)
    manual_df[yes_no_column] = manual_df[yes_no_column].replace(r"\byes(?i)\b", value=1, regex=True)

    manual_df[yes_no_column] = manual_df[yes_no_column].replace(r'\bno(?i)\b', value=0, regex=True)

    # Get steroids
    steroid_hits = manual_df[manual_df[yes_no_column] == 1]

    steroid_hits['Source'] = 'Manual'

    # Create single name
    steroid_hits['Genus'] = steroid_hits['Genus'].apply(remove_whitespace_at_beginning_and_end)
    steroid_hits['Species'] = steroid_hits['Species'].apply(remove_whitespace_at_beginning_and_end)
    steroid_hits['Name'] = steroid_hits['Genus'] + " " + steroid_hits['Species']

    # Get accepted info
    acc_steroids = get_accepted_info_from_names_in_column(steroid_hits, 'Name')

    cardenolide_hits = acc_steroids[acc_steroids['Description'].str.contains('ardenolide')]

    acc_steroids.to_csv(_rub_apoc_steroid_hits_manual_output_csv)
    cardenolide_hits.to_csv(_rub_apoc_cardenolide_hits_manual_output_csv)


def get_steroid_card_hits():
    get_manual_steroid_card_hits()
    get_rub_apoc_knapsack_steroid_hits()
    get_rub_apoc_knapsack_cardenolide_hits()

    manual_steroid_hits = pd.read_csv(_rub_apoc_steroid_hits_manual_output_csv)
    knapsack_steroid_hits = pd.read_csv(_rub_apoc_steroid_hits_knapsack_output_csv)

    compile_hits([manual_steroid_hits, knapsack_steroid_hits], rub_apoc_steroid_hits_output_csv)

    manual_cardenolide_hits = pd.read_csv(_rub_apoc_cardenolide_hits_manual_output_csv)
    knapsack_cardenolide_hits = pd.read_csv(_rub_apoc_cardenolide_hits_knapsack_output_csv)

    compile_hits([manual_cardenolide_hits, knapsack_cardenolide_hits], rub_apoc_cardenolide_hits_output_csv)

def main():
    # get_rub_apoc_metabolites()
    # # recheck_taxa(_check_output_csv)
    # summarise_metabolites()
    # get_rub_apoc_antibac_metabolite_hits()
    # get_rub_apoc_alkaloid_hits()

    get_steroid_card_hits()


if __name__ == '__main__':
    main()
