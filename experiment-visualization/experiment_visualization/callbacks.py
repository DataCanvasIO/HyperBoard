from hypernets.experiment import ABSExperimentVisCallback, ActionType
import abc
import pickle
import time
import json
import os
import datetime
from pathlib import Path

from experiment_visualization.app import WebApp, WebAppRunner
from hypernets.core.callbacks import Callback, EarlyStoppingCallback
from hypernets.experiment import EarlyStoppingStatusMeta
from hypernets.experiment import ExperimentCallback, \
    ExperimentExtractor, StepMeta, ExperimentMeta
from hypernets.utils import fs, logging as hyn_logging
from hypernets.utils import get_tree_importances


def append_event_to_file(event_file, action_type, payload):
    event_dict = {
        "type": action_type,
        "payload": payload
    }
    # fs.open
    with open(event_file, 'a', newline='\n') as f:
        f.write(json.dumps(event_dict))
        f.write('\n')


class LogEventExperimentCallback(ABSExperimentVisCallback):

    def __init__(self, hyper_model_callback_cls, log_dir=None, server_port=8888):
        super(LogEventExperimentCallback, self).__init__(hyper_model_callback_cls)
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
        logfile_path = Path(self.log_dir) / f"events_{id(exp)}.json"
        if not logfile_path.parent.exists():
            os.makedirs(logfile_path.parent, exist_ok=True)
        logfile = logfile_path.absolute().as_posix()
        self._log_mapping[exp] = logfile
        return logfile

    def remove_exp_log(self, exp):
        del self._log_mapping[exp]

    def setup_hyper_model_callback(self, exp, step_index):
        super().setup_hyper_model_callback(exp, step_index)

        callback = self._find_hyper_model_callback(exp)
        assert callback
        logfile = self.get_log_file(exp)
        callback.set_log_file(logfile)

    def append_event(self, exp,  action_type, payload):
        logfile = self.get_log_file(exp)
        append_event_to_file(logfile, action_type, payload)

    def experiment_start(self, exp):
        self.add_exp_log(exp)
        super(LogEventExperimentCallback, self).experiment_start(exp)

    def experiment_start_(self, exp, experiment_data: ExperimentMeta):
        # logger.info(f"for experiment {id(exp)} add event file {logfile} ")
        logfile = self.get_log_file(exp)
        webapp = WebApp(event_file=logfile,
                        server_port=self.server_port)
        runner = WebAppRunner(webapp)
        runner.start()
        self.append_event(exp, ActionType.ExperimentStart, experiment_data.to_dict())

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

