import abc
import pickle
import time
import json
import os
import datetime
from pathlib import Path

from hypernets.board.app import WebApp, WebAppRunner
from hypernets.core.callbacks import Callback, EarlyStoppingCallback
from hypernets.experiment import EarlyStoppingStatusMeta
from hypernets.experiment import ExperimentCallback, \
    ExperimentExtractor, StepMeta, ExperimentMeta
from hypernets.utils import fs, logging as hyn_logging
from hypernets.utils import get_tree_importances


logger = hyn_logging.get_logger(__name__)


class ActionType:
    ExperimentStart = 'experimentStart'
    ExperimentBreak = 'experimentBreak'
    ExperimentEnd = 'experimentEnd'
    StepStart = 'stepStart'
    StepBreak = 'stepBreak'
    StepEnd = 'stepEnd'
    EarlyStopped = 'earlyStopped'
    TrialEnd = 'trialEnd'


def append_event_to_file(event_file, action_type, payload):
    event_dict = {
        "type": action_type,
        "payload": payload
    }
    with fs.open(event_file, 'a', newline='\n') as f:
        f.write(json.dumps(event_dict))
        f.write('\n')


class ABSExperimentVisCallback(ExperimentCallback, metaclass=abc.ABCMeta):

    @staticmethod
    def get_step(experiment, step_name):
        for i, step in enumerate(experiment.steps):
            if step.name == step_name:
                return i, step
        return -1, None

    @classmethod
    def get_step_index(cls, experiment, step_name):
        return cls.get_step(experiment, step_name)[0]

    def experiment_start(self, exp):
        d = ExperimentExtractor(exp).extract()
        self.experiment_start_(exp, d)

    @abc.abstractmethod
    def experiment_start_(self, exp, experiment_data):
        raise NotImplemented

    def _find_hyper_model_callback(self, exp):
        for callback in exp.hyper_model.callbacks:
            if isinstance(callback, self.hypermodel_callback_cls()):
                return callback
        return exp

    def setup_hypermodel_callback(self, exp, step_index):
        callback = self._find_hyper_model_callback(exp)
        assert callback
        callback.set_current_running_step_index(step_index)
        callback.set_exp_id(id(exp))

    def step_start(self, exp, step):
        step_name = step
        step_index = self.get_step_index(exp, step_name)
        self.setup_hypermodel_callback(exp, step_index)

        payload = {
            'index': step_index,
            'status': StepMeta.STATUS_PROCESS,
            'start_datetime': time.time(),
        }
        self.step_start_(exp, step, payload)

    @abc.abstractmethod
    def step_start_(self, exp, step, d):
        raise NotImplemented

    def step_end(self, exp, step, output, elapsed):
        step_name = step
        step = exp.get_step(step_name)

        step.done_time = time.time()  # fix done_time is none
        step_index = self.get_step_index(exp, step_name)
        experiment_data = ExperimentExtractor.extract_step(step_index, step).to_dict()

        self.step_end_(exp, step, output, elapsed, experiment_data)

    @abc.abstractmethod
    def step_end_(self, exp, step, output, elapsed, experiment_data):
        raise NotImplemented

    def step_break(self, exp, step, error):
        step_name = step
        step_index = self.get_step_index(exp, step_name)
        payload = {
            'index': step_index,
            'extension': {
                'reason': str(error)
            },
            'status': StepMeta.STATUS_ERROR
        }
        self.step_break_(exp, step, error, payload)

    @abc.abstractmethod
    def step_break_(self, exp, step, error, payload):
        raise NotImplemented

    @classmethod
    def hypermodel_callback_cls(cls):
        raise NotImplemented


