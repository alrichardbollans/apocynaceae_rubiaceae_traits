import os

import pandas as pd
from pkg_resources import resource_filename

from cleaning import compile_hits, output_summary_of_hit_csv
from automatchnames import clean_urn_ids, get_accepted_info_from_names_in_column

### Inputs


_inputs_path = resource_filename(__name__, 'inputs')
_input_species_csv = os.path.join(_inputs_path, 'clean.csv')

_useful_plants_file = os.path.join(_inputs_path, 'useful_plant_processed_db.txt')
cornell_poison_file = os.path.join(_inputs_path, 'Plants Poisonous to Livestock Cornell University.html')
CPCS_poison_file = os.path.join(_inputs_path, 'California Poison Control System (CPCS).html')
UCANR_toxic_file = os.path.join(_inputs_path, 'UCANR_toxic.html')
UCANR_nontoxic_file = os.path.join(_inputs_path, 'UCANR_nontoxic.html')
usda_toxic_file = os.path.join(_inputs_path, 'USDA_Toxic.csv')
tppt_toxic_file = os.path.join(_inputs_path, 'TPPT_database.csv')
_clinitox_nontoxic_file = os.path.join(_inputs_path, 'CliniTox Toxicity Level - Non-Toxic.htm')
_clinitox_toxic_filenames = ['CliniTox Toxicity Level - Toxic.htm', 'CliniTox Toxicity Level - Highly Toxic.htm',
                             'CliniTox Toxicity Level - Very Highly Toxic.htm']

### Temp outputs
_temp_outputs_path = resource_filename(__name__, 'temp_outputs')
_littox_temp_output_accepted_csv = os.path.join(_temp_outputs_path, 'littox_accepted.csv')
_useful_temp_output_accepted_csv = os.path.join(_temp_outputs_path, 'useful_accepted.csv')
_powo_search_temp_output_accepted_csv = os.path.join(_temp_outputs_path, 'powo_poisons_accepted.csv')
_wiki_search_temp_output_csv = os.path.join(_temp_outputs_path, 'wiki_poisons.csv')
_wiki_search_temp_output_accepted_csv = os.path.join(_temp_outputs_path, 'wiki_poisons_accepted.csv')
_cornell_temp_accepted_csv = os.path.join(_temp_outputs_path, 'cornell_accepted.csv')
_CPCS_toxic_temp_accepted_csv = os.path.join(_temp_outputs_path, 'CPCS_toxic_accepted.csv')
_CPCS_nontoxic_temp_accepted_csv = os.path.join(_temp_outputs_path, 'CPCS_nontoxic_accepted.csv')
_UCANR_toxic_temp_accepted_csv = os.path.join(_temp_outputs_path, 'UCANR_toxic_accepted.csv')
_UCANR_nontoxic_temp_accepted_csv = os.path.join(_temp_outputs_path, 'UCANR_nontoxic_accepted.csv')
_usda_toxic_temp_accepted_csv = os.path.join(_temp_outputs_path, 'usda_toxic_accepted.csv')
_tppt_toxic_temp_accepted_csv = os.path.join(_temp_outputs_path, 'tppt_toxic_accepted.csv')
_clinitox_nontoxic_temp_accepted_csv = os.path.join(_temp_outputs_path, 'clinitox_nontoxic_accepted.csv')
_clinitox_toxic_temp_accepted_csv = os.path.join(_temp_outputs_path, 'clinitox_toxic_accepted.csv')

### Outputs
_output_path = resource_filename(__name__, 'outputs')
output_poison_csv = os.path.join(_output_path, 'list_of_poisonous_plants.csv')
output_nonpoison_csv = os.path.join(_output_path, 'list_of_nonpoisonous_plants.csv')


def prepare_cornell_data() -> pd.DataFrame:
    tables = pd.read_html(cornell_poison_file)
    tables[0]['Source'] = 'Cornell CALS'
    tables[0].rename(columns={'Scientific Name': 'Cornell_Snippet'}, inplace=True)
    db_acc = get_accepted_info_from_names_in_column(tables[0], 'Cornell_Snippet')
    db_acc.to_csv(_cornell_temp_accepted_csv)
    return db_acc


def prepare_CPCS_data():
    tables = pd.read_html(CPCS_poison_file)

    non_toxic_db = tables[1]
    # Remove letter headers
    non_toxic_db = non_toxic_db[~non_toxic_db['Latin or scientific name'].str.contains('^[A-Z]$', regex=True)]
    acc_non_toxic = get_accepted_info_from_names_in_column(non_toxic_db, 'Latin or scientific name')
    acc_non_toxic.rename(columns={'Latin or scientific name': 'CPCS_Snippet'}, inplace=True)
    acc_non_toxic['Source'] = 'CPCS'
    acc_non_toxic.to_csv(_CPCS_nontoxic_temp_accepted_csv)

    toxic_db = tables[4]
    toxic_db = toxic_db[~toxic_db['Latin or scientific name'].str.contains('^[A-Z]$', regex=True)]
    acc_toxic = get_accepted_info_from_names_in_column(toxic_db, 'Latin or scientific name')
    acc_toxic.rename(columns={'Latin or scientific name': 'CPCS_Snippet'}, inplace=True)
    acc_toxic['Source'] = 'CPCS'
    acc_toxic.to_csv(_CPCS_toxic_temp_accepted_csv)


