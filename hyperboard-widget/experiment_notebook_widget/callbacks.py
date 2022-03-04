from IPython.display import display

from experiment_notebook_widget import ExperimentProcessWidget
from hypernets.experiment import ABSExpVisExperimentCallback, ActionType


class NotebookExperimentCallback(ABSExpVisExperimentCallback):

    _exp_dom_mapping = {}

    @classmethod
    def send_action(cls, exp_id, action_type, payload):
        event_dict = {
            'type': action_type,
            'payload': payload
        }
        dom_widget = cls.get_dom_widget(exp_id)
        dom_widget.value = event_dict

    @classmethod
    def send_action_(cls, exp, action_type, payload):
        cls.send_action(id(exp), action_type, payload)

    @classmethod
    def add_dom_widget(cls, exp, dom_widget):
        cls._exp_dom_mapping[id(exp)] = dom_widget

    @classmethod
    def get_dom_widget(cls, exp_id):
        return cls._exp_dom_mapping.get(exp_id)

    def experiment_start_(self, exp, experiment_data):
        widget = ExperimentProcessWidget(exp)
        display(widget)
        widget.initData = ''  # remove init data, if refresh the page will show nothing on the browser
        self.add_dom_widget(exp, widget)
        self.send_action_(exp, ActionType.ExperimentStart, experiment_data.to_dict())

    def experiment_end(self, exp, elapsed):
        self.send_action_(exp, ActionType.ExperimentEnd, {})

    def experiment_break(self, exp, error):
        self.send_action_(exp, ActionType.ExperimentBreak, {})

    def step_start_(self, exp, step, d):
        step_name = step
        step_index = self.get_step_index(exp, step_name)
        self.setup_hyper_model_callback(exp, step_index)  # update step_index everytime
        self.send_action_(exp, ActionType.StepStart, d)

    def step_end_(self, exp, step, output, elapsed, step_meta_dict):
        self.send_action_(exp, ActionType.StepEnd, step_meta_dict)

    def step_break_(self, exp, step, error, payload):
        self.send_action_(exp, ActionType.StepBreak, payload)
