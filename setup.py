"""
Created on Apr 17, 2017

@author: jrm
"""
from setuptools import setup, find_packages

setup(
    name='enaml-web',
    version='0.10.2',
    author='CodeLV',
    author_email='frmdstryr@gmail.com',
    url='https://github.com/codelv/enaml-web',
    description='Web component toolkit for Enaml',
    license="MIT",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    requires=['enaml'],
    install_requires=['enaml >= 0.9.8', 'lxml>=3.4.0'],
    optional_requires=[
        'Pygments', 'Markdown', 'nbconvert',  # extra components
    ],
    packages=find_packages(),
)
