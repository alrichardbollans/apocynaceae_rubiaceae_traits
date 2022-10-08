import os

import pandas as pd
from pkg_resources import resource_filename

import wikipedia_searches
### Inputs
from taxa_lists import get_all_taxa

### Outputs
_output_path = resource_filename(__name__, 'outputs')
output_wiki_csv = os.path.join(_output_path, 'list_plants_with_wiki_pages.csv')
output_wiki_views_csv = os.path.join(_output_path, 'taxa_wiki_views.csv')
more_checked_taxa_csv = os.path.join(_output_path, 'initially_missed_taxa.csv')


def main():
    data = get_all_taxa(families_of_interest=['Apocynaceae', 'Rubiaceae'], accepted=False,
                        ranks=["Species", "Subspecies", "Variety"])

    taxa = data["taxa"].unique()

    wikipedia_searches.make_wiki_hit_df(taxa, os.path.join(_output_path, output_wiki_csv),
                                        force_new_search=True)


if __name__ == '__main__':
    main()