def prepare_toxic_UCANR_data():
    toxic_tables = pd.read_html(UCANR_toxic_file, header=0)

    toxic_db = toxic_tables[0]
    acc_toxic = get_accepted_info_from_names_in_column(toxic_db, 'Toxic plants: Scientific name')
    acc_toxic['Source'] = 'UCANR'
    acc_toxic.rename(columns={'Toxic plants: Scientific name': 'UCANR_Snippet'}, inplace=True)
    acc_toxic.to_csv(_UCANR_toxic_temp_accepted_csv)


def prepare_usda_data():
    toxic_db = pd.read_csv(usda_toxic_file)
    acc_toxic = get_accepted_info_from_names_in_column(toxic_db, 'Plants with Activity Synergy')
    acc_toxic['Source'] = 'USDA(Duke)'
    acc_toxic.rename(columns={'Plants with Activity Synergy': 'USDA(Duke)_Snippet'}, inplace=True)
    acc_toxic.to_csv(_usda_toxic_temp_accepted_csv)


def prepare_TPPT_data():
    toxic_db = pd.read_csv(tppt_toxic_file)
    toxic_db = toxic_db[~(toxic_db['Human_toxicity'] == 'unknown')]
    acc_toxic = get_accepted_info_from_names_in_column(toxic_db, 'Latin_plant_name',
                                                       families_of_interest=toxic_db['Plant_family'].unique().tolist())
    acc_toxic['Source'] = 'TPPT'
    acc_toxic.rename(columns={'Latin_plant_name': 'TPPT_Snippet'}, inplace=True)
    acc_toxic.to_csv(_tppt_toxic_temp_accepted_csv)


def prepare_nontoxic_UCANR_data():
    nontoxic_tables = pd.read_html(UCANR_nontoxic_file, header=0)

    nontoxic_db = nontoxic_tables[0]
    acc_nontoxic = get_accepted_info_from_names_in_column(nontoxic_db, 'Safe plants: Scientific name')
    acc_nontoxic['Source'] = 'UCANR'
    acc_nontoxic.rename(columns={'Safe plants: Scientific name': 'UCANR_Snippet'}, inplace=True)
    acc_nontoxic.to_csv(_UCANR_nontoxic_temp_accepted_csv)


def prepare_nontoxic_clinitox_data():
    from bs4 import BeautifulSoup

    with open(_clinitox_nontoxic_file, 'r') as f:
        contents = f.read()
        list_elements = []
        soup = BeautifulSoup(contents, features="html.parser")
        for tag in soup.find_all('li'):
            list_elements.append(tag.text)
    out_dict = {'Safe plants: Scientific name': list_elements}
    nontoxic_db = pd.DataFrame(out_dict)
    acc_nontoxic = get_accepted_info_from_names_in_column(nontoxic_db, 'Safe plants: Scientific name')
    acc_nontoxic['Source'] = 'CliniTox'
    acc_nontoxic.rename(columns={'Safe plants: Scientific name': 'CliniTox_Snippet'}, inplace=True)
    acc_nontoxic.to_csv(_clinitox_nontoxic_temp_accepted_csv)


def prepare_toxic_clinitox_data():
    list_elements = []

    from bs4 import BeautifulSoup

    for fname in _clinitox_toxic_filenames:
        clin_file = os.path.join(_inputs_path, fname)
        with open(clin_file, 'r') as f:
            contents = f.read()

            soup = BeautifulSoup(contents, features="html.parser")
            for tag in soup.find_all('li'):
                list_elements.append(tag.text)
    out_dict = {'Toxic plants: Scientific name': list_elements}
    toxic_db = pd.DataFrame(out_dict)
    acc_toxic_db = get_accepted_info_from_names_in_column(toxic_db, 'Toxic plants: Scientific name')
    acc_toxic_db['Source'] = 'CliniTox'
    acc_toxic_db.rename(columns={'Toxic plants: Scientific name': 'CliniTox_Snippet'}, inplace=True)
    acc_toxic_db.to_csv(_clinitox_toxic_temp_accepted_csv)


def prepare_useful_plants_poisons() -> pd.DataFrame:
    useful_db = pd.read_csv(_useful_plants_file, encoding='latin_1', sep='\t')

    useful_db = useful_db[useful_db['Poisons'] == 1]
    #
    # useful_db.rename(
    #     columns={'acc_ipniid': 'Accepted_ID', 'binomial_acc_name': 'Accepted_Name'},
    #     inplace=True)
    # useful_db['Accepted_Rank'] = 'Species'
    # useful_db['Accepted_Species'] = useful_db['Accepted_Name']
    # useful_db['Accepted_Species_ID'] = useful_db['Accepted_ID']
    #
    # useful_db.dropna(subset=['Accepted_ID'], inplace=True)

    # Drop columns containing 'Source' as this gets confused when compiling all data
    cs = [c for c in useful_db.columns if 'Source' in c]
    useful_db.drop(columns=cs, inplace=True)
    # Then add a source column
    useful_db['Source'] = 'Useful Plants Data'
    useful_db.rename(columns={'binomial_acc_name': 'Useful_Plants_Snippet'}, inplace=True)
    useful_db_acc = get_accepted_info_from_names_in_column(useful_db, 'Useful_Plants_Snippet')
    useful_db_acc.to_csv(_useful_temp_output_accepted_csv)
    return useful_db_acc


