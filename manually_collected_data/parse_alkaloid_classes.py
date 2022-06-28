import os
from typing import List

import pandas as pd

from manually_collected_data import trait_parsing_output_path, encoded_traits_csv

parsed_alkaloid_classes_csv = os.path.join(trait_parsing_output_path, 'parsed_alkaloid_classes.csv')


def remove_whitespace_at_beginning_and_end(value):
    try:
        v = value.rstrip()
        out = v.lstrip()
        return out
    except AttributeError:
        return value


def OHE_alks(df: pd.DataFrame) -> pd.DataFrame:
    import numpy as np
    # OHE alks
    def convert_alks_to_lists(hab: str) -> List[str]:

        if hab == '?':
            raise ValueError
        try:
            if ';' not in hab:
                alk_list = [hab]
            else:
                alk_list = hab.split(';')
        except TypeError:
            raise ValueError
        else:
            out_list = list(map(remove_whitespace_at_beginning_and_end, alk_list))

            return out_list

    df['Alkaloid_mainclass'] = df['Alkaloid_mainclass'].apply(convert_alks_to_lists)

    multilabels = df['Alkaloid_mainclass'].str.join('|').str.get_dummies()
    multilabels = multilabels.add_prefix('alk_')
    df = df.join(multilabels)

    return df


def parse_alkaloid_data():
    input_alks = pd.read_csv(encoded_traits_csv, index_col=0)

    input_alks.dropna(subset=['Alkaloid_mainclass'], inplace=True)

    # OHE
    encoded = OHE_alks(input_alks)
    alk_cols_to_use = [c for c in encoded.columns.tolist() if 'alk_' in c]
    encoded = encoded[['Accepted_Name', 'Genus', 'Accepted_ID'] + alk_cols_to_use]
    encoded.to_csv(parsed_alkaloid_classes_csv)
    encoded.describe().to_csv(os.path.join(trait_parsing_output_path, 'alks summary.csv'))

    cols = [x for x in encoded.columns.tolist() if 'alk_' in x]

    def rmv_prefix(given_value: str):
        out = given_value[given_value.rindex('alk_') + len('alk_'):]
        return out

    cols_to_use = list(map(rmv_prefix, cols))

    pd.DataFrame(cols_to_use).to_csv('alks_to_parse.csv')


def main():
    parse_alkaloid_data()


if __name__ == '__main__':
    main()
