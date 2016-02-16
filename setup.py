from distutils.core import setup

setup(
    name='py',
    version='0.1',
    author='Anders Barth',
    author_email='anders.barth@gmail.com',
    packages=['multipletau_cor_tttr'],
    scripts=['bin/cor_from_file.py','bin/multipletau_cor_tttr_example.py'],
    url='http://pypi.python.org/pypi/multipletau_cor_tttr/',
    #license='LICENSE.txt',
    description='Library for correlation of time-tagged time-resolved photon data for fluorescence correlation spectroscopy (FCS) analysis.',
    long_description=open('README').read(),
    install_requires=[
        "numpy >= 1.9.3",
        "matplotlib >= 1.4.3",
        "ctypes >= 1.1.0"
    ],
)