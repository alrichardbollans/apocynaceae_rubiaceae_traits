import os
import unittest

import numpy as np
import pandas as pd
from automatchnames import get_genus_from_full_name

from manually_collected_data import clean_activities, ordinal_encode, encoded_traits_csv, \
    ORDER_STANDARDISED_CSV, parsed_alkaloid_classes_csv, convert_alks_in_cols_to_lists, trait_parsing_output_path
from unittests_for_vars import imported_and_encoded_data


class Test(unittest.TestCase):

    def test_data(self):
        t = imported_and_encoded_data()

        t.activities(ORDER_STANDARDISED_CSV)

        # Test all has family
        trait_df = pd.read_csv(encoded_traits_csv)

        self.assertEqual(trait_df['Family'].unique().tolist(), ['Apocynaceae', 'Rubiaceae'])
        genus_df = trait_df[trait_df['Accepted_Rank'] == 'Genus']
        self.assertEqual(len(genus_df), 1, msg=genus_df)

        t.type_of_test(encoded_traits_csv)

    def test_genera_from_acc_names(self):
        self.assertEqual(get_genus_from_full_name('Danais'), 'Danais')
        self.assertEqual(get_genus_from_full_name('Danais spp.'), 'Danais')
        self.assertEqual(get_genus_from_full_name('Danais xanthorrhoea'), 'Danais')

    def test_encodings(self):
        self.assertEqual(clean_activities('Active1 '), 'Active')
        self.assertIsInstance(clean_activities(' Weak'), str)
        self.assertIsInstance(clean_activities(np.NAN), type(np.NAN))

        self.assertEqual(ordinal_encode('Active1 '), 1)
        self.assertIsInstance(ordinal_encode(' Weak'), int)
        self.assertIsInstance(ordinal_encode(np.NAN), type(np.NAN))

        # self.assertEqual(clean_alkaloids('Dragendorff1 '), 1)
        # self.assertEqual(clean_alkaloids('Dragendorff1 Not Detected'), 0)
        # self.assertIsInstance(clean_alkaloids(np.NAN), type(np.NAN))
        # self.assertIsInstance(clean_alkaloids('urn:lsid:ipni.org:names:30479151-2'), type(np.NAN))

    def test_alkaloid_class_output(self):
        alk_class_df = pd.read_csv(parsed_alkaloid_classes_csv)

        # test some instances
        # zero pyrrolizidine
        zero_pyrrolizidines = alk_class_df[alk_class_df['alk_pyrrolizidine'] == 0]
        self.assertIn('Rondeletia panamensis', zero_pyrrolizidines['Accepted_Name'].values)
        self.assertIn('Aganosma cymosa', zero_pyrrolizidines['Accepted_Name'].values)

        # MIA <-> indole monoterpenoid This isn't strictly true as the monoterpene and indole may be separate alkaloids
        mia_df = alk_class_df[alk_class_df['alk_mia'] == 1]
        indmono_df = alk_class_df[(alk_class_df['alk_indole'] == 1) & (alk_class_df['alk_monoterpene'] == 1)]

        diff1 = mia_df[~mia_df['Accepted_Name'].isin(indmono_df['Accepted_Name'])]
        diff2 = indmono_df[~indmono_df['Accepted_Name'].isin(mia_df['Accepted_Name'])]

        self.assertEqual(len(diff1.index), 0, msg=diff1)
        self.assertEqual(len(diff2.index), 0, msg=diff2)

        # Update this
        alk_class_list = ['diterpenoid', 'imidazole', 'indole', 'indolizidine', 'isoquinoline', 'mia', 'misc. one n',
                          'misc. two n', 'monoterpene', 'peptide', 'piperidine', 'purine',
                          'pyrazine', 'pyridine', 'pyrrole', 'pyrrolidine', 'pyrrolizidine', 'quinoline',
                          'quinolizidine', 'simple amine', 'spermidine', 'steroidal']

        for c in alk_class_df.columns.tolist():
            if 'alk_' in c:
                out = c[c.rindex('alk_') + len('alk_'):]
                self.assertIn(out, alk_class_list)

    def test_alk_class_input(self):
        trait_df = pd.read_csv(encoded_traits_csv, index_col=0)
        _conal_alk_class_columns = ['Alkaloid_mainclass(conal)', 'Alkaloid_otherclasses']
        _alk_class_column = 'Alkaloid_classes'

        problem1_df = trait_df[
            (~trait_df[_alk_class_column].isna()) & trait_df['Alkaloid_mainclass(conal)'].isna() & trait_df[
                'Alkaloid_otherclasses'].isna()]
        problem2_df = trait_df[(trait_df[_alk_class_column].isna()) & (
                ~trait_df['Alkaloid_mainclass(conal)'].isna() | ~trait_df['Alkaloid_otherclasses'].isna())]

        self.assertEqual(len(problem1_df.index), 0, msg=f'{problem1_df}')
        self.assertEqual(len(problem2_df.index), 0, msg=f'{problem2_df}')
        trait_df = trait_df.dropna(subset=_alk_class_column)
        trait_df[_alk_class_column] = trait_df[_alk_class_column].apply(convert_alks_in_cols_to_lists)

        def check_rows(row):
            for alk in row[_alk_class_column]:
                if alk not in ['monoterpene', 'indole']:
                    self.assertIn(alk, str(row['Alkaloid_mainclass(conal)']).lower() + str(
                        row['Alkaloid_otherclasses']).lower(), msg=row)

        trait_df.apply(check_rows, axis=1)

    def test_alkaloid_input(self):
        trait_df = pd.read_csv(encoded_traits_csv, index_col=0)
        # Test that yes' and nos have something in test notes

        trait_df_with_alk_values = trait_df[~trait_df['Alkaloids'].isna()]
        problem_df = trait_df_with_alk_values[trait_df_with_alk_values['Alkaloids_test_notes'].isna()]
        self.assertEqual(len(problem_df.index), 0,msg=problem_df)


if __name__ == '__main__':
    unittest.main()
