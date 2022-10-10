# hboard-widget

[![Python Versions](https://img.shields.io/pypi/pyversions/hboard-widget.svg)](https://pypi.org/project/hboard-widget)
[![Downloads](https://pepy.tech/badge/hboard-widget)](https://pepy.tech/project/hboard-widget)
[![PyPI Version](https://img.shields.io/pypi/v/hboard-widget.svg)](https://pypi.org/project/hboard-widget)

[中文](README_zh_CN.md)

This project provides a visualization tool for experiment information based on jupyter notebook/ jupyterlab widget.

## Installation

**Install with pip**
```shell
pip install hboard-widget
```

**Install with conda**
```shell
conda install -c conda-forge hboard-widget
```

**Install with source code**

Build from source code need following requirements:
- [python 3.7+](https://python.org)
- [nodejs v14.15.0+](https://nodejs.org/en/)
- [pip 20.0.2+](https://pypi.org/project/pip/)
- [jupyterlab 2.0.0+ ](https://jupyter.org/)

*The project need frontend of [hboard](../hboard) to be built in advance.*

Clone the source code:
```bash
git clone https://github.com/DataCanvasIO/HyperBoard.git
```

Build for development:
```bash
cd ./hboard-widget
pip install -e .
jupyter nbextension install --py --symlink --overwrite --sys-prefix hboard_widget
jupyter nbextension enable --py --sys-prefix hboard_widget
jupyter labextension develop --overwrite hboard_widget
```

You need to rebuild the JS when you make a code change:
```shell
cd ./hboard-widget/js
yarn run build
```

## Example 

The following steps shows how to implement the experiment visualization in notebook

1. Import the required modules：
```python
import warnings
warnings.filterwarnings('ignore')

from sklearn.model_selection import train_test_split
from hypernets.examples.plain_model import PlainModel, PlainSearchSpace
from hypernets.experiment import make_experiment
from hypernets.tabular.datasets import dsutils
```

2. Create an experiment
```python
df = dsutils.load_boston()
df_train, df_eval = train_test_split(df, test_size=0.2)
search_space = PlainSearchSpace(enable_lr=False, enable_nn=False, enable_dt=False, enable_dtr=True)
experiment = make_experiment(PlainModel, df_train,
                             target='target',
                             search_space=search_space,
                             callbacks=[],
                             search_callbacks=[])
```

3. Experiment visualization configurations

```python
from hboard_widget import ExperimentSummary
experiment_summary_widget = ExperimentSummary(experiment)
display(experiment_summary_widget)
```

<img width="80%" height="80%" src="docs/images/experiment_config.png"/>



4. Visualize the dataset information

```python
from hboard_widget import DatasetSummary
dataset_summary_widget = DatasetSummary(experiment.get_data_character())
display(dataset_summary_widget)
```

<img width="80%" height="80%" src="docs/images/experiment_dataset.png"/>


5. Visualize the experiment process

```python
from hboard_widget import ExperimentProcessWidget
estimator = experiment.run(max_trials=3)

widget = ExperimentProcessWidget(experiment)
display(widget)
```
<img width="80%" height="80%" src="docs/images/experiment_process.png"/>

Find the project in Notebook [experiment visualization notebook.ipynb](hboard_widget/examples/01.visual_experiment.ipynb).


## Related project

Currently, [HyperGBM](https://github.com/DataCanvasIO/HyperGBM) has integrated this tool. The HyperGBM experiment could call the notebook widget visualization function and display the experiment dashboard. Please refer to [HyperGBM: Experiment Visualization in Notebook](https://hypergbm.readthedocs.io/en/latest/quick_start_notebook.html)


