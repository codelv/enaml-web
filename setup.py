'''
Created on Apr 17, 2017

@author: jrm
'''
from setuptools import setup, find_packages

setup(
    name='enaml-web',
    version='0.1.2',
    author='frmdstryr',
    author_email='frmdstryr@gmail.com',
    url='https://gitlab.com/frmdstryr/enaml-web',
    description='Web component toolkit for Enaml',
    license = "MIT",
    long_description=open('README.md').read(),
    requires=['enaml'],
    install_requires=['distribute', 'enaml >= 0.9.8', 'lxml>=3.4.0', 'future'],
    optional_requires=['watchdog', 'Pygments', 'Markdown'],
    packages=find_packages(),
)
