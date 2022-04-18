import os

import pandas as pd
from automatchnames import remove_whitespace_at_beginning_and_end, get_accepted_info_from_names_in_column
from pkg_resources import resource_filename

from manually_collected_data import trait_parsing_output_path

_input_path = resource_filename(__name__, 'inputs')
manual_steroid_input = os.path.join(_input_path, 'MPNS - Apocynaceae, cardenolides and steroids.csv')

rub_apoc_steroid_hits_manual_output_csv = os.path.join(trait_parsing_output_path, 'rub_apocs_steroid_manual.csv')
rub_apoc_cardenolide_hits_manual_output_csv = os.path.join(trait_parsing_output_path, 'rub_apocs_card_manual.csv')

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

    acc_steroids.to_csv(rub_apoc_steroid_hits_manual_output_csv)
    cardenolide_hits.to_csv(rub_apoc_cardenolide_hits_manual_output_csv)

def main():
    get_manual_steroid_card_hits()


if __name__ == '__main__':
    main()