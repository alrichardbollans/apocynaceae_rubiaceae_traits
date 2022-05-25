import os
import unittest

import pandas as pd
from pkg_resources import resource_filename

test_dir = resource_filename(__name__, 'test_outputs')
from climate_vars import clean_native_occurences_with_clim_vars_csv, clean_introd_occurences_with_clim_vars_csv


class MyTestCase(unittest.TestCase):
    def test_something(self):
        #
        native_occ_df = pd.read_csv(clean_native_occurences_with_clim_vars_csv)
        introd_occ_df = pd.read_csv(clean_introd_occurences_with_clim_vars_csv)

        def test_examples(occ_df:pd.DataFrame,tag:str):
            dups = occ_df[occ_df.duplicated(subset=['gbifID'])]
            self.assertEqual(len(dups.index),0)

            # Coord uncertainty 20000
            print('coord uncertainty clean')
            uncertain = occ_df[occ_df['coordinateUncertaintyInMeters'] > 20000]
            uncertain.to_csv(os.path.join(test_dir, tag+'bad_coord_examples.csv'))
            # clim_occ_df = clim_occ_df[clim_occ_df['coordinateUncertaintyInMeters'] <= 20000]

            self.assertEqual(len(uncertain.index), 0)

            ## Years
            uncertain = occ_df[occ_df['year'] < 1945]
            uncertain.to_csv(os.path.join(test_dir, tag+'bad_year_examples.csv'))
            self.assertEqual(len(uncertain.index), 0)
            ## 0 long and lat
            uncertain = occ_df[(occ_df['longitude'] == 0) & (occ_df['latitude'] == 0)]
            uncertain.to_csv(os.path.join(test_dir, tag+'bad_zerolatlong_examples.csv'))
            self.assertEqual(len(uncertain.index), 0)
            uncertain = occ_df[(occ_df['longitude'] == occ_df['latitude'])]
            uncertain.to_csv(os.path.join(test_dir, 'bad_eqlatlong_examples.csv'))
            self.assertEqual(len(uncertain.index), 0)
            # na lat long
            uncertain = occ_df[(occ_df['longitude'].isna()) | (occ_df['latitude'].isna())]
            uncertain.to_csv(os.path.join(test_dir, tag+'bad_nalatlong_examples.csv'))
            self.assertEqual(len(uncertain.index), 0)

            # na codes
            # uncertain = occ_df[(occ_df['countryCode'].isna())]
            # uncertain.to_csv(os.path.join(test_dir, tag+'bad_naccode_examples.csv'))

        test_examples(native_occ_df, 'native')
        test_examples(introd_occ_df,'intro')

    def test_native_introduced(self):
        native_occ_df = pd.read_csv(clean_native_occurences_with_clim_vars_csv)
        print(len(native_occ_df.index))
        introd_occ_df = pd.read_csv(clean_introd_occurences_with_clim_vars_csv)
        print(len(introd_occ_df.index))

        occ_df = pd.concat([native_occ_df, introd_occ_df])
        dups = occ_df[occ_df['gbifID'].duplicated(keep="first")]
        print(dups)
        dups.to_csv(os.path.join(test_dir, 'introduced_natives.csv'))
        print(len(dups['fullname'].unique()))
        print(dups['fullname'].unique())

        self.assertEqual(len(dups.index),0)


if __name__ == '__main__':
    unittest.main()
