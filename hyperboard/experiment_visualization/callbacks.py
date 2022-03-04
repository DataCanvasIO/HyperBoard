import datetime
import json
import os
from typing import Type
from pathlib import Path

from experiment_visualization.app import WebApp, WebAppRunner
from hypernets.experiment import ABSExpVisExperimentCallback, ActionType, ABSExpVisHyperModelCallback
from hypernets.experiment import ExperimentMeta
from hypernets.utils import logging as hyn_logging

logger = hyn_logging.getLogger(__name__)


def _append_event_to_file(event_file, action_type, payload):
    event_dict = {
        "type": action_type,
        "payload": payload
    }
    # fs.open
    with open(event_file, 'a', newline='\n') as f:
        f.write(json.dumps(event_dict))
        f.write('\n')


class WebVisHyperModelCallback(ABSExpVisHyperModelCallback):  # Final class

    def __init__(self, parse_trial):
        super(WebVisHyperModelCallback, self).__init__()
        self.event_file = None
        self.parse_trial = parse_trial

    def set_log_file(self, log_file):
        self.event_file = log_file

    def assert_ready(self):
        super(WebVisHyperModelCallback, self).assert_ready()
        assert self.event_file is not None

    def send_event(self, action_type, payload):
        _append_event_to_file(self.event_file, action_type, payload)

    def on_search_end_(self, hyper_model, early_stopping_data):
        if early_stopping_data is not None:
            payload = early_stopping_data.to_dict()
            self.send_event(ActionType.EarlyStopped, payload)

    def on_trial_end(self, hyper_model, space, trial_no, reward, improved, elapsed):
        self.assert_ready()
        trial_event_data = self.parse_trial(hyper_model, space, trial_no, reward,
                                            improved, elapsed, self.max_trials, self.current_running_step_index)
        self.send_event(ActionType.TrialEnd, trial_event_data)


class WebVisExperimentCallback(ABSExpVisExperimentCallback):

    _log_mapping = {}
    _webapp_mapping = {}

    def __init__(self, event_file_dir="./events", server_port=8888, exit_web_server_on_finish=False):
        """
        Parameters
        ----------
        event_file_dir : str, optional, default is "./events"
            where to store experiment running events log
        server_port : int, optional, default is 8888
            http server port.
        exit_web_server_on_finish : str, optional, default is False
            whether to exit http server after experiment finished.
        """
        super(WebVisExperimentCallback, self).__init__(WebVisHyperModelCallback)
        self.event_file_dir = self._prepare_output_file(event_file_dir)
        self.server_port = server_port
        self.exit_web_server_on_finish = exit_web_server_on_finish

    @staticmethod
    def _prepare_output_file(event_file_dir):
        if event_file_dir[-1] == '/':
            event_file_dir = event_file_dir[:-1]
        abs_event_file_dir = Path(event_file_dir).absolute().as_posix()

        os.makedirs(abs_event_file_dir, exist_ok=True)
        return abs_event_file_dir

    def get_log_file(self, exp):
        logfile = self._log_mapping.get(exp)
        assert logfile
        return logfile

    def add_exp_log(self, exp):
        logfile_path = Path(self.event_file_dir) / f"events_{id(exp)}.json"
        logger.info(f"create experiment event file: {logfile_path}")
        if not logfile_path.parent.exists():
            os.makedirs(logfile_path.parent, exist_ok=True)
        logfile = logfile_path.absolute().as_posix()
        self._log_mapping[exp] = logfile
        return logfile

    def get_webapp(self, exp):
        return self._webapp_mapping.get(exp)

    def add_webapp(self, exp, webapp):
        self._webapp_mapping[exp] = webapp

    def remove_exp_log(self, exp):
        del self._log_mapping[exp]

    def setup_hyper_model_callback(self, exp, step_index):
        super().setup_hyper_model_callback(exp, step_index)

        callback = self._find_hyper_model_callback(exp)
        assert callback
        logfile = self.get_log_file(exp)
        callback.set_log_file(logfile)

    def send_event(self, exp, action_type, payload):
        logfile = self.get_log_file(exp)
        _append_event_to_file(logfile, action_type, payload)

    def experiment_start(self, exp):
        self.add_exp_log(exp)
        super(WebVisExperimentCallback, self).experiment_start(exp)

    def experiment_start_(self, exp, experiment_data: ExperimentMeta):
        # logger.info(f"for experiment {id(exp)} add event file {logfile} ")
        logfile = self.get_log_file(exp)
        webapp = WebApp(event_file=logfile,
                        server_port=self.server_port)
        runner = WebAppRunner(webapp)
        self.add_webapp(exp, runner)
        runner.start()

        self.send_event(exp, ActionType.ExperimentStart, experiment_data.to_dict())

    def step_start_(self, exp, step_name, d):
        self.send_event(exp, ActionType.StepStart, d)

    def step_break_(self, exp, step, error, payload):
        self.send_event(exp, ActionType.StepBreak, payload)

    def step_end_(self, exp, step, output, elapsed, experiment_data):
        self.send_event(exp, ActionType.StepEnd, experiment_data)

    def stop_webapp_if_need(self, exp):
        if self.exit_web_server_on_finish:
            runner:WebAppRunner = self.get_webapp(exp)
            if runner is not None:
                runner.stop()
                runner.is_alive()
            else:
                logger.warning(f"runner is None for exp {str(exp)}")

    def experiment_end(self, exp, elapsed):
        self.send_event(exp, ActionType.ExperimentEnd, {})
        # self.remove_exp_log(exp)
        self.stop_webapp_if_need(exp)

    def experiment_break(self, exp, error):
        # TODO add event
        # self.remove_exp_log(exp)
        self.stop_webapp_if_need(exp)
