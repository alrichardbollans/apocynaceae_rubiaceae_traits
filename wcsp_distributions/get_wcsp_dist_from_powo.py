import os
import pickle
import time
from json import JSONDecodeError
from typing import List

import automatchnames
import pandas as pd
from automatchnames import get_accepted_info_from_ids_in_column
from pkg_resources import resource_filename
from pykew import powo_terms, powo, ipni
from pykew.ipni_terms import Name
from taxa_lists import get_all_taxa
from tqdm import tqdm

from climate_vars import families_in_occurrences

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


def search_powo_for_distributions(ipni_list: List[str]):
    # Note distributions aren't given for synonyms. This is fine except in cases where you use an id which is
    # no longer accepted
    # Also, this function does not return distributions of extinct taxa
    import pykew.powo as powo
    out = {}
    for i in tqdm(range(len(ipni_list)), desc="Searching POWO for dists…", ascii=False, ncols=72):

        time.sleep(1)
        ipni = ipni_list[i]
        lookup_str = 'urn:lsid:ipni.org:names:' + str(ipni)
        try:

            res = powo.lookup(lookup_str, include=['distribution'])
            dist_codes = []
            try:
                native_to = [d['tdwgCode'] for d in res['distribution']['natives']]
                dist_codes += native_to
            except KeyError:
                print(f'No native codes: {ipni}')

            finally:
                try:
                    introduced_to = [d['tdwgCode'] for d in res['distribution']['introduced']]
                    dist_codes += introduced_to
                except KeyError:

                    pass

                finally:
                    out[ipni] = dist_codes
                with open(distributions_pkl, 'wb') as f:
                    pickle.dump(out, f)
        except JSONDecodeError:
            print(f'json error: {ipni}')


def convert_pkl_to_df():
    with open(distributions_pkl, 'rb') as f:
        dist_dict = pickle.load(f)

    str_dict = {}
    for k in dist_dict.keys():
        str_dict[k] = str(dist_dict[k])
    value_dict = {'kew_id': list(str_dict.keys()), 'iso3_codes': list(str_dict.values())}
    out_df = pd.DataFrame(value_dict)
    acc_out_df = get_accepted_info_from_ids_in_column(out_df, 'kew_id', families_of_interest=families_in_occurrences)
    acc_out_df.to_csv(distributions_csv)


def main():
    acc_taxa = get_all_taxa(families_of_interest=families_in_occurrences, accepted=True,
                            ranks=['Species', 'Subspecies', 'Variety'])
    id_list = acc_taxa['kew_id'].to_list()
    search_powo_for_distributions(id_list)
    convert_pkl_to_df()


if __name__ == '__main__':
    main()
