import os

import pandas as pd
from conservation_priorities import get_threat_status_taxa_in_family

from pkg_resources import resource_filename

_temp_outputs_path = resource_filename(__name__, 'temp_outputs')
rub_apoc_threat_status_csv = os.path.join(_temp_outputs_path, 'rub_apoc_threat_status.csv')

_outputs_path = resource_filename(__name__, 'outputs')

rub_apoc_accepted_threat_status_csv = os.path.join(_outputs_path, 'rub_apoc_accepted_threat_status.csv')


def main():
    # TODO:Note There are quite a few synonyms of unplaced names
    # TODO:Note cases like Adenium boehmianum Schinz 	where same report gives threatend and not threatened
    fams = ['Apocynaceae', 'Rubiaceae']
    get_threat_status_taxa_in_family(fams, rub_apoc_threat_status_csv, rub_apoc_accepted_threat_status_csv,
                                     ranks=['Species'])


if __name__ == '__main__':
    main()
