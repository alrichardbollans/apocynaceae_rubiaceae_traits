import os

from pkg_resources import resource_filename
from taxa_lists import get_all_taxa
from wcsp_distribution_search import search_powo_for_tdwg3_distributions, convert_pkl_to_df

_inputs_path = resource_filename(__name__, 'inputs')

_temp_outputs_path = resource_filename(__name__, 'temp_outputs')

_output_path = resource_filename(__name__, 'outputs')
distributions_pkl = os.path.join(_temp_outputs_path, 'distributions.pkl')
distributions_csv = os.path.join(_output_path, 'distributions.csv')
if not os.path.isdir(_inputs_path):
    os.mkdir(_inputs_path)
if not os.path.isdir(_temp_outputs_path):
    os.mkdir(_temp_outputs_path)
if not os.path.isdir(_output_path):
    os.mkdir(_output_path)


def main():
    acc_taxa = get_all_taxa(families_of_interest=['Apocynaceae', 'Rubiaceae', 'Celastraceae'], accepted=True,
                            ranks=['Species', 'Subspecies', 'Variety'])
    id_list = acc_taxa['kew_id'].to_list()
    search_powo_for_tdwg3_distributions(id_list, distributions_pkl)
    convert_pkl_to_df(distributions_pkl, distributions_csv)


if __name__ == '__main__':
    main()
