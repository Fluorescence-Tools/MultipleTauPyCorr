from distutils.core import setup, Extension

module = Extension('multipletau_cor_tttr/CCF',
                   sources=['multipletau_cor_tttr/CCF.c'])

setup(
    name='multipletau_cor_tttr',
    version='0.1.2',
    author='Anders Barth',
    license='MIT',
    author_email='anders.barth@gmail.com',
    packages=['multipletau_cor_tttr'],
    package_data={'multipletau_cor_tttr': ['sample/sample_data.npy', 'sample/multipletau_cor_tttr_example.py']},
    url='http://testpypi.python.org/pypi/multipletau_cor_tttr/',
    description='Library for correlation of time-tagged time-resolved photon data for'
                ' fluorescence correlation spectroscopy (FCS) analysis.',
    long_description=open('README').read(),
    ext_modules=[module],
    install_requires=['numpy', 'matplotlib'],
    classifiers=['Programming Language :: Python :: 2.7',
                 'Programming Language :: Python :: 3.5'],
    keywords=['FCS Fluorescence Correlation Spectroscopy Single Photon Counting TTTR Multiple-tau algorithm']
)
