import unittest

import pandas as pd

from getting_malarial_regions import taxa_in_malarial_countries_csv
from wcsp_distributions import distributions_csv


class MyTestCase(unittest.TestCase):
    def test_output_instances(self):
        distros_df = pd.read_csv(distributions_csv, index_col=0)
        distros_df.set_index('kew_id', inplace=True)
        self.assertEqual("['ANG', 'NAM']", distros_df.at['76360-1', 'native_tdwg3_codes'], msg=f'76360-1')
        self.assertEqual("['SAM']", distros_df.at['77164465-1', 'native_tdwg3_codes'], msg=f'77164465-1')
        self.assertEqual("['CHC', 'CHT']", distros_df.at['756598-1', 'native_tdwg3_codes'], msg=f'756598-1')

    def test_malarial_instances(self):
        malarial_taxa = pd.read_csv(taxa_in_malarial_countries_csv)
        malarial_taxa_acc_ids = malarial_taxa['Accepted_ID'].to_list()
        print(malarial_taxa_acc_ids)
        non_malarial_ids = ['77197401-1', '21200-2', '77167599-1', '102673-1']

        for id in non_malarial_ids:
            self.assertNotIn(id,malarial_taxa_acc_ids)


if __name__ == '__main__':
    unittest.main()
