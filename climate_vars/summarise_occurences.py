import os.path

import pandas as pd
from taxa_lists import get_all_taxa

from climate_vars import summary_output_csv, climate_output_path, occurrences_with_clim_and_accepted_names_csv


def summarise():
    # TODO: se
    families = ['Apocynaceae', 'Rubiaceae']
    acc_taxa = get_all_taxa(families_of_interest=families, accepted=True,
                            ranks=['Species', 'Subspecies', 'Variety'])
    clean_occ_df = pd.read_csv(occurrences_with_clim_and_accepted_names_csv)

    clean_occ_df.describe().to_csv(os.path.join(climate_output_path, 'data_summary.csv'))
    unique_taxa = clean_occ_df['Accepted_Name'].unique()
    unique_taxa_in_fams = [x for x in unique_taxa if x in acc_taxa['accepted_name'].values]

    out_dict = {'Total Occurrences': [len(clean_occ_df.index)], 'Total Taxa': [len(acc_taxa.index)],
                'Found Taxa': [len(unique_taxa_in_fams)],
                'Percent': [float(len(unique_taxa_in_fams)) / len(acc_taxa.index)]}
    out_df = pd.DataFrame(out_dict)
    out_df.to_csv(summary_output_csv)


def plot_sp_map():
    # Note package issue: https://github.com/gbif/pygbif/issues/86
    from pygbif import maps
    out = maps.map(taxonKey=1)
    print(out.response)
    print(out.path)
    print(out.img)
    out.plot()


def main():
    summarise()


if __name__ == '__main__':
    main()
