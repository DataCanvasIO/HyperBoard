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

name = 'experiment-notebook-widget'
pkg_name = 'experiment_notebook_widget'

LONG_DESCRIPTION = 'Jupyter widgets for hyperntes'

# Get experiment_notebook_widget version
version = get_version(pjoin(pkg_name, '_version.py'))

js_dir = pjoin(here, 'js')

# Representative files that should exist after a successful build
jstargets = [
    pjoin(js_dir, 'dist', 'index.js'),
]

data_files_spec = [
    ('share/jupyter/nbextensions/experiment_notebook_widget', 'experiment_notebook_widget/nbextension', '*.*'),
    ('share/jupyter/labextensions/experiment_notebook_widget', 'experiment_notebook_widget/labextension', '**'),
    ('share/jupyter/labextensions/experiment_notebook_widget', '.', 'install.json'),
    ('etc/jupyter/nbconfig/notebook.d', '.', 'experiment_notebook_widget.json'),
]

cmdclass = create_cmdclass('jsdeps', data_files_spec=data_files_spec)
cmdclass['jsdeps'] = combine_commands(
    install_npm(js_dir, npm=['yarn'], build_cmd='build:prod'), ensure_targets(jstargets),
)

setup_args = dict(
    name=name,
    version=version,
    description=LONG_DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    install_requires=[
        'ipywidgets>=7.6.0',
        'numpy',
        'hypernets==0.2.5',
        'pandas'
    ],
    setup_requires=['jupyter_packaging'],
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
