import os

import pandas as pd
from automatchnames import remove_whitespace_at_beginning_and_end, get_accepted_info_from_names_in_column
from pkg_resources import resource_filename

from manually_collected_data import trait_parsing_output_path, encoded_traits_csv

rub_apoc_alk_hits_manual_output_csv = os.path.join(trait_parsing_output_path, 'rub_apocs_alks_manual.csv')

def get_manual_alk_hits():
    manual_df = pd.read_csv(encoded_traits_csv)
    # Get steroids
    alk_hits = manual_df[manual_df['Alkaloids'] == 1]

    alk_hits['Source'] = 'Manual'

    alk_hits.to_csv(rub_apoc_alk_hits_manual_output_csv)

def main():
    get_manual_alk_hits()


if __name__ == '__main__':
    main()