from IPython.display import display

from hn_widget import ExperimentProcessWidget
from hypergbm.callbacks import ParseTrailEventCallback, ActionType, ABSExperimentVisCallback


class JupyterHyperModelCallback(ParseTrailEventCallback):

    def __init__(self):
        super(JupyterHyperModelCallback, self).__init__()
        self.dom_widget = None

    def set_dom_widget(self, dom_widget):
        self.dom_widget = dom_widget

    def is_ready(self):
        return super(JupyterHyperModelCallback, self).is_ready() and self.dom_widget is not None

    def send_action(self, action_type, payload):
        assert self.is_ready()
        event_dict = {
            'type': action_type,
            'data': payload
        }
        self.dom_widget.value = event_dict

    def on_search_end_(self, hyper_model, trial_data):
        if trial_data is not None:  # early stopping triggered
            self.send_action(ActionType.EarlyStopped, trial_data.to_dict())

    def on_trial_end_(self, hyper_model, space, trial_no, reward, improved, elapsed, trial_data):
        self.send_action(ActionType.TrialEnd, trial_data)


class JupyterWidgetExperimentCallback(ABSExperimentVisCallback):

    _exp_dom_mapping = {}

    def __init__(self):
        pass

    @classmethod
    def send_action(cls, exp, action_type, payload):
        event_dict = {
            'type': action_type,
            'payload': payload
        }
        dom_widget = cls._exp_dom_mapping.get(exp)
        dom_widget.value = event_dict

    @classmethod
    def add_dom_widget(cls, exp, dom_widget):
        cls._exp_dom_mapping[exp] = dom_widget

    @classmethod
    def get_dom_widget(cls, exp):
        return cls._exp_dom_mapping.get(exp)

    @classmethod
    def setup_hypermodel_callback(cls, exp, step_index):
        super().setup_hypermodel_callback(exp, step_index)

        callback = cls._find_hyper_model_callback(exp)
        assert callback
        dom_widget = cls.get_dom_widget(exp)
        callback.set_dom_widget(dom_widget)

    def experiment_start_(self, exp, experiment_data):
        widget = ExperimentProcessWidget(exp)
        display(widget)
        widget.initData = ''  # remove init data, if refresh the page will show nothing on the browser

        self.add_dom_widget(exp, widget)
        self.send_action(exp, ActionType.ExperimentStart, experiment_data)

    def experiment_end(self, exp, elapsed):
        self.send_action(exp, ActionType.ExperimentEnd, {})

    def experiment_break(self, exp, error):
        self.send_action(exp, ActionType.ExperimentBreak, {})

    def step_start_(self, exp, step, d):
        step_name = step
        step_index = self.get_step_index(exp, step_name)
        self.setup_hypermodel_callback(exp, step_index)  # update step_index everytime
        self.send_action(exp, ActionType.StepStart, d)

    def step_end_(self, exp, step, output, elapsed, experiment_data):
        self.send_action(exp, ActionType.StepStart, experiment_data)

    def step_break_(self, exp, step, error, payload):
        self.send_action(exp, ActionType.StepStart, payload)

    def hypermodel_callback_cls(self):
        return JupyterHyperModelCallback

