__author__ = 'jgevirtz'




from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

setup(
    name='simpleorm',
    version='1.2.0',
    description='A toy ORM backed by MySQL as an example of how an ORM might be designed.',
    url='https://github.com/joshgev/simpleorm',
    author='Joshua Gevirtz',
    author_email='joshgev@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Documentation',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
    keywords='example mysql orm',
    packages=find_packages(),
    install_requires=['mysqlclient'])