# https://ipywidgets.readthedocs.io/en/latest/examples/Widget%20Custom.html

from __future__ import print_function
from setuptools import setup, find_packages
import os
from os.path import join as pjoin
from distutils import log

from jupyter_packaging import (
    create_cmdclass,
    install_npm,
    ensure_targets,
    combine_commands,
    get_version,
)

here = os.path.dirname(os.path.abspath(__file__))

log.set_verbosity(log.DEBUG)
log.info('setup.py entered')
log.info('$PATH=%s' % os.environ['PATH'])

name = 'hboard-widget'
pkg_name = 'hboard_widget'

LONG_DESCRIPTION = 'Jupyter widgets for hypernets'

# Get hboard_widget version
version = get_version(pjoin(pkg_name, '_version.py'))

js_dir = pjoin(here, 'js')

# Representative files that should exist after a successful build
jstargets = [
    pjoin(js_dir, 'dist', 'index.js'),
]

data_files_spec = [
    ('share/jupyter/nbextensions/hboard_widget', 'hboard_widget/nbextension', '*.*'),
    ('share/jupyter/labextensions/hboard_widget', 'hboard_widget/labextension', '**'),
    ('share/jupyter/labextensions/hboard_widget', '.', 'install.json'),
    ('etc/jupyter/nbconfig/notebook.d', '.', 'hboard_widget.json'),
]

cmdclass = create_cmdclass('jsdeps', data_files_spec=data_files_spec)
cmdclass['jsdeps'] = combine_commands(
    install_npm(js_dir, npm=['yarn'], build_cmd='build:prod'), ensure_targets(jstargets),
)

long_description = open('README.md', encoding='utf-8').read()

setup_args = dict(
    name=name,
    version=version,
    description=LONG_DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[
        'ipywidgets>=7,<9',
        'hypernets>=0.2.5.1,<0.2.6',
    ],
    setup_requires=['jupyter-packaging'],
    packages=find_packages(),
    zip_safe=False,
    cmdclass=cmdclass,
    author='wuhf',
    author_email='wuhf@zetyun.com',
    url='https://github.com/DataCanvasIO/HyperBoard.git',
    keywords=[
        'hypernets',
        'jupyter',
        'widgets',
    ],
    include_package_data=True,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: IPython',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Multimedia :: Graphics',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)

setup(**setup_args)
