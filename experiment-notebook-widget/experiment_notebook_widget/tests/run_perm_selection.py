
from sklearn.model_selection import train_test_split

from hypergbm import HyperGBM
from hypergbm.search_space import search_space_general
from hypernets.core.callbacks import SummaryCallback, FileLoggingCallback
from hypernets.core.searcher import OptimizeDirection
from hypernets.experiment.compete import EnsembleStep
from hypernets.searchers.random_searcher import RandomSearcher
from hypernets.tabular.datasets import dsutils
from hypergbm.tests import test_output_dir
from hypernets.experiment import CompeteExperiment
import json

from hypernets.core.callbacks import EarlyStoppingCallback
from sklearn.metrics import get_scorer

df = dsutils.load_bank()
# df.drop(['id'], axis=1, inplace=True)
X_train, X_test = train_test_split(df.head(1000), test_size=0.2, random_state=42)
y_train = X_train.pop('y')
y_test = X_test.pop('y')

rs = RandomSearcher(search_space_general, optimize_direction=OptimizeDirection.Maximize)
from hypergbm.experiment_callbacks import HyperGBMNotebookExperimentCallback, HyperGBMNotebookHyperModelCallback

hk = HyperGBM(rs, task='binary', reward_metric='accuracy',
              cache_dir=f'{test_output_dir}/hypergbm_cache',
              callbacks=[HyperGBMNotebookHyperModelCallback(), EarlyStoppingCallback(3, 'max', time_limit=60, expected_reward=1)])


ce = CompeteExperiment(hk, X_train, y_train,
                       scorer=get_scorer('roc_auc'),
                       feature_reselection=True,
                       feature_reselection_estimator_size=10,
                       feature_reselection_strategy='threshold',
                       feature_reselection_threshold=0.1,
                       feature_reselection_quantile=None,
                       feature_reselection_number=None,
                       callbacks=[HyperGBMNotebookExperimentCallback()])
ce.run(max_trails=3)

print(ce)

