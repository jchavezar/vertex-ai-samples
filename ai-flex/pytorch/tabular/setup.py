from setuptools import find_packages
from setuptools import setup

setup(
    name='trainer',
    version='0.1',
    packages=find_packages(),
    install_requires=["pytorch_tabular[extra]", "pandas", "gcsfs"],
    include_package_data=True,
    description='My training application.'
)