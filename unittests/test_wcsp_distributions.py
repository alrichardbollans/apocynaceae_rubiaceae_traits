import unittest

import pandas as pd

from metabolite_vars import rub_apoc_alkaloid_hits_output_csv
from unittests import confirming_hits
from wcsp_distributions import distributions_csv


class MyTestCase(unittest.TestCase):
    def test_output_instances(self):

        distros_df = pd.read_csv(distributions_csv, index_col=0)
        distros_df.set_index('kew_id', inplace=True)
        self.assertEqual("['ANG', 'NAM']", distros_df.at['76360-1', 'tdwg3_codes'], msg=f'76360-1')
        self.assertEqual("['SAM']", distros_df.at['77164465-1', 'tdwg3_codes'], msg=f'77164465-1')
        self.assertEqual("['CHC', 'CHT']", distros_df.at['756598-1', 'tdwg3_codes'], msg=f'756598-1')

if __name__ == '__main__':
    unittest.main()
