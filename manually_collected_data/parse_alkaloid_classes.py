import os
from typing import List

import numpy as np
import pandas as pd

from manually_collected_data import trait_parsing_output_path, encoded_traits_csv

parsed_alkaloid_classes_csv = os.path.join(trait_parsing_output_path, 'parsed_alkaloid_classes.csv')

_conal_alk_class_columns = ['Alkaloid_mainclass(conal)', 'Alkaloid_otherclasses']
_alk_class_presence_column = 'Alkaloid_classes'
_alk_class_absence_column = 'Alkaloid_class_absences'


def remove_whitespace_at_beginning_and_end(value: str):
    try:
        v = value.rstrip()
        out = v.lstrip()
        return out
    except AttributeError:
        return value


def remove_reference_in_string(val: str):
    import re
    return re.sub("[\[].*?[\]]", "", val)


def lower_case_string(val: str):
    return val.lower()


def convert_alks_in_cols_to_lists(hab: str) -> List[str]:
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
        out_list = list(map(remove_reference_in_string, alk_list))
        out_list = list(map(remove_whitespace_at_beginning_and_end, out_list))

        out_list = list(map(lower_case_string, out_list))

        return out_list


def OHE_alks(df: pd.DataFrame, class_col: str) -> pd.DataFrame:
    # OHE alks

    df[class_col] = df[class_col].apply(convert_alks_in_cols_to_lists)

    multilabels = df[class_col].str.join('|').str.get_dummies()
    multilabels = multilabels.add_prefix('alk_')
    df = df.join(multilabels)

    return df


def parse_alkaloid_data():
    name_cols_to_use = ['Genus', 'Accepted_Name', 'Accepted_ID', 'Accepted_Species', 'Accepted_Species_ID',
                        'Accepted_Rank']
    trait_df = pd.read_csv(encoded_traits_csv, index_col=0)

    # OHE presence
    input_presence_alks = trait_df.dropna(subset=_alk_class_presence_column)
    presence_encoded = OHE_alks(input_presence_alks, _alk_class_presence_column)

    alk_cols_to_use = [c for c in presence_encoded.columns.tolist() if 'alk_' in c]
    presence_encoded = presence_encoded[name_cols_to_use + alk_cols_to_use]

    # OHE absence
    input_absence_alks = trait_df.dropna(subset=_alk_class_absence_column)
    absence_encoded = OHE_alks(input_absence_alks, _alk_class_absence_column)

    absence_alk_cols_to_use = [c for c in absence_encoded.columns.tolist() if 'alk_' in c]
    absence_encoded = absence_encoded[name_cols_to_use + absence_alk_cols_to_use]
    absence_encoded = absence_encoded.replace(0, np.nan)
    absence_encoded = absence_encoded.replace(1, 0)

    encoded = pd.merge(presence_encoded, absence_encoded, how='outer')

    # Add zero entries
    zero_alks = trait_df[trait_df['Alkaloids'] == 0][name_cols_to_use]
    for alk_col in alk_cols_to_use:
        zero_alks[alk_col] = 0

    encoded = pd.concat([encoded, zero_alks])

    encoded.to_csv(parsed_alkaloid_classes_csv)
    encoded.describe().to_csv(os.path.join(trait_parsing_output_path, 'alks summary.csv'))

    cols = [x for x in encoded.columns.tolist() if 'alk_' in x]

    def rmv_prefix(given_value: str):
        out = given_value[given_value.rindex('alk_') + len('alk_'):]
        return out

    cols_to_use = list(map(rmv_prefix, cols))
    print(cols_to_use)
    pd.DataFrame(cols_to_use).to_csv('alks_to_parse.csv')


def main():
    parse_alkaloid_data()


if __name__ == '__main__':
    main()
