import unittest

import pandas as pd

# TODO: Add these to generic trait package?

class imported_and_encoded_data(unittest.TestCase):
    def type_of_test(self, csv_file:str):
        trait_df = pd.read_csv(csv_file)
        trait_df = trait_df[~trait_df['Activity_Antimalarial'].isna()]

        vitro_names = ['Vitro', 'Vivo,Vitro', 'Vitro,Vivo']
        vitro_df = trait_df[trait_df['Type_of_Test'].isin(vitro_names)]

        vivo_names = ['Vivo', 'Vivo,Vitro', 'Vitro,Vivo']
        vivo_df = trait_df[trait_df['Type_of_Test'].isin(vivo_names)]

        neither_df = trait_df[trait_df['Type_of_Test'].isna()]

        neither_df =neither_df[neither_df['Genus'] != 'Cinchona']
        ## Assert that all labelled samples have a type of test
        self.assertEqual(len(neither_df.index), 0, msg=neither_df['Accepted_Name'])

        mice_df = trait_df[trait_df['Given_Activities'].str.contains('mice')]
        vitro_mice = mice_df[mice_df['Type_of_Test'].isin(vivo_names)]

        # If 'mice' in activties, probably should be vivo

        self.assertEqual(len(vitro_mice.index), 0, msg=vitro_mice['Accepted_Name'])


    def activities(self, raw_file:str):
        trait_df = pd.read_csv(raw_file)
        self.assertEqual(len(trait_df[trait_df['Activity_Antimalarial'] == 'Weak'].index), 0)
