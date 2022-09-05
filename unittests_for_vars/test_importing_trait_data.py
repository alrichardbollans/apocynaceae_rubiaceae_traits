import unittest

import numpy as np
from automatchnames import get_genus_from_full_name

from manually_collected_data import clean_activities, ordinal_encode, clean_alkaloids, encoded_traits_csv, \
    ORDER_STANDARDISED_CSV
from unittests_for_vars import imported_and_encoded_data


# TODO: To avoid repeating this for future families, create separate package for general family vars

class Test(unittest.TestCase):

    def test_data(self):
        t = imported_and_encoded_data()

        t.activities(ORDER_STANDARDISED_CSV)
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

        self.assertEqual(clean_alkaloids('Dragendorff1 '), 1)
        self.assertEqual(clean_alkaloids('Dragendorff1 Not Detected'), 0)
        self.assertIsInstance(clean_alkaloids(np.NAN), type(np.NAN))
        self.assertIsInstance(clean_alkaloids('urn:lsid:ipni.org:names:30479151-2'), type(np.NAN))


if __name__ == '__main__':
    unittest.main()
