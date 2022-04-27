import os.path

import numpy as np
import pandas as pd
# Add progress bar to apply method
from tqdm import tqdm

tqdm.pandas()
from manually_collected_data import ORDER_STANDARDISED_CSV, trait_parsing_output_path

TARGET_COLUMN = "Activity_Antimalarial"
encoded_traits_csv = os.path.join(trait_parsing_output_path, 'encoded_traits.csv')


def ordinal_encode(activity_value: str) -> int:
    try:
        activity_value = activity_value.lower()
        if "inactive" in activity_value:
            return 0
        elif "weak" in activity_value:
            return 0
        elif "active" in activity_value:
            return 1
        else:
            raise ValueError(f'Unrecognised activity: {activity_value}')
    except AttributeError:
        return np.nan


def clean_activities(given_activity: str) -> str:
    try:
        given_activity = given_activity.lower()
        if "inactive" in given_activity:
            return "Inactive"
        elif "weak" in given_activity:
            return "Weak"
        elif "active" in given_activity:
            return "Active"
        else:
            raise ValueError('Unrecognised activity')
    except AttributeError:
        return np.nan


def encode_activity(df: pd.DataFrame):
    # If activity is empty, take authors decision
    df[TARGET_COLUMN] = df[TARGET_COLUMN].fillna(df.Authors_Activity_Label)
    # Standardise activity column
    df[TARGET_COLUMN] = df[TARGET_COLUMN].apply(clean_activities)
    df[TARGET_COLUMN] = df[TARGET_COLUMN].apply(ordinal_encode)


def encode_alkaloids(df: pd.DataFrame):
    df['Alkaloids'] = df['Alkaloids'].apply(clean_alkaloids)
    df.loc[(df['Tested_for_Alkaloids'].isna()) & (df['Alkaloids'] == 0), 'Alkaloids'] = np.nan


def clean_alkaloids(given_value: str) -> int:
    # TODO: Manually go through this
    given_value = str(given_value).lower()
    # Previous steps may have added instances, check for these first
    if given_value == '1' or given_value == '1.0':
        return 1
    if given_value == '0' or given_value == '0.0':
        return 0

    test_names = ["dragendorff", "hager", "wagner", "mayer", "phytochemical screening"]
    presence_names = ["unclear", "detected", "isolated"]
    try:
        if "not detected" in given_value:
            print(f'no alkaloids: {given_value}')
            return 0
        elif any(x in given_value for x in presence_names):
            print(f'alkaloids: {given_value}')

            return 1
        elif any(x in given_value for x in test_names):
            print(f'alkaloids: {given_value}')

            return 1
        else:
            raise AttributeError(f'Unrecognised alkaloids: {given_value}')
    except AttributeError as e:
        if not given_value == "nan":
            print(e)
        return np.nan


def replace_yes_no_in_column(df: pd.DataFrame, column_name: str):
    '''
    Changes 'Yes' to 1 and <Nan> to 0 in given column
    :param df:
    :param column_name:
    :return:
    '''

    df[column_name] = df[column_name].replace(r"\byes(?i)\b", value=1, regex=True)

    df[column_name] = df[column_name].replace(r'\bno(?i)\b', value=0, regex=True)


def encode_features(df: pd.DataFrame) -> pd.DataFrame:
    encode_alkaloids(df)
    encode_activity(df)
    replace_yes_no_in_column(df, 'History_Antimalarial')
    replace_yes_no_in_column(df, 'History_Fever')

    def encode_family(fam: str) -> float:
        if fam == "Apocynaceae":
            return 0
        elif fam == "Rubiaceae":
            return 1
        else:
            raise ValueError

    df['Encoded_Family'] = df['Family'].apply(encode_family)

    return df


def main():
    trait_df = pd.read_csv(ORDER_STANDARDISED_CSV, index_col=0)

    trait_df.reset_index(inplace=True, drop=True)

    out_df = encode_features(trait_df)

    out_df.to_csv(encoded_traits_csv)


if __name__ == '__main__':
    main()
