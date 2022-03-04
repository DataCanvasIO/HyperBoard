var plugin = require('./index');
var base = require('@jupyter-widgets/base');

module.exports = {
  id: 'hyperboard_widget:plugin',
  requires: [base.IJupyterWidgetRegistry],
  activate: function(app, widgets) {
      widgets.registerWidget({
          name: 'hyperboard_widget',
          version: plugin.version,
          exports: plugin
      });
  },
  autoStart: true
};

