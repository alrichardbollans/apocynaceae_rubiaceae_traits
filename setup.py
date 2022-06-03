from setuptools import setup, find_packages

# To install run pip install -e PATH_TO_PACKAGE

setup(
    name='apocynaceaerubiaceaetraits',
    url='https://github.com/alrichardbollans/apocynaceae_rubiaceae_traits',
    author='Adam Richard-Bollans',
    author_email='38588335+alrichardbollans@users.noreply.github.com',
    # Needed to actually package something
    packages=find_packages(include=['cleaning_plant_occurrences', 'climate_vars', 'common_name_vars',
                                    'conservation_priority',
                                    'getting_malarial_regions',
                                    'large_file_storage',
                                    'manually_collected_data', 'morphological_vars',
                                    'metabolite_vars', 'medicinal_usage_vars',
                                    'poison_vars',
                                    'wcsp_distributions',
                                    'wikipedia_vars']),
    package_data={
        "": ["outputs/*"]
    },
    # *strongly* suggested for sharing
    version='0.1',
    license='MIT',
    description='A set of python packages for plant trait data',
    long_description=open('README.md').read(),
)
