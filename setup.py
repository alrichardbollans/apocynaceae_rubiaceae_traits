from setuptools import setup, find_packages

# To install run pip install -e PATH_TO_PACKAGE

setup(
    name='apocynaceaerubiaceaetraits',
    url='https://github.com/alrichardbollans/apocynaceae_rubiaceae_traits',
    author='Adam Richard-Bollans',
    author_email='38588335+alrichardbollans@users.noreply.github.com',
    # Needed to actually package something
    packages=find_packages(include=['climate_vars', 'common_name_vars',
                                    'conservation_priorities',
                                    'poison_vars',
                                    'manually_collected_data', 'morphological_vars',
                                    'metabolite_vars', 'medicinal_usage_vars',
                                    'wikipedia_vars']),
    # *strongly* suggested for sharing
    version='0.1',
    license='MIT',
    description='A set of python packages for plant trait data',
    long_description=open('README.md').read(),
)
