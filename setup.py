from setuptools import setup, find_packages

# To install run pip install -e PATH_TO_PACKAGE

setup(
    name='apocynaceaerubiaceaetraits',
    url='https://github.com/alrichardbollans/apocynaceae_rubiaceae_traits',
    author='Adam Richard-Bollans',
    author_email='38588335+alrichardbollans@users.noreply.github.com',
    # Needed to actually package something
    packages=find_packages(include=['alkaloid_vars', 'climate_vars','common_name_vars',
                                    'manually_collected_data', 'morphological_vars',
                                    'metabolite_vars', 'medicinal_usage_vars', 'parse_main_trait_table',
                                    'wikipedia_vars']),
    # *strongly* suggested for sharing
    version='0.1',
    license='MIT',
    description='A set of python packages for plant trait data',
    long_description=open('README.md').read(),
)