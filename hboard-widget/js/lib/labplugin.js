var plugin = require('./index');
var base = require('@jupyter-widgets/base');

module.exports = {
  id: 'hboard_widget:plugin',
  requires: [base.IJupyterWidgetRegistry],
  activate: function(app, widgets) {
      widgets.registerWidget({
          name: 'hboard_widget',
          version: plugin.version,
          exports: plugin
      });
  },
  autoStart: true
};