class LogEventExperimentCallback(ABSExperimentVisCallback):

    def __init__(self, log_dir=None, server_port=8888):
        self.log_dir = self._prepare_output_file(log_dir)
        self.server_port = server_port
        self._log_mapping = {}

    def _prepare_output_file(self, log_dir):
        if log_dir is None:
            log_dir = 'log'

        if log_dir[-1] == '/':
            log_dir = log_dir[:-1]

        running_dir = f'exp_{datetime.datetime.now().__format__("%m%d-%H%M%S")}'
        output_path = os.path.expanduser(f'{log_dir}/{running_dir}')

        os.makedirs(output_path, exist_ok=True)
        return Path(output_path).absolute()

    def get_log_file(self, exp):
        logfile = self._log_mapping.get(exp)
        assert logfile
        return logfile

    def add_exp_log(self, exp):
        logfile = (Path(self.log_dir) / f"events_{id(exp)}.json").absolute().as_posix()
        self._log_mapping[exp] = logfile
        return logfile

    def remove_exp_log(self, exp):
        del self._log_mapping[exp]

    def setup_hypermodel_callback(self, exp, step_index):
        super().setup_hypermodel_callback(exp, step_index)

        callback = self._find_hyper_model_callback(exp)
        assert callback
        logfile = self.get_log_file(exp)
        callback.set_log_file(logfile)

    def append_event(self, exp,  action_type, payload):
        logfile = self.get_log_file(exp)
        append_event_to_file(logfile, action_type, payload)

    def experiment_start_(self, exp, experiment_data: ExperimentMeta):
        logfile = self.add_exp_log(exp)
        logger.info(f"for experiment {id(exp)} add event file {logfile} ")
        self.append_event(exp, ActionType.ExperimentStart, experiment_data.to_dict())
        webapp = WebApp(event_file=logfile,
                        server_port=self.server_port)
        runner = WebAppRunner(webapp)
        runner.start()

    def step_start_(self, exp, step_name, d):
        self.append_event(exp, ActionType.StepStart, d)

    def step_break_(self, exp, step, error, payload):
        self.append_event(exp, ActionType.StepBreak, payload)

    def step_end_(self, exp, step, output, elapsed, experiment_data):
        self.append_event(exp, ActionType.StepEnd, experiment_data)

    def experiment_end(self, exp, elapsed):
        self.append_event(exp, ActionType.ExperimentEnd, {})
        self.remove_exp_log(exp)

    def experiment_break(self, exp, error):
        self.remove_exp_log(exp)

    def hypermodel_callback_cls(cls):
        return LogEventHyperModelCallback


