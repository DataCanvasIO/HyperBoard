# -*- coding:utf-8 -*-

from __future__ import absolute_import

from setuptools import find_packages
from setuptools import setup


MIN_PYTHON_VERSION = '>=3.6.*'

description = 'Hypernets experiment visualization'
long_description = open('README.md', encoding='utf-8').read()
setup(
    name='hyperboard',
    version='0.1.0',
    long_description=long_description,
    long_description_content_type="text/markdown",
    description=description,
    url='https://github.com/DataCanvasIO/HyperBoard',
    author='DataCanvas Community',
    author_email='wuhf@zetyun.com',
    license='Apache License 2.0',
    install_requires=[
        "tornado",
        "hypernets>=0.2.5.1,<0.2.6"
    ],
    zip_safe=False,
    include_package_data=True,
    package_data={
        # can not inlcude a directory recursion
        'hyperboard': ['assets/*', 'assets/static/*', 'assets/static/js/*'],
    },
    python_requires=MIN_PYTHON_VERSION,
    classifiers=[
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    packages=find_packages(exclude=('docs', 'tests*')),
    entry_points={
        'console_scripts': [
            'hyperboard = hyperboard.cli:main',
        ]
    },
)