def prepare_littox_poisons() -> pd.DataFrame:
    littox_db = pd.read_csv(os.path.join(_inputs_path, 'Littox_210428_copy.csv'))
    littox_db['Source'] = 'LITTOX'
    littox_db.rename(columns={'Latin name provided': 'LITTOX_Snippet'}, inplace=True)
    littox_db_acc = get_accepted_info_from_names_in_column(littox_db, 'LITTOX_Snippet')
    littox_db_acc.to_csv(_littox_temp_output_accepted_csv)
    return littox_db_acc


def get_powo_poisons():
    from powo_searches import search_powo
    search_powo(['poison', 'poisonous', 'toxic', 'deadly'],
                _powo_search_temp_output_accepted_csv,
                filters=['species', 'infraspecies']
                )


def get_wiki_poisons():
    import wikipedia_searches
    wiki_df = wikipedia_searches.search_for_poisons(_wiki_search_temp_output_csv)
    # wiki_df = pd.read_csv(_wiki_search_temp_output_csv, index_col=0)
    acc_wiki_df = get_accepted_info_from_names_in_column(wiki_df, 'name')
    acc_wiki_df.rename(columns={'name': 'wiki_Snippet'}, inplace=True)
    acc_wiki_df.to_csv(_wiki_search_temp_output_accepted_csv)

    return acc_wiki_df


def get_nonpoison_hits():
    if not os.path.isdir(_temp_outputs_path):
        os.mkdir(_temp_outputs_path)
    if not os.path.isdir(_output_path):
        os.mkdir(_output_path)

    prepare_CPCS_data()
    prepare_nontoxic_UCANR_data()
    prepare_nontoxic_clinitox_data()
    clinitox_hits = pd.read_csv(_clinitox_nontoxic_temp_accepted_csv)
    ucanr_hits = pd.read_csv(_UCANR_nontoxic_temp_accepted_csv)
    CPCS_hits = pd.read_csv(_CPCS_nontoxic_temp_accepted_csv)

    compile_hits([CPCS_hits, ucanr_hits, clinitox_hits], output_nonpoison_csv)




def get_poison_hits():
    if not os.path.isdir(_temp_outputs_path):
        os.mkdir(_temp_outputs_path)
    if not os.path.isdir(_output_path):
        os.mkdir(_output_path)

    get_wiki_poisons()
    get_powo_poisons()
    prepare_littox_poisons()
    prepare_useful_plants_poisons()

    prepare_cornell_data()
    prepare_CPCS_data()
    prepare_toxic_UCANR_data()
    prepare_usda_data()
    prepare_TPPT_data()
    prepare_toxic_clinitox_data()
    clinitox_hits = pd.read_csv(_clinitox_toxic_temp_accepted_csv)
    tppt_hits = pd.read_csv(_tppt_toxic_temp_accepted_csv)
    usda_hits = pd.read_csv(_usda_toxic_temp_accepted_csv)
    ucanr_hits = pd.read_csv(_UCANR_toxic_temp_accepted_csv)
    CPCS_hits = pd.read_csv(_CPCS_toxic_temp_accepted_csv)
    cornell_hits = pd.read_csv(_cornell_temp_accepted_csv)
    wiki_hits = pd.read_csv(_wiki_search_temp_output_accepted_csv)
    powo_hits = pd.read_csv(_powo_search_temp_output_accepted_csv)
    powo_hits['powo_name_Snippet'] = powo_hits['name']
    littox_hits = pd.read_csv(_littox_temp_output_accepted_csv)
    useful_hits = pd.read_csv(_useful_temp_output_accepted_csv)
    useful_hits['Accepted_Species_ID'] = useful_hits['Accepted_ID']
    compile_hits(
        [useful_hits, powo_hits, littox_hits, wiki_hits, cornell_hits, CPCS_hits, ucanr_hits, usda_hits, tppt_hits,
         clinitox_hits],
        output_poison_csv)


def output_source_summaries():
    output_summary_of_hit_csv(
        output_poison_csv,
        os.path.join(_output_path, 'source_summaries', 'poison_source_summary'),
        source_translations={'Wiki': '_wiki', 'POWO': 'POWO pages'})

    output_summary_of_hit_csv(
        output_nonpoison_csv,
        os.path.join(_output_path, 'source_summaries', 'nonpoison_source_summary'))


if __name__ == '__main__':
    get_poison_hits()
    get_nonpoison_hits()
