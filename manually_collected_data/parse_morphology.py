import os

import pandas as pd
from pkg_resources import resource_filename

from manually_collected_data import trait_parsing_output_path
from automatchnames import remove_whitespace_at_beginning_and_end, get_accepted_info_from_names_in_column

_inputs_path = resource_filename(__name__, 'inputs')
_manual_morph_data_csv = os.path.join(_inputs_path, 'manual_morphological_traits.csv')
_manual_habit_data_csv = os.path.join(_inputs_path, 'manual_habits.csv')

manual_morph_data_output = os.path.join(trait_parsing_output_path, 'manual_morph_data.csv')
manual_habit_data_output = os.path.join(trait_parsing_output_path, 'manual_habit_data.csv')


def prepare_habits():
    habits = pd.read_csv(_manual_habit_data_csv)
    acc_manual_data = get_accepted_info_from_names_in_column(habits, 'genus')

    acc_manual_data.to_csv(manual_habit_data_output)


def prepare_manually_collected_data():
    manual_data = pd.read_csv(_manual_morph_data_csv)
    manual_data.drop(columns='Comment', inplace=True)
    manual_data.rename(columns={'spines (present (y) or absent(x)': 'spines',
                                'latex (white, clear, red, orange, yellow)': 'latex',
                                'corolla overlap (left (l) or right(r))': 'corolla',
                                'predominant habit (shrub (sh), subshrub (subsh), liana (li), tree(tr), succ (sc), herb (hb)': 'habit'
                                }, inplace=True)

    manual_data.drop(columns='habit', inplace=True)
    manual_data['Manual_snippet'] = ''
    manual_data['spines'] = manual_data['spines'].apply(remove_whitespace_at_beginning_and_end)
    manual_data['latex'] = manual_data['latex'].apply(remove_whitespace_at_beginning_and_end)
    manual_data['corolla'] = manual_data['corolla'].apply(remove_whitespace_at_beginning_and_end)

    acc_manual_data = get_accepted_info_from_names_in_column(manual_data, 'Genera')

    acc_manual_data.to_csv(manual_morph_data_output)


def main():
    prepare_manually_collected_data()
    prepare_habits()


if __name__ == '__main__':
    main()
