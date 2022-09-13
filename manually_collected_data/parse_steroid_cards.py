import os

import pandas as pd
from automatchnames import remove_whitespace_at_beginning_and_end, get_accepted_info_from_names_in_column
from pkg_resources import resource_filename

from manually_collected_data import trait_parsing_output_path, encoded_traits_csv

_input_path = resource_filename(__name__, 'inputs')
rub_apoc_steroid_hits_manual_output_csv = os.path.join(trait_parsing_output_path, 'rub_apocs_steroid_manual.csv')
rub_apoc_cardenolide_hits_manual_output_csv = os.path.join(trait_parsing_output_path, 'rub_apocs_card_manual.csv')

def get_manual_steroid_hits():
    manual_df = pd.read_csv(encoded_traits_csv, index_col=0
                            )
    # Get steroids
    steroid_hits = manual_df[manual_df['Steroids'] == 1]

    steroid_hits.to_csv(rub_apoc_steroid_hits_manual_output_csv)


def get_manual_cardenolide_hits():
    manual_df = pd.read_csv(encoded_traits_csv, index_col=0
                            )
    # Get cardenolides
    cardenolide_hits = manual_df[manual_df['Cardenolides'] == 1]

    cardenolide_hits.to_csv(rub_apoc_cardenolide_hits_manual_output_csv)


def main():
    get_manual_steroid_hits()
    get_manual_cardenolide_hits()


if __name__ == '__main__':
    main()