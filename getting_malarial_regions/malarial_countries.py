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


# From https://datacatalog.worldbank.org/search/dataset/0037712
# Accessed 03/05/2022
# Any country with any incidence of malaria between 1960 and 2021
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
    # Without a decent parser, the list output from world bank data is parsed manually here
    # using TDWG_geo2.pdf
    parsed_code_dict = {'Afghanistan': ['AFG'], 'Algeria': ['ALG'], 'Angola': ['ANG'],
                        'Argentina': ['AGE', 'AGS', 'AGW'],
                        'Armenia': ['TCS'],
                        'Azerbaijan': ['TCS'], 'Bangladesh': ['BAN'], 'Belize': ['BLZ'], 'Benin': ['BEN'],
                        'Bhutan': ['EHM'],
                        'Bolivia': ['BOL'], 'Botswana': ['BOT'], 'Brazil': ['BZC', 'BZE', 'BZL', 'BZN', 'BZS'],
                        'Burkina Faso': ['BKN'], 'Burundi': ['BUR'],
                        'Cabo Verde': ['CVI'], 'Cambodia': ['CBD'], 'Cameroon': ['CMN'],
                        'Central African Republic': ['CAF'],
                        'Chad': ['CHA'],
                        'China': ['CHC', 'CHN', 'CHS', 'CHH', 'CHI', 'CHM', 'CHQ', 'CHT', 'CHX'], 'Colombia': ['CLM'],
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
                        'Korea, Rep.': ['KOR'], 'Kyrgyz Republic': ['KGZ'], 'Lao PDR': ['LAO'], 'Liberia': ['LBR'],
                        'Madagascar': ['MDG'],
                        'Malawi': ['MLW'], 'Malaysia': ['MLY'], 'Mali': ['MLI'], 'Mauritania': ['MTN'],
                        'Mexico': ['MXC', 'MXE', 'MXG', 'MXI', 'MXN', 'MXS', 'MXT'],
                        'Morocco': ['MOR'],
                        'Mozambique': ['MOZ'], 'Myanmar': ['MYA'], 'Namibia': ['NAM'], 'Nepal': ['NEP'],
                        'Nicaragua': ['NIC'],
                        'Niger': ['NGR'],
                        'Nigeria': ['NGA'], 'Oman': ['OMA'], 'Pakistan': ['PAK'], 'Panama': ['PAN'],
                        'Papua New Guinea': ['NWG'],
                        'Paraguay': ['PAR'], 'Peru': ['PER'], 'Philippines': ['PHI'], 'Rwanda': ['RWA'],
                        'Sao Tome and Principe': ['GGI'],
                        'Saudi Arabia': ['SAU'], 'Senegal': ['SEN'], 'Sierra Leone': ['SIE'],
                        'Solomon Islands': ['SOL'],
                        'Somalia': ['SOM'],
                        'South Africa': ['CPP', 'OFS', 'NAT', 'TVL'], 'South Sudan': ['SUD'], 'Sri Lanka': ['SRL'],
                        'Sudan': ['SUD'],
                        'Suriname': ['SUR'],
                        'Syrian Arab Republic': ['LBS'], 'Tajikistan': ['TZK'], 'Tanzania': ['TAN'],
                        'Thailand': ['THA'],
                        'Timor-Leste': ['LSI'], 'Togo': ['TOG'], 'Turkey': ['TUR'], 'Turkmenistan': ['TKM'],
                        'Uganda': ['UGA'],
                        'Uzbekistan': ['UZB'], 'Vanuatu': ['VAN'], 'Venezuela, RB': ['VEN'], 'Vietnam': ['VIE'],
                        'Yemen, Rep.': ['YEM'],
                        'Zambia': ['ZAM'], 'Zimbabwe': ['ZIM'], 'Kazakhstan': ['KAZ'], 'United Arab Emirates': ['GST']}

    parsed_codes = []
    for k in parsed_code_dict.keys():
        for v in parsed_code_dict[k]:
            parsed_codes.append(v)

    return parsed_codes


