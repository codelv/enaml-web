"""
Created on Apr 17, 2017

@author: jrm
"""
from setuptools import Extension, setup, find_packages

speedups_module = Extension(
    "web.core.speedups",
    ["src/speedups.c"],
    include_dirs=["src"],
    language="c",
    optional=True,
)

setup(
    name='enaml-web',
    version='0.11.3',
    author='CodeLV',
    author_email='frmdstryr@gmail.com',
    url='https://github.com/codelv/enaml-web',
    description='Web component toolkit for Enaml',
    license="MIT",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    requires=['enaml'],
    python_requires='>=3.9',
    install_requires=['enaml >= 0.9.8', 'lxml>=3.4.0'],
    optional_requires=[
        'Pygments', 'Markdown', 'nbconvert',  # extra components
    ],
    ext_modules=[speedups_module],
    packages=find_packages(),
)