class ParseTrailEventCallback(Callback):

    def __init__(self, **kwargs):
        super(ParseTrailEventCallback, self).__init__()
        self.max_trials = None
        self.current_running_step_index = None
        self.exp_id = None

    def set_exp_id(self, exp_id):
        self.exp_id = exp_id

    def set_current_running_step_index(self, value):
        self.current_running_step_index = value

    def is_ready(self):
        return self.exp_id is not None and self.current_running_step_index is not None

    @staticmethod
    def sort_imp(imp_dict, sort_imp_dict, n_features=10):
        sort_imps = []
        for k in sort_imp_dict:
            sort_imps.append({
                'name': k,
                'imp': sort_imp_dict[k]
            })

        top_features = list(
            map(lambda x: x['name'], sorted(sort_imps, key=lambda v: v['imp'], reverse=True)[: n_features]))

        imps = []
        for f in top_features:
            imps.append({
                'name': f,
                'imp': imp_dict[f]
            })
        return imps

    def on_search_start(self, hyper_model, X, y, X_eval, y_eval, cv,
                        num_folds, max_trials, dataset_id, trial_store, **fit_kwargs):
        self.max_trials = max_trials  # to record trail summary info

    @staticmethod
    def get_early_stopping_status_data(hyper_model):
        """ Return early stopping if triggered
        :param hyper_model:
        :return:
        """
        # check whether end cause by early stopping
        for c in hyper_model.callbacks:
            if isinstance(c, EarlyStoppingCallback):
                if c.triggered:
                    if c.start_time is not None:
                        elapsed_time = time.time() - c.start_time
                    else:
                        elapsed_time = None
                    ess = EarlyStoppingStatusMeta(c.best_reward, c.best_trial_no, c.counter_no_improvement_trials,
                                                  c.triggered, c.triggered_reason, elapsed_time)
                    return ess
        return None

    def on_search_end(self, hyper_model):
        assert self.is_ready()
        early_stopping_data = self.get_early_stopping_status_data(hyper_model)
        self.on_search_end_(hyper_model, early_stopping_data)

    def on_search_end_(self, hyper_model, early_stopping_data):
        pass

    @staticmethod
    def get_space_params(space):
        params_dict = {}
        for hyper_param in space.get_assigned_params():
            # param_name = hyper_param.alias[len(list(hyper_param.references)[0].name) + 1:]
            param_name = hyper_param.alias
            param_value = hyper_param.value
            # only show number param
            # if isinstance(param_value, int) or isinstance(param_value, float):
            #     if not isinstance(param_value, bool):
            #         params_dict[param_name] = param_value
            if param_name is not None and param_value is not None:
                # params_dict[param_name.split('.')[-1]] = str(param_value)
                params_dict[param_name] = str(param_value)
        return params_dict

    @staticmethod
    def assert_int_param(value, var_name):
        if value is None:
            raise ValueError(f"Var {var_name} can not be None.")
        else:
            if not isinstance(value, float) and not isinstance(value, int):
                raise ValueError(f"Var {var_name} = {value} not a number.")

    @staticmethod
    def get_trail_by_no(hyper_model, trial_no):
        for t in hyper_model.history.trials:
            if t.trial_no == trial_no:
                return t
        return None

    def on_trial_end(self, hyper_model, space, trial_no, reward, improved, elapsed):
        assert self.is_ready()

        self.assert_int_param(reward, 'reward')
        self.assert_int_param(trial_no, 'trail_no')
        self.assert_int_param(elapsed, 'elapsed')

        # pass
        trial = self.get_trail_by_no(hyper_model, trial_no)

        if trial is None:
            raise Exception(f"Trial no {trial_no} is not in history")

        model_file = trial.model_file
        with fs.open(model_file, 'rb') as f:
            model = pickle.load(f)

        cv_models = model.cv_gbm_models_
        models_json = []
        is_cv = cv_models is not None and len(cv_models) > 0
        if is_cv:
            # cv is opening
            imps = []
            for m in cv_models:
                imps.append(get_tree_importances(m))

            imps_avg = {}
            for k in imps[0]:
                imps_avg[k] = sum([imp.get(k, 0) for imp in imps]) / 3

            for fold, m in enumerate(cv_models):
                models_json.append({
                    'fold': fold,
                    'importances': self.sort_imp(get_tree_importances(m), imps_avg)
                })
        else:
            gbm_model = model.gbm_model
            if gbm_model is None:
                raise Exception("Both cv_models or gbm_model is None ")
            imp_dict = get_tree_importances(gbm_model)
            models_json.append({
                'fold': None,
                'importances': self.sort_imp(imp_dict, imp_dict)
            })
        early_stopping_status = None
        for c in hyper_model.callbacks:
            if isinstance(c, EarlyStoppingCallback):
                early_stopping_status = EarlyStoppingStatusMeta(c.best_reward, c.best_trial_no,
                                                                c.counter_no_improvement_trials,
                                                                c.triggered,
                                                                c.triggered_reason,
                                                                time.time() - c.start_time).to_dict()
                break
        trial_data = {
            "trialNo": trial_no,
            "maxTrials": self.max_trials,
            "hyperParams": self.get_space_params(space),
            "models": models_json,
            "reward": reward,
            "elapsed": elapsed,
            "is_cv": is_cv,
            "metricName": hyper_model.reward_metric,
            "earlyStopping": early_stopping_status
        }
        data = {
            'modelInstanceId': id(hyper_model),
            'trialData': trial_data
        }
        self.on_trial_end_(hyper_model, space, trial_no, reward, improved, elapsed, data)

    def on_trial_end_(self, hyper_model, space, trial_no, reward, improved, elapsed, trial_data):
        pass


class LogEventHyperModelCallback(ParseTrailEventCallback):

    def __init__(self):
        super(LogEventHyperModelCallback, self).__init__()
        self.log_file = None

    def set_log_file(self, log_file):
        self.log_file = log_file

    def is_ready(self):
        return super(LogEventHyperModelCallback, self).is_ready() and self.log_file is not None

    def on_search_end_(self, hyper_model, early_stopping_data):
        if early_stopping_data is not None:
            payload = early_stopping_data.to_dict()
            append_event_to_file(self.log_file, ActionType.EarlyStopped, payload)

    def on_trial_end_(self, hyper_model, space, trial_no, reward, improved, elapsed, trial_data):
        append_event_to_file(self.log_file, ActionType.TrialEnd, trial_data)
