import os

import pandas as pd

from manually_collected_data import trait_parsing_output_path, encoded_traits_csv

rub_apoc_alk_hits_manual_output_csv = os.path.join(trait_parsing_output_path, 'rub_apocs_alks_manual.csv')


def get_manual_alk_hits():
    manual_df = pd.read_csv(encoded_traits_csv,index_col=0)
    presence_alk_strings = manual_df[manual_df['Alkaloids'] == 1]['Alkaloids_test_notes'].unique().tolist()
    absence_alk_strings = manual_df[manual_df['Alkaloids'] == 0]['Alkaloids_test_notes'].unique().tolist()

    presence_alk_csv = os.path.join(trait_parsing_output_path, "presence_alk_strings.csv")
    print('##### Presence alkaloid strings:')
    for a in presence_alk_strings:
        print(a)
    with open(presence_alk_csv, 'w') as f:
        for line in presence_alk_strings:
            f.write(f"{line}\n")

    print('##### Absence alkaloid strings:')
    for a in absence_alk_strings:
        print(a)

    absence_alk_csv = os.path.join(trait_parsing_output_path, "absence_alk_strings.csv")

    with open(absence_alk_csv, 'w') as f:
        for line in absence_alk_strings:
            f.write(f"{line}\n")
    # Get alks
    alk_hits = manual_df[manual_df['Alkaloids'] == 1]

    alk_hits.to_csv(rub_apoc_alk_hits_manual_output_csv)


def main():
    get_manual_alk_hits()


if __name__ == '__main__':
    main()
