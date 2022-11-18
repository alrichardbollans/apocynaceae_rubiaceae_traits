import unittest

import pandas as pd

# TODO: Add these to generic trait package?

class imported_and_encoded_data(unittest.TestCase):



    def activities(self, raw_file:str):
        trait_df = pd.read_csv(raw_file)
        self.assertEqual(len(trait_df[trait_df['Activity_Antimalarial'] == 'Weak'].index), 0)
