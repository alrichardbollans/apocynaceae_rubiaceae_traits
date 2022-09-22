import ast
import os
import unittest

import pandas as pd
from automatchnames import get_accepted_info_from_names_in_column
from clean_plant_occurrences import read_occurences_and_output_acc_names, \
    find_whether_occurrences_in_native_or_introduced_regions, get_tdwg_regions_for_occurrences
from pkg_resources import resource_filename
from tqdm import tqdm

from cleaning_plant_occurrences import final_occurrence_output_csv, clean_occurrences_by_tdwg_regions
from large_file_storage import plant_occurences
from wcsp_distributions import distributions_csv

input_test_dir = resource_filename(__name__, 'test_inputs')
test_output_dir = resource_filename(__name__, 'test_outputs')

_final_cleaned_output_df = pd.read_csv(final_occurrence_output_csv, index_col=0)
_native_cleaned_output_df = pd.read_csv(
    os.path.join(plant_occurences, 'outputs', 'final_native_cleaned_occurrences.csv'), index_col=0)


class MyTestCase(unittest.TestCase):

    def test_bad_records(self):
        bad_records = pd.read_csv(os.path.join(input_test_dir, 'occs_which_should_be_removed.csv'))
        bad_records_with_acc_info = read_occurences_and_output_acc_names(bad_records)
        native_cleaned = clean_occurrences_by_tdwg_regions(bad_records_with_acc_info, distributions_csv,
                                                           priority='native',
                                                           output_csv=os.path.join(test_output_dir,
                                                                                   'native_should_be_empty.csv'))
        self.assertEqual(len(native_cleaned.index), 0)

        both_cleaned = clean_occurrences_by_tdwg_regions(bad_records_with_acc_info, distributions_csv,
                                                         priority='both',
                                                         output_csv=os.path.join(test_output_dir,
                                                                                 'both_should_be_empty.csv'))
        self.assertEqual(len(both_cleaned.index), 0)

        native_then_introduced_cleaned = clean_occurrences_by_tdwg_regions(bad_records_with_acc_info, distributions_csv,
                                                                           priority='native_then_introduced',
                                                                           output_csv=os.path.join(test_output_dir,
                                                                                                   'native_then_introduced_should_be_empty.csv'))
        self.assertEqual(len(native_then_introduced_cleaned.index), 0)

    def test_bad_records_not_in_output(self):
        bad_records = pd.read_csv(os.path.join(input_test_dir, 'occs_which_should_be_removed.csv'))
        for id in bad_records['gbifID'].values:
            self.assertNotIn(id, _final_cleaned_output_df['gbifID'].values)
            self.assertNotIn(id, _native_cleaned_output_df['gbifID'].values)

    def test_good_native_records(self):
        good_native_records = pd.read_csv(os.path.join(input_test_dir, 'native_ok.csv'))
        good_records_with_acc_info = read_occurences_and_output_acc_names(good_native_records)
        occ_with_tdwg = get_tdwg_regions_for_occurrences(good_records_with_acc_info)
        matched_tdwg_info = find_whether_occurrences_in_native_or_introduced_regions(occ_with_tdwg, distributions_csv,
                                                                                     output_csv=os.path.join(
                                                                                         test_output_dir,
                                                                                         'good_native_with_tdwg.csv'))

        native_cleaned = clean_occurrences_by_tdwg_regions(good_records_with_acc_info, distributions_csv,
                                                           priority='native',
                                                           output_csv=os.path.join(test_output_dir,
                                                                                   'native_native.csv'))
        diff = good_native_records[~good_native_records['gbifID'].isin(native_cleaned['gbifID'])]
        print(diff['gbifID'])
        self.assertEqual(len(diff.index), 0)

        native_cleaned = clean_occurrences_by_tdwg_regions(good_records_with_acc_info, distributions_csv,
                                                           priority='both',
                                                           output_csv=os.path.join(test_output_dir,
                                                                                   'native_both.csv'))
        self.assertEqual(len(native_cleaned.index), len(good_native_records.index))

        native_cleaned = clean_occurrences_by_tdwg_regions(good_records_with_acc_info, distributions_csv,
                                                           priority='native_then_introduced',
                                                           output_csv=os.path.join(test_output_dir,
                                                                                   'native_native_then_introduced.csv'))
        self.assertEqual(len(native_cleaned.index), len(good_native_records.index))

    def test_clean_output_for_standard_criteria(self):
        def test_examples(occ_df: pd.DataFrame, tag: str):
            dups = occ_df[occ_df.duplicated(subset=['gbifID'])]
            self.assertEqual(len(dups.index), 0)

            # Coord uncertainty 20000
            print('coord uncertainty clean')
            uncertain = occ_df[occ_df['coordinateUncertaintyInMeters'] > 20000]
            uncertain.to_csv(os.path.join(test_output_dir, tag + 'bad_coord_examples.csv'))
            # clim_occ_df = clim_occ_df[clim_occ_df['coordinateUncertaintyInMeters'] <= 20000]

            self.assertEqual(len(uncertain.index), 0)

            ## Years
            uncertain = occ_df[occ_df['year'] < 1945]
            uncertain.to_csv(os.path.join(test_output_dir, tag + 'bad_year_examples.csv'))
            self.assertEqual(len(uncertain.index), 0)
            ## 0 long and lat
            uncertain = occ_df[(occ_df['decimalLongitude'] == 0) & (occ_df['decimalLatitude'] == 0)]
            uncertain.to_csv(os.path.join(test_output_dir, tag + 'bad_zerolatlong_examples.csv'))
            self.assertEqual(len(uncertain.index), 0)
            uncertain = occ_df[(occ_df['decimalLongitude'] == occ_df['decimalLatitude'])]
            uncertain.to_csv(os.path.join(test_output_dir, 'bad_eqlatlong_examples.csv'))
            self.assertEqual(len(uncertain.index), 0)
            # na lat long
            uncertain = occ_df[(occ_df['decimalLongitude'].isna()) | (occ_df['decimalLatitude'].isna())]
            uncertain.to_csv(os.path.join(test_output_dir, tag + 'bad_nalatlong_examples.csv'))
            self.assertEqual(len(uncertain.index), 0)

            # na codes
            # uncertain = occ_df[(occ_df['countryCode'].isna())]
            # uncertain.to_csv(os.path.join(test_dir, tag+'bad_naccode_examples.csv'))

        test_examples(_final_cleaned_output_df, '')
        test_examples(_native_cleaned_output_df, 'native')

    def test_tdwg_regions_in_given_codes(self):
        # Test natives
        print('testing native tdwg3 codes')
        for idx, row in tqdm(_native_cleaned_output_df.iterrows(), total=_native_cleaned_output_df.shape[0],
                             desc="Searching 1", ascii=False, ncols=72):
            self.assertIn(row['tdwg3_region'], ast.literal_eval(row['native_tdwg3_codes']))

        print('testing native/introduced tdwg3 codes')
        for idx, row in tqdm(_final_cleaned_output_df.iterrows(), total=_final_cleaned_output_df.shape[0],
                             desc="Searching 2", ascii=False, ncols=72):
            native_intro_codes = ast.literal_eval(row['native_tdwg3_codes']) + ast.literal_eval(
                row['intro_tdwg3_codes'])
            self.assertIn(row['tdwg3_region'], native_intro_codes)

    def test_gbif_records_preserved(self):
        _standard_cleaned_csv = os.path.join(plant_occurences, 'outputs', 'standard_cleaned_occurrences.csv')
        standard_cleaned_records = pd.read_csv(_standard_cleaned_csv)

        columns_to_check = ['gbifID', 'decimalLongitude', 'decimalLatitude', 'fullname']

        def tidy_df_to_match(df):
            new_df = df[columns_to_check]
            new_df.drop_duplicates(subset=['gbifID'], keep='first', inplace=True)
            new_df.set_index('gbifID', inplace=True)
            new_df.sort_index(ascending=True, inplace=True)
            return new_df

        standard_cleaned_records_in_native = tidy_df_to_match(standard_cleaned_records[
                                                                  standard_cleaned_records['gbifID'].isin(
                                                                      _native_cleaned_output_df['gbifID'].values)][
                                                                  columns_to_check])
        natives_with_basic_columns = tidy_df_to_match(_native_cleaned_output_df)

        print('testing:')
        print(standard_cleaned_records_in_native)
        print(natives_with_basic_columns)

        pd.testing.assert_frame_equal(standard_cleaned_records_in_native, natives_with_basic_columns)

        standard_cleaned_records_in_final = tidy_df_to_match(standard_cleaned_records[
                                                                 standard_cleaned_records['gbifID'].isin(
                                                                     _final_cleaned_output_df['gbifID'].values)][
                                                                 columns_to_check])
        final_with_basic_columns = tidy_df_to_match(_final_cleaned_output_df)

        print('testing:')
        print(standard_cleaned_records_in_final)
        print(final_with_basic_columns)
        pd.testing.assert_frame_equal(standard_cleaned_records_in_final, final_with_basic_columns)

    def test_distributions_of_occs(self):
        dist_records = pd.read_csv(os.path.join(input_test_dir, 'occ_region_test.csv'))
        dist_records_with_tdwg = get_tdwg_regions_for_occurrences(dist_records)
        self.assertListEqual(dist_records_with_tdwg['known_region'].tolist(),
                             dist_records_with_tdwg['tdwg3_region'].tolist())

    def test_native_introduced_matching(self):
        dist_records = pd.read_csv(os.path.join(input_test_dir, 'occ_region_test.csv'))
        dist_records_wiht_acc_info = get_accepted_info_from_names_in_column(dist_records, 'fullname',
                                                                            families_of_interest=['Apocynaceae',
                                                                                                  'Rubiaceae'])
        dist_records_with_tdwg = get_tdwg_regions_for_occurrences(dist_records_wiht_acc_info)
        dist_records_with_native_intro_info = find_whether_occurrences_in_native_or_introduced_regions(
            dist_records_with_tdwg,
            distributions_csv)
        dist_records_with_native_intro_info.to_csv(os.path.join(test_output_dir, 'tested_known_distributions.csv'))
        self.assertListEqual(dist_records_with_native_intro_info['known_native'].tolist(),
                             dist_records_with_native_intro_info['within_native'].tolist())

        self.assertListEqual(dist_records_with_native_intro_info['known_introd'].tolist(),
                             dist_records_with_native_intro_info['within_introduced'].tolist())

    def test_more_with_introduced(self):
        self.assertGreaterEqual(_final_cleaned_output_df.shape[0], _native_cleaned_output_df.shape[0])

    def test_no_duplicates(self):

        duplicates = _final_cleaned_output_df.duplicated(subset=['gbifID'])
        self.assertEqual(len(duplicates), 0)
        duplicates = _native_cleaned_output_df.duplicated(subset=['gbifID'])
        self.assertEqual(len(duplicates), 0)


if __name__ == '__main__':
    unittest.main()
