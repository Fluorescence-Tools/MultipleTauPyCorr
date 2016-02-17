from distutils.core import setup, Extension

module = Extension('multipletau_cor_tttr/CCF',
                    sources = ['multipletau_cor_tttr/CCF.c'])

setup(
    name='multipletau_cor_tttr',
    version='0.1.3',
    author='Anders Barth',
    author_email='anders.barth@gmail.com',
    packages=['multipletau_cor_tttr'],
    include_package_data = True,
    scripts=['bin/cor_from_file.py', 'bin/multipletau_cor_tttr_example.py',
             'bin/sampledata/sample_data.npy','bin/sampledata/sample.spc'],
    url='http://testpypi.python.org/pypi/multipletau_cor_tttr/',
    description='Library for correlation of time-tagged time-resolved photon data for fluorescence correlation spectroscopy (FCS) analysis.',
    long_description=open('README').read(),
      ext_modules = [module],
)