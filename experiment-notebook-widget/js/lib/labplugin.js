var plugin = require('./index');
var base = require('@jupyter-widgets/base');

module.exports = {
  id: 'experiment_notebook_widget:plugin',
  requires: [base.IJupyterWidgetRegistry],
  activate: function(app, widgets) {
      widgets.registerWidget({
          name: 'experiment_notebook_widget',
          version: plugin.version,
          exports: plugin
      });
  },
  autoStart: true
};

