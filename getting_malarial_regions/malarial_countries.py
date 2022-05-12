import os

import pandas as pd
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import cartopy.io.shapereader as shpreader
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
def get_world_bank_countries():
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
    retranslations = parsed_names_from_world_bank()
    return list(countries_with_malaria.keys()) + retranslations


def parsed_names_from_world_bank():
    """ Get names from world bank in format reconisged by cartopy"""
    missed_names = ["Cote d'Ivoire", 'Eswatini', "Korea, Dem. People's Rep."]
    retranslations = ["Côte d'Ivoire", "Dem. Rep. Korea", "Kingdom of eSwatini"]
    return retranslations


# From https://www.cdc.gov/malaria/about/distribution.html
# Accessed: 05/05/2022
def states_from_CDC():
    states = ['Western Sahara', 'Kiribati', 'Somaliland', 'French Guiana', 'Puntland']
    return states

def states_from_literature():
    # Australia: https://doi.org/10.5694/j.1326-5377.1996.tb122051.x
    # Réunion: https://europepmc.org/article/med/8784548
    return ['Australia', 'Réunion']

def plot_countries(malarial_countries):
    shapename = os.path.join(_inputs_path, "ne_10m_admin_0_map_units", "ne_10m_admin_0_map_units.shp")
    countries_shp = shpreader.Reader(shapename)
    plt.figure(figsize=(40, 25))
    plt.xlim(-210, 210)
    plt.ylim(-70, 90)
    plt.title('Historical Malarial Regions', fontsize=40)
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.coastlines(resolution='10m')
    ax.add_feature(cfeature.BORDERS, linewidth=5)
    for country in countries_shp.records():
        name_long = country.attributes['NAME_LONG']
        name_short = country.attributes['NAME_SORT']
        formal_name = country.attributes['FORMAL_EN']
        map_names = [name_long, name_short, formal_name]
        if any(name in malarial_countries for name in map_names):

            # print(country.attributes['name_long'], next(earth_colors))
            ax.add_geometries([country.geometry], ccrs.PlateCarree(),
                              facecolor='red',
                              label=name_long)

            x = country.geometry.centroid.x
            y = country.geometry.centroid.y

            ax.text(x, y, name_long, color='black', size=10, ha='center', va='center', transform=ccrs.PlateCarree())
        else:
            print(name_long)
            ax.add_geometries([country.geometry], ccrs.PlateCarree(),
                              facecolor='white',
                              label=name_long)

    all_map_names = [country.attributes['NAME_LONG'] for country in countries_shp.records()] + [
        country.attributes['FORMAL_EN'] for country in countries_shp.records()] + [
                        country.attributes['NAME_SORT'] for country in countries_shp.records()]
    missed_names = [x for x in malarial_countries if x not in all_map_names]
    print(missed_names)
    # plt.show()
    plt.savefig(os.path.join(_output_path, 'malarial_countries.png'), dpi=300)


def get_iso3_codes(malarial_countries):
    iso_3_codes = []
    shapename = os.path.join(_inputs_path, "ne_10m_admin_0_map_units", "ne_10m_admin_0_map_units.shp")
    countries_shp = shpreader.Reader(shapename)
    for country in countries_shp.records():
        name_long = country.attributes['NAME_LONG']
        name_short = country.attributes['NAME_SORT']
        formal_name = country.attributes['FORMAL_EN']
        map_names = [name_long, name_short, formal_name]
        if any(name in malarial_countries for name in map_names):

            if country.attributes['ISO_A3'] == '-99':
                print(map_names)
            else:
                iso_3_codes.append(country.attributes['ISO_A3'])

    # These codes aren't assigned from the shapefiles
    # Somalia units are contained by SOM
    manual_additions = ['SOM', 'GEO', 'IRQ', 'PNG']
    out_codes = iso_3_codes + manual_additions
    code_df = pd.DataFrame({'iso3_codes': out_codes})
    code_df.to_csv(malaria_country_codes_csv)


if __name__ == '__main__':
    malarial_states = get_world_bank_countries() + states_from_CDC() + states_from_literature()
    plot_countries(malarial_states)
    get_iso3_codes(malarial_states)
