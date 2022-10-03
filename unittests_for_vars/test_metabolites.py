import unittest

import pandas as pd
from automatchnames import COL_NAMES
from tqdm import tqdm

from metabolite_vars import accepted_metabolites_output_csv, \
    unaccepted_metabolites_output_csv, rubiaceae_apocynaceae_metabolites_output_csv


class MyTestCase(unittest.TestCase):

    def test_meta_hits(self):
        import numpy as np
        accepted_df = pd.read_csv(accepted_metabolites_output_csv, index_col=0)
        unaccepted_df = pd.read_csv(unaccepted_metabolites_output_csv, index_col=0)
        cat_temp_outputs = pd.concat([accepted_df, unaccepted_df])
        final_output_df = pd.read_csv(rubiaceae_apocynaceae_metabolites_output_csv, index_col=0)

        # Check final_output_df has unqiue accepted names
        self.assertEqual(len(final_output_df[final_output_df.duplicated(subset=['Accepted_Name'], keep=False)]), 0)

        # check final_output_df has all accepted names
        for x in set(accepted_df['Accepted_Name'].tolist()):
            if str(x) not in ['nan']:
                self.assertIn(x, final_output_df['Accepted_Name'].values)

        for x in set(final_output_df['Accepted_Name'].tolist()):
            if str(x) not in ['nan']:
                self.assertIn(x, accepted_df['Accepted_Name'].values)

        # Check columns
        for c in accepted_df.columns:
            self.assertIn(c, final_output_df.columns)
            self.assertIn(c, cat_temp_outputs.columns)
        for c in unaccepted_df.columns:
            self.assertTrue(c in final_output_df.columns or c.lower() in [x.lower() for x in final_output_df.columns],
                            msg=c)
            self.assertTrue(c in cat_temp_outputs.columns or c.lower() in [x.lower() for x in cat_temp_outputs.columns],
                            msg=c)

        # Bad cases: when taxa has 1 in one of the data frames and 0 in final_output
        for i in tqdm(range(len(cat_temp_outputs.columns)), desc="testing", ascii=False, ncols=72):
            c = cat_temp_outputs.columns[i]
            if c not in ['taxa'] + list(COL_NAMES.values()):
                should_be_one = cat_temp_outputs[cat_temp_outputs[c] == 1]
                # Just get accepted names in the accepted_Df as some synonyms are resolved outside the family.
                should_be_one = should_be_one[should_be_one['Accepted_Name'].isin(accepted_df['Accepted_Name'].values)]

                is_one = final_output_df[final_output_df[c] == 1]

                self.assertEqual(sorted(should_be_one['Accepted_Name'].unique().tolist()),
                                 sorted(is_one['Accepted_Name'].tolist()))
        # # If in either, then in both.
        # for i in tqdm(range(len(accepted_df['Accepted_Name'].tolist())), desc="testing", ascii=False, ncols=72):
        #     acc_name = accepted_df['Accepted_Name'].tolist()[i]
        #     all_df = cat_temp_outputs[cat_temp_outputs['Accepted_Name'] == acc_name]
        #     for c in all_df.columns:
        #         if c not in ['taxa'] + list(COL_NAMES.values()):
        #             x = all_df[c].max()
        #             if c not in final_output_df.columns:
        #                 # rename c
        #                 c = [x for x in final_output_df.columns if x.lower() == c.lower()][0]
        #             fin_val_df = final_output_df[final_output_df['Accepted_Name'] == acc_name]
        #             final_value = fin_val_df.iloc[0][c]
        #             # print(str.join(':', [acc_name, c]))
        #             # print(f'x:{x}, final_val: {final_value}')
        #             if np.isnan(x):
        #                 self.assertEqual(final_value, 0, msg=str.join(':', [acc_name, c]))
        #             else:
        #                 self.assertEqual(final_value, x, msg=str.join(':', [acc_name, c]))


if __name__ == '__main__':
    unittest.main()
