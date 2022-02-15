# experiment-notebook-widget

This widget is used to visualize the running the hypernets experiment in jupyter notebook or jupyterlab.

## build from source code

`hypernets jupyter widget` relies on `hypernets experiment`,  to build the software environment required by the project:

- [python 3.7+](https://python.org)
- [nodejs v14.15.0+](https://nodejs.org/en/)
- [pip 20.0.2+](https://pypi.org/project/pip/)
- [jupyterlab 2.0.0+ ](https://jupyter.org/) (if you're using jupyterlab)

Clone the repo:

```bash
git clone https://github.com/DataCanvasIO/HyperBoard.git
```

Build React project `hypernets-experiment`:

```bash
cd experiment-notebook-widget
python setup.py install
```

Enable the widget:
```bash
jupyter nbextension install --py --symlink --sys-prefix hn_widget
jupyter nbextension enable --py --sys-prefix hn_widget
```