def plot_countries(tdwg3_region_codes: List[str], title: str, output_path: str):
    import matplotlib.pyplot as plt
    import cartopy.crs as ccrs
    import cartopy.feature as cfeature
    import cartopy.io.shapereader as shpreader

    tdwg3_shp = shpreader.Reader(
        os.path.join(_inputs_path, 'wgsrpd-master', 'level3', 'level3.shp'))

    print('plotting countries')

    plt.figure(figsize=(40, 25))
    plt.xlim(-210, 210)
    plt.ylim(-70, 90)
    plt.xticks(fontsize=30)
    plt.yticks(fontsize=30)
    plt.title(title, fontsize=40)
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.coastlines(resolution='10m')
    ax.add_feature(cfeature.BORDERS, linewidth=5)
    for country in tdwg3_shp.records():
        tdwg_code = country.attributes['LEVEL3_COD']
        if tdwg_code in tdwg3_region_codes:

            # print(country.attributes['name_long'], next(earth_colors))
            ax.add_geometries([country.geometry], ccrs.PlateCarree(),
                              facecolor='orange',
                              label=tdwg_code)

            x = country.geometry.centroid.x
            y = country.geometry.centroid.y

            ax.text(x, y, tdwg_code, color='black', size=10, ha='center', va='center',
                    transform=ccrs.PlateCarree())
        else:
            # print(f"code not in given malarial isocodes: {tdwg_code}")
            ax.add_geometries([country.geometry], ccrs.PlateCarree(),
                              facecolor='white',
                              label=tdwg_code)

    all_map_isos = [country.attributes['LEVEL3_COD'] for country in tdwg3_shp.records()]
    missed_names = [x for x in tdwg3_region_codes if x not in all_map_isos]
    print(f'iso codes not plotted on map: {missed_names}')
    # plt.show()
    plt.tight_layout()
    # change the fontsize

    plt.savefig(output_path, dpi=50)


def get_tdwg3_codes():
    world_bank_codes = get_world_bank_tdwg_codes()
    print('Getting iso3 codes')
    # Caprivi strip is in namibia
    # Assam is part of india
    manual_additions = ['CPV', 'ASS']
    # Australia: https://doi.org/10.5694/j.1326-5377.1996.tb122051.x (Malaria transmission and climate change in Australia)
    # Réunion: https://europepmc.org/article/med/8784548 (Control of malaria re-emergence in Reunion)
    # Libya: https://doi.org/10.1016/B978-0-12-394303-3.00010-4 (The Changing Limits and Incidence of Malaria in Africa)
    # Tunisia: https://doi.org/10.1016/B978-0-12-394303-3.00010-4 (The Changing Limits and Incidence of Malaria in Africa)
    # Uruguay: https://doi.org/10.1093/ae/46.4.238 (Malaria Vector Heterogeneity in South America)
    codes_from_literature = ['NTA', 'WAU', 'QLD', 'REU', 'LBY', 'TUN']
    # From https://www.cdc.gov/malaria/about/distribution.html
    # ['Western Sahara', 'Kiribati', 'French Guiana'] Zaire, Cabinda
    # Accessed: 12/05/2022
    codes_from_CDC = ['WSA', 'LIN', 'FRG', 'ZAI', 'CAB']

    iso_3_codes = manual_additions + codes_from_literature + world_bank_codes + codes_from_CDC

    code_df = pd.DataFrame({'tdwg3_codes': iso_3_codes})
    code_df.to_csv(malaria_country_codes_csv)

    return iso_3_codes


if __name__ == '__main__':
    # print_world_bank_countries()
    codes = get_tdwg3_codes()
    plot_countries(codes, 'Historical Malarial Regions', os.path.join(_output_path, 'malarial_countries.png'))
