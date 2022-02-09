experiment_notebook_widget
===============================

Jupyter widgets for hyperntes

Installation
------------

To install use pip:

    $ pip install hypernets-jupyter-widget

For a development installation (requires [Node.js](https://nodejs.org) and [Yarn version](https://classic.yarnpkg.com/)),

    $ git clone https://github.com/DataCanvas/experiment_notebook_widget.git
    $ cd experiment_notebook_widget
    $ pip install -e .
    $ jupyter nbextension install --py --symlink --overwrite --sys-prefix experiment_notebook_widget
    $ jupyter nbextension enable --py --sys-prefix experiment_notebook_widget

When actively developing your extension for JupyterLab, run the command:

    $ jupyter labextension develop --overwrite experiment_notebook_widget

Then you need to rebuild the JS when you make a code change:

    $ cd js
    $ yarn run build

You then need to refresh the JupyterLab page when your javascript changes.
