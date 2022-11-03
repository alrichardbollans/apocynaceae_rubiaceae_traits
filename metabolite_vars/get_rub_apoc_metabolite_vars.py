import os

import numpy as np
import pandas as pd

from pkg_resources import resource_filename
from powo_searches import search_powo
from taxa_lists import get_all_taxa
from automatchnames import COL_NAMES

from metabolite_searches import get_metabolites_for_taxa, output_alkaloids_from_metabolites, get_compound_hits_for_taxa, \
    get_antibac_metabolite_hits_for_taxa, recheck_taxa, output_steroids_from_metabolites, \
    output_cardenolides_from_metabolites, get_antimalarial_metabolite_hits_for_taxa, \
    get_inactive_antimalarial_metabolite_hits_for_taxa, get_manual_antimalarial_metabolite_hits_for_taxa
from cleaning import compile_hits, output_summary_of_hit_csv
from tqdm import tqdm

from manually_collected_data import rub_apoc_steroid_hits_manual_output_csv, \
    rub_apoc_cardenolide_hits_manual_output_csv, rub_apoc_alk_hits_manual_output_csv

_input_path = resource_filename(__name__, 'inputs')

_temp_output_path = resource_filename(__name__, 'temp_outputs')
_rub_apoc_steroid_hits_knapsack_output_csv = os.path.join(_temp_output_path, 'rub_apocs_steroid_knapsack.csv')
_rub_apoc_cardenolide_hits_knapsack_output_csv = os.path.join(_temp_output_path, 'rub_apocs_card_knapsack.csv')
_rub_apoc_alk_hits_knapsack_output_csv = os.path.join(_temp_output_path, 'rub_apocs_alk_knapsack.csv')
_powo_search_alks_temp_output_accepted_csv = os.path.join(_temp_output_path, 'powo_alks.csv')

_output_path = resource_filename(__name__, 'outputs')

rubiaceae_apocynaceae_metabolites_output_csv = os.path.join(_output_path, 'rub_apocs_metabolites.csv')
accepted_metabolites_output_csv = os.path.join(_output_path, 'accepted_metabolites.csv')
unaccepted_metabolites_output_csv = os.path.join(_output_path, 'unaccepted_metabolites.csv')
_rubiaceae_apocynaceae_alks_output_csv = os.path.join(_output_path, 'rub_apocs_alkaloids.csv')
_rubiaceae_apocynaceae_steroid_output_csv = os.path.join(_output_path, 'rub_apocs_steroids.csv')
_rubiaceae_apocynaceae_cardenolide_output_csv = os.path.join(_output_path, 'rub_apocs_cardenolides.csv')

rub_apoc_alkaloid_hits_output_csv = os.path.join(_output_path, 'rub_apocs_alkaloid_hits.csv')
rub_apoc_steroid_hits_output_csv = os.path.join(_output_path, 'rub_apocs_steroid_hits.csv')
rub_apoc_cardenolide_hits_output_csv = os.path.join(_output_path, 'rub_apocs_cardenolides_hits.csv')

rub_apoc_antibac_metabolite_hits_output_csv = os.path.join(_output_path, 'rub_apocs_antibac_metabolites_hits.csv')
rub_apoc_knapsack_antimal_metabolite_hits_output_csv = os.path.join(_output_path, 'rub_apocs_knapsack_antimalarial_metabolites_hits.csv')
rub_apoc_manual_antimal_metabolite_hits_output_csv = os.path.join(_output_path, 'rub_apocs_manual_antimalarial_metabolites_hits.csv')
rub_apoc_inactive_antimal_metabolite_hits_output_csv = os.path.join(_output_path,
                                                                    'rub_apocs_inactive_antimalarial_metabolites_hits.csv')
_check_output_csv = os.path.join(_output_path, 'rechecked_taxa.csv')


