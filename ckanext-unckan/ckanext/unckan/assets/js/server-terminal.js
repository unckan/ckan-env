(function (ckan, $) {
  'use strict';

  ckan.module('server-terminal', function ($) {
    return {
      initialize: function () {
        this.output = this.el.find('[data-terminal-output]');
        this.status = this.el.find('[data-terminal-status]');
        if (!this.output.length) return;
        this.el.on('change', '[data-terminal-source], [data-terminal-lines]', $.proxy(this.load, this));
        this.el.on('click', '[data-terminal-action="refresh"]', $.proxy(this.load, this));
        this.load();
        this.timer = window.setInterval($.proxy(this.load, this), 3000);
      },
      teardown: function () {
        window.clearInterval(this.timer);
      },
      load: function () {
        var self = this;
        $.getJSON(this.options.endpoint, {
          source: this.el.find('[data-terminal-source]').val(),
          lines: this.el.find('[data-terminal-lines]').val()
        }).done(function (data) {
          self.output.text(data.content || '—');
          self.status.text('Actualizado: ' + new Date().toLocaleTimeString() + ' · ' + data.size + ' bytes');
          if (self.el.find('[data-terminal-follow]').is(':checked')) {
            var screen = self.el.find('.server-terminal__screen')[0];
            screen.scrollTop = screen.scrollHeight;
          }
        }).fail(function (response) {
          var message = response.responseJSON && response.responseJSON.error;
          self.status.text(message || 'No se pudieron cargar los logs.');
        });
      }
    };
  });
})(this.ckan, this.jQuery);
