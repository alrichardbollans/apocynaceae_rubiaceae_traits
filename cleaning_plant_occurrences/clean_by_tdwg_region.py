import os

import pandas as pd
# Add progress bar to apply method
from clean_plant_occurrences import read_occurences_and_output_acc_names, clean_occurrences_by_tdwg_regions

from large_file_storage import plant_occurences
from wcsp_distributions import distributions_csv

_standard_cleaned_csv = os.path.join(plant_occurences, 'outputs', 'standard_cleaned_occurrences.csv')

accepted_name_info_of_occurrences_csv = os.path.join(plant_occurences, 'outputs',
                                                     'standard_cleaned_occurences_with_accepted_names.csv')

final_occurrence_output_csv = os.path.join(plant_occurences, 'outputs', 'final_cleaned_occurrences.csv')
_final_native_occurrence_output_csv = os.path.join(plant_occurences, 'outputs', 'final_native_cleaned_occurrences.csv')

families_in_occurrences = ['Apocynaceae', 'Rubiaceae', 'Celastraceae']
def read_my_occs():

    standard_occ_df = pd.read_csv(_standard_cleaned_csv)
    read_occurences_and_output_acc_names(standard_occ_df, accepted_name_info_of_occurrences_csv,
                                         families_in_occurrences=families_in_occurrences)


def clean_my_occs():
    acc_occ_df = pd.read_csv(accepted_name_info_of_occurrences_csv)
    print(f'given # of occurrences: {len(acc_occ_df.index)}')
    both = clean_occurrences_by_tdwg_regions(acc_occ_df, distributions_csv, priority='both',
                                             output_csv=final_occurrence_output_csv)
    print(f'# of native/introduced occurrences: {len(both.index)}')

    native = clean_occurrences_by_tdwg_regions(acc_occ_df, distributions_csv, priority='native',
                                               output_csv=_final_native_occurrence_output_csv)
    print(f'# of native occurrences: {len(native.index)}')


if __name__ == '__main__':
    # read_my_occs()
    clean_my_occs()