def get_rub_apoc_metabolites():
    wcvp_data = get_all_taxa(families_of_interest=['Apocynaceae', 'Rubiaceae'],
                             ranks=["Species", "Variety", "Subspecies"])
    accepted_data = wcvp_data[wcvp_data['taxonomic_status'] == 'Accepted']
    accepted_metabolites_df = get_metabolites_for_taxa(accepted_data["taxon_name"].values,
                                                         output_csv=accepted_metabolites_output_csv)

    unaccepted_data = wcvp_data[wcvp_data['taxonomic_status'] != 'Accepted']

    unaccepted_metabolites_df = get_metabolites_for_taxa(unaccepted_data["taxon_name"].values,
                                                       output_csv=unaccepted_metabolites_output_csv)

    # accepted_metabolites_df = pd.read_csv(accepted_metabolites_output_csv, index_col=0)
    # unaccepted_metabolites_df = pd.read_csv(unaccepted_metabolites_output_csv, index_col=0)
    # Add new columns
    out_df = accepted_metabolites_df.copy()
    lower_cols = [x.lower() for x in out_df.columns]
    for c in unaccepted_metabolites_df.columns:
        if c.lower() not in lower_cols:
            out_df[c] = 0

    for i in tqdm(range(len(unaccepted_metabolites_df['Accepted_Name'].tolist())), desc="testing", ascii=False,
                  ncols=72):
        acc_name = unaccepted_metabolites_df['Accepted_Name'].tolist()[i]
        # print(acc_name)
        taxa_df = unaccepted_metabolites_df[unaccepted_metabolites_df['Accepted_Name'] == acc_name]
        for c in unaccepted_metabolites_df.columns:

            if c not in ['taxa'] + list(COL_NAMES.values()):
                x = taxa_df[c].max()
                if c not in out_df.columns:
                    # rename c to match out_df
                    # this is an issue caused by capitals in knapsack data.
                    # In future best to resolve this by lower casing all strings on import.
                    c = [x for x in out_df.columns if x.lower() == c.lower()][0]

                if c not in out_df.columns:
                    print(c)
                    raise ValueError

                if x == 1:
                    out_df.loc[out_df['Accepted_Name'] == acc_name, c] = 1

    out_df = out_df.fillna(0)
    out_df.to_csv(rubiaceae_apocynaceae_metabolites_output_csv)


def get_rub_apoc_alkaloid_hits():
    # Knapsack
    metabolites_to_check = pd.read_csv(rubiaceae_apocynaceae_metabolites_output_csv).columns.tolist()

    alks_df = output_alkaloids_from_metabolites(metabolites_to_check, _rubiaceae_apocynaceae_alks_output_csv)

    rubs_apoc_metas_data = pd.read_csv(rubiaceae_apocynaceae_metabolites_output_csv)
    get_compound_hits_for_taxa('alks', rubs_apoc_metas_data, alks_df, _rub_apoc_alk_hits_knapsack_output_csv,
                               fams=['Rubiaceae', 'Apocynaceae'])

    # POWO
    search_powo(['alkaloid'],
                _powo_search_alks_temp_output_accepted_csv, families_of_interest=['Rubiaceae', 'Apocynaceae'],
                filters=['species', 'infraspecies'])

    # Compile
    powo_hits = pd.read_csv(_powo_search_alks_temp_output_accepted_csv)
    knapsack_alk_hits = pd.read_csv(_rub_apoc_alk_hits_knapsack_output_csv)
    manual_alk_hits = pd.read_csv(rub_apoc_alk_hits_manual_output_csv)

    compile_hits([manual_alk_hits, knapsack_alk_hits, powo_hits], rub_apoc_alkaloid_hits_output_csv)

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
    get_compound_hits_for_taxa('cardenolides', rubs_apoc_metas_data, card_df,
                               _rub_apoc_cardenolide_hits_knapsack_output_csv,
                               fams=['Rubiaceae', 'Apocynaceae'])


def summarise_metabolites():
    metas_data = pd.read_csv(rubiaceae_apocynaceae_metabolites_output_csv)
    summ = metas_data.describe()
    print(summ)
    worthwhile_metabolites = [x for x in summ.columns if summ[x]['mean'] > 0.001]
    print(worthwhile_metabolites)


