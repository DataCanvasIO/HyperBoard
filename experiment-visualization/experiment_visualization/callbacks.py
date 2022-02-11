import datetime
import json
import os
from pathlib import Path

from experiment_visualization.app import WebApp, WebAppRunner
from hypernets.experiment import ABSExperimentVisCallback, ActionType
from hypernets.experiment import ExperimentMeta
from hypernets.utils import logging as hyn_logging

logger = hyn_logging.getLogger(__name__)


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

    _log_mapping = {}
    _webapp_mapping = {}

    def __init__(self, hyper_model_callback_cls, log_dir=None, server_port=8888, exit_web_server_on_finish=False):
        super(LogEventExperimentCallback, self).__init__(hyper_model_callback_cls)
        self.log_dir = self._prepare_output_file(log_dir)
        self.server_port = server_port
        self.exit_web_server_on_finish = exit_web_server_on_finish

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
        self.add_webapp(exp, runner)
        runner.start()

        self.append_event(exp, ActionType.ExperimentStart, experiment_data.to_dict())

    def step_start_(self, exp, step_name, d):
        self.append_event(exp, ActionType.StepStart, d)

    def step_break_(self, exp, step, error, payload):
        self.append_event(exp, ActionType.StepBreak, payload)

    def step_end_(self, exp, step, output, elapsed, experiment_data):
        self.append_event(exp, ActionType.StepEnd, experiment_data)

    def stop_webapp_if_need(self, exp):
        if self.exit_web_server_on_finish:
            runner:WebAppRunner = self.get_webapp(exp)
            if runner is not None:
                runner.stop()
                runner.is_alive()
            else:
                logger.warning(f"runner is None for exp {str(exp)}")

    def experiment_end(self, exp, elapsed):
        self.append_event(exp, ActionType.ExperimentEnd, {})
        # self.remove_exp_log(exp)
        self.stop_webapp_if_need(exp)

    def experiment_break(self, exp, error):
        # TODO add event
        # self.remove_exp_log(exp)
        self.stop_webapp_if_need(exp)
