# -*- coding: utf-8 -*-

import os
import gtk
import time

class GshellLogger(object):

    def __init__(self, terminal):
        super(GshellLogger, self).__init__()
        self.terminal = terminal
        self.log_file = None
        self.handler_id = None
        self.last_row = 0
        self.last_col = 0
        self.logging = False

    def start_logger(self, log_file=None):
        self.log_file = log_file
        if not self.log_file:
            savedialog = gtk.FileChooserDialog(title="Save Log File As",
                                           action=gtk.FILE_CHOOSER_ACTION_SAVE,
                                           buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                                    gtk.STOCK_SAVE, gtk.RESPONSE_OK))
            savedialog.set_do_overwrite_confirmation(True)
            savedialog.set_local_only(True)
            savedialog.show_all()
            response = savedialog.run()
            if response == gtk.RESPONSE_OK:
                self.log_file = os.path.join(savedialog.get_current_folder(),
                                             savedialog.get_filename())
            savedialog.destroy()
        if self.log_file:
            try:
                self.log = open(self.log_file, 'a')
                self.log.write("\n\n\n%s\nSession opened at %s\n%s\n" % ("-"*80, time.strftime("%Y-%m-%d %H:%M:%S"), "-"*80))
                self.handler_id = self.terminal.connect('contents-changed', self.on_contents_changed)
                self.last_col, self.last_row = self.terminal.get_cursor_position()
                self.logging = True
            except Exception, e:
                print 'Error write to log file: %s' % self.log_file
                print e
                return

    def stop_logger(self):
        if self.handler_id:
            self.terminal.disconnect(self.handler_id)
        col, row = self.terminal.get_cursor_position()
        if self.last_row != row:
            text = self.terminal.get_text_range(self.last_row, self.last_col, row, col, lambda *a: True)
            self.log.write(text[:-1])
            self.last_row = row
            self.last_col = col
        self.log.close()
        self.logging = False

    def on_contents_changed(self, widget, *args):
        col, row = self.terminal.get_cursor_position()
        if self.last_row != row:
            text = self.terminal.get_text_range(self.last_row, self.last_col, row, col, lambda *a: True)
            self.log.write(text[:-1])
            self.last_row = row
            self.last_col = col
