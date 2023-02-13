import os
from typing import List

import pandas as pd
from pkg_resources import resource_filename

from large_file_storage import data_download

_inputs_path = resource_filename(__name__, 'inputs')

_temp_outputs_path = resource_filename(__name__, 'temp_outputs')

_output_path = resource_filename(__name__, 'outputs')
malaria_country_codes_csv = os.path.join(_output_path, 'malarial_country_codes.csv')
if not os.path.isdir(_inputs_path):
    os.mkdir(_inputs_path)
if not os.path.isdir(_temp_outputs_path):
    os.mkdir(_temp_outputs_path)
if not os.path.isdir(_output_path):
    os.mkdir(_output_path)

# Without a decent parser, the list output from world bank data is parsed manually using TDWG_geo2.pdf
world_bank_parsed_code_dict = {'Afghanistan': ['AFG'], 'Algeria': ['ALG'], 'Angola': ['ANG'],
                               'Argentina': ['AGE', 'AGS', 'AGW'],
                               'Armenia': ['TCS'],
                               'Azerbaijan': ['TCS'], 'Bangladesh': ['BAN'], 'Belize': ['BLZ'],
                               'Benin': ['BEN'],
                               'Bhutan': ['EHM'],
                               'Bolivia': ['BOL'], 'Botswana': ['BOT'],
                               'Brazil': ['BZC', 'BZE', 'BZL', 'BZN', 'BZS'],
                               'Burkina Faso': ['BKN'], 'Burundi': ['BUR'],
                               'Cabo Verde': ['CVI'], 'Cambodia': ['CBD'], 'Cameroon': ['CMN'],
                               'Central African Republic': ['CAF'],
                               'Chad': ['CHA'],
                               'China': ['CHC', 'CHN', 'CHS', 'CHH', 'CHI', 'CHM', 'CHQ', 'CHT', 'CHX'],
                               'Colombia': ['CLM'],
                               'Comoros': ['COM'], 'Congo, Dem. Rep.': ['CON'],
                               'Congo, Rep.': ['CON'],
                               'Costa Rica': ['COS'], "Cote d'Ivoire": ['IVO'], 'Djibouti': ['DJI'],
                               'Dominican Republic': ['DOM'],
                               'Ecuador': ['ECU'], 'Egypt, Arab Rep.': ['EGY'], 'El Salvador': ['ELS'],
                               'Equatorial Guinea': ['EQG'],
                               'Eritrea': ['ERI'], 'Eswatini': ['SWZ'], 'Ethiopia': ['ETH'], 'Gabon': ['GAB'],
                               'Gambia, The': ['GAM'],
                               'Georgia': ['TCS'], 'Ghana': ['GHA'], 'Guatemala': ['GUA'], 'Guinea': ['GUI'],
                               'Guinea-Bissau': ['GNB'],
                               'Guyana': ['GUY'], 'Haiti': ['HAI'], 'Honduras': ['HON'], 'India': ['IND'],
                               'Indonesia': ['NWG', 'JAW', 'BOR', 'LSI', 'MOL', 'SUL', 'SUM'],
                               'Iran, Islamic Rep.': ['IRN'], 'Iraq': ['IRQ'], 'Kenya': ['KEN'],
                               "Korea, Dem. People's Rep.": ['KOR'],
                               'Korea, Rep.': ['KOR'], 'Kyrgyz Republic': ['KGZ'], 'Lao PDR': ['LAO'],
                               'Liberia': ['LBR'],
                               'Madagascar': ['MDG'],
                               'Malawi': ['MLW'], 'Malaysia': ['MLY'], 'Mali': ['MLI'], 'Mauritania': ['MTN'],
                               'Mexico': ['MXC', 'MXE', 'MXG', 'MXI', 'MXN', 'MXS', 'MXT'],
                               'Morocco': ['MOR'],
                               'Mozambique': ['MOZ'], 'Myanmar': ['MYA'], 'Namibia': ['NAM'],
                               'Nepal': ['NEP'],
                               'Nicaragua': ['NIC'],
                               'Niger': ['NGR'],
                               'Nigeria': ['NGA'], 'Oman': ['OMA'], 'Pakistan': ['PAK'], 'Panama': ['PAN'],
                               'Papua New Guinea': ['NWG'],
                               'Paraguay': ['PAR'], 'Peru': ['PER'], 'Philippines': ['PHI'],
                               'Rwanda': ['RWA'],
                               'Sao Tome and Principe': ['GGI'],
                               'Saudi Arabia': ['SAU'], 'Senegal': ['SEN'], 'Sierra Leone': ['SIE'],
                               'Solomon Islands': ['SOL'],
                               'Somalia': ['SOM'],
                               'South Africa': ['CPP', 'OFS', 'NAT', 'TVL'], 'South Sudan': ['SUD'],
                               'Sri Lanka': ['SRL'],
                               'Sudan': ['SUD'],
                               'Suriname': ['SUR'],
                               'Syrian Arab Republic': ['LBS'], 'Tajikistan': ['TZK'], 'Tanzania': ['TAN'],
                               'Thailand': ['THA'],
                               'Timor-Leste': ['LSI'], 'Togo': ['TOG'], 'Turkey': ['TUR'],
                               'Turkmenistan': ['TKM'],
                               'Uganda': ['UGA'],
                               'Uzbekistan': ['UZB'], 'Vanuatu': ['VAN'], 'Venezuela, RB': ['VEN'],
                               'Vietnam': ['VIE'],
                               'Yemen, Rep.': ['YEM'],
                               'Zambia': ['ZAM'], 'Zimbabwe': ['ZIM'], 'Kazakhstan': ['KAZ'],
                               'United Arab Emirates': ['GST']}


