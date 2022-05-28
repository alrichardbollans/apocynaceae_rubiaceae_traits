import pandas as pd
from taxa_lists import get_all_taxa

from cleaning_plant_occurrences import final_occurrence_output_csv
from climate_vars import summary_output_csv


def summarise_occurrences():
    families = ['Apocynaceae', 'Rubiaceae']
    acc_taxa = get_all_taxa(families_of_interest=families, accepted=True,
                            ranks=['Species', 'Subspecies', 'Variety'])
    occ_df = pd.read_csv(final_occurrence_output_csv)

    unique_taxa = occ_df['Accepted_Name'].unique()
    unique_taxa_in_fams = [x for x in unique_taxa if x in acc_taxa['accepted_name'].values]

    out_dict = {'Total Occurrences': [len(occ_df.index)], 'Total Taxa': [len(acc_taxa.index)],
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
    summarise_occurrences()


if __name__ == '__main__':
    main()