def get_rub_apoc_antibac_metabolite_hits():
    all_metas_data = pd.read_csv(rubiaceae_apocynaceae_metabolites_output_csv)
    get_antibac_metabolite_hits_for_taxa(all_metas_data, rub_apoc_antibac_metabolite_hits_output_csv,
                                         fams=['Rubiaceae', 'Apocynaceae'])

def get_rub_apoc_knapsack_antimal_metabolite_hits():
    all_metas_data = pd.read_csv(rubiaceae_apocynaceae_metabolites_output_csv)
    get_antimalarial_metabolite_hits_for_taxa(all_metas_data, rub_apoc_knapsack_antimal_metabolite_hits_output_csv,
                                              fams=['Rubiaceae', 'Apocynaceae'])

def get_rub_apoc_manual_antimal_metabolite_hits():
    all_metas_data = pd.read_csv(rubiaceae_apocynaceae_metabolites_output_csv)
    get_manual_antimalarial_metabolite_hits_for_taxa(all_metas_data, rub_apoc_manual_antimal_metabolite_hits_output_csv,
                                                     fams=['Rubiaceae', 'Apocynaceae'])

def get_rub_apoc_inactive_antimal_metabolite_hits():
    all_metas_data = pd.read_csv(rubiaceae_apocynaceae_metabolites_output_csv)
    get_inactive_antimalarial_metabolite_hits_for_taxa(all_metas_data,
                                                       rub_apoc_inactive_antimal_metabolite_hits_output_csv,
                                                       fams=['Rubiaceae', 'Apocynaceae'])


def get_steroid_card_hits():
    get_rub_apoc_knapsack_steroid_hits()
    get_rub_apoc_knapsack_cardenolide_hits()

    manual_steroid_hits = pd.read_csv(rub_apoc_steroid_hits_manual_output_csv)
    knapsack_steroid_hits = pd.read_csv(_rub_apoc_steroid_hits_knapsack_output_csv)

    compile_hits([manual_steroid_hits, knapsack_steroid_hits], rub_apoc_steroid_hits_output_csv)

    manual_cardenolide_hits = pd.read_csv(rub_apoc_cardenolide_hits_manual_output_csv)
    knapsack_cardenolide_hits = pd.read_csv(_rub_apoc_cardenolide_hits_knapsack_output_csv)

    compile_hits([manual_cardenolide_hits, knapsack_cardenolide_hits], rub_apoc_cardenolide_hits_output_csv)


def output_source_summaries():
    output_summary_of_hit_csv(
        rub_apoc_steroid_hits_output_csv,
        os.path.join(_output_path, 'source_summaries', 'steroid_source_summary'),
        families=['Apocynaceae', 'Rubiaceae'], ranks=['Species'])

    output_summary_of_hit_csv(
        rub_apoc_cardenolide_hits_output_csv,
        os.path.join(_output_path, 'source_summaries', 'cardenolide_source_summary'),
        families=['Apocynaceae', 'Rubiaceae'], ranks=['Species'])

    output_summary_of_hit_csv(
        rub_apoc_alkaloid_hits_output_csv,
        os.path.join(_output_path, 'source_summaries', 'alkaloid_source_summary'),
        families=['Apocynaceae', 'Rubiaceae'],
        source_translations={'POWO': 'POWO pages'}, ranks=['Species'])
def main():
    get_rub_apoc_metabolites()
    recheck_taxa(_check_output_csv)
    summarise_metabolites()
    get_rub_apoc_knapsack_antimal_metabolite_hits()
    get_rub_apoc_manual_antimal_metabolite_hits()
    get_rub_apoc_inactive_antimal_metabolite_hits()
    get_rub_apoc_antibac_metabolite_hits()
    get_rub_apoc_alkaloid_hits()

    get_steroid_card_hits()
    output_source_summaries()

if __name__ == '__main__':
    main()