# From https://datacatalog.worldbank.org/search/dataset/0037712
# Accessed 03/05/2022
# Any country with any incidence of malaria between 1960 and 2021
# the indicator is estimated only where malaria transmission occurs
def print_world_bank_countries():
    wdid = pd.read_csv(os.path.join(data_download, 'WDI_csv/WDIData.csv'))
    malaria_data = wdid[wdid['Indicator Name'] == 'Incidence of malaria (per 1,000 population at risk)']

    years = range(1960, 2021)

    countries_with_malaria = {}

    for y in years:
        countries_in_year = malaria_data[~malaria_data[str(y)].isna()]
        for c in countries_in_year['Country Name']:
            if c not in countries_with_malaria.keys():
                code = countries_in_year[countries_in_year['Country Name'] == c]['Country Code'].values[0]
                countries_with_malaria[c] = code

    print(countries_with_malaria)
    print(countries_with_malaria.keys())
    # retranslations = parsed_names_from_world_bank()
    # return list(countries_with_malaria.values())


def get_world_bank_tdwg_codes():
    parsed_codes = []
    for k in world_bank_parsed_code_dict.keys():
        for v in world_bank_parsed_code_dict[k]:
            parsed_codes.append(v)

    return parsed_codes


def get_WHO_codes():
    who_df = pd.read_csv(os.path.join(_inputs_path, 'f8SXcv4V.csv'))
    malarial_regions = who_df[who_df['FactValueNumeric'] > 0]
    malarial_regions.drop_duplicates(subset=['Location'], inplace=True)

    name_code_parser = world_bank_parsed_code_dict.copy()
    additional_codes = {'Bolivia (Plurinational State of)': ['BOL'],
                        'Viet Nam': ['VIE'],
                        'Yemen': ['YEM'],
                        "Democratic People's Republic of Korea": ['KOR'],
                        'Venezuela (Bolivarian Republic of)': ['VEN'],
                        'Democratic Republic of the Congo': ['CON'],
                        "Lao People's Democratic Republic": ['LAO'],
                        "Republic of Korea": ['KOR'],
                        'Côte d’Ivoire': ['IVO'],
                        'United Republic of Tanzania': ['TAN'],
                        'Gambia': ['GAM'],
                        'Congo': ['CON'],
                        'Iran (Islamic Republic of)': ['IRN'],
                        'Kyrgyzstan': ['KGZ']
                        }
    name_code_parser.update(additional_codes)
    region_codes = []

    for location in malarial_regions['Location'].tolist():
        for v in name_code_parser[location]:
            region_codes.append(v)

    return region_codes


def get_tdwg3_codes():
    world_bank_codes = get_world_bank_tdwg_codes()

    who_codes = get_WHO_codes()

    print('Getting iso3 codes')
    # Caprivi strip is in namibia
    # Assam is part of india
    manual_additions = ['CPV', 'ASS']
    # Australia: https://doi.org/10.5694/j.1326-5377.1996.tb122051.x (Malaria transmission and climate change in Australia)
    # Réunion: https://europepmc.org/article/med/8784548 (Control of malaria re-emergence in Reunion)
    # Libya: https://doi.org/10.1016/B978-0-12-394303-3.00010-4 (The Changing Limits and Incidence of Malaria in Africa)
    # Tunisia: https://doi.org/10.1016/B978-0-12-394303-3.00010-4 (The Changing Limits and Incidence of Malaria in Africa)
    # Uruguay: https://doi.org/10.1093/ae/46.4.238 (Malaria Vector Heterogeneity in South America)
    # Trinidad (and Tobago): Dave D Chadee, Ashton LeMaitre, and Clive C Tilluckdharry, “An Epidemic Outbreak of Plasmodium Vivax Malaria in Trinidad-Abstract,” West Indian Med. j, 1993, 45–46.
    codes_from_literature = ['NTA', 'WAU', 'QLD', 'REU', 'LBY', 'TUN', 'TRT']
    # From https://www.cdc.gov/malaria/about/distribution.html
    # ['Western Sahara', 'Kiribati', 'French Guiana'] Zaire, Cabinda
    # Accessed: 12/05/2022
    codes_from_CDC = ['WSA', 'LIN', 'FRG', 'ZAI', 'CAB']

    iso_3_codes = who_codes + manual_additions + codes_from_literature + world_bank_codes + codes_from_CDC
    iso_3_codes = sorted(iso_3_codes)
    code_df = pd.DataFrame({'tdwg3_codes': iso_3_codes})
    code_df.drop_duplicates(subset=['tdwg3_codes'], inplace=True)
    code_df.reset_index(inplace=True, drop=True)
    code_df.to_csv(malaria_country_codes_csv)

    return iso_3_codes
