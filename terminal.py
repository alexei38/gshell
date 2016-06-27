# -*- coding: utf-8 -*-

import os
import gtk
import vte
import pango
import psutil
import signal
import gobject

class GshellTerm(vte.Terminal):

    def __init__(self, main_window, *args, **kwds):
        super(GshellTerm, self).__init__(*args, **kwds)
        self.mark_close = False
        self.label = None
        self.host = None
        self.pid = None
        self.page_term = None
        self.terminal_active = False
        self.config = main_window.config
        self.main_window = main_window
        self.show_all()
        self.composite_support = hasattr(self, "set_opacity") or hasattr(self, "is_composited")

    def spawn_child(self, command=None, argv=[], envv=[]):
        print 'GshellTerm::spawn_child called'
        if not command:
            command = os.getenv('SHELL')
        self.pid = self.fork_command(command=command, argv=argv, envv=envv, directory=os.getenv('HOME'))
        if self.pid == -1:
            print 'GshellTerm::spawn_child Failed execute cmd = %s argv = %s' % (command, argv)
        else:
            if command in ['sshpass', 'ssh']:
                self.terminal_active = True

    def close(self):
        print 'GshellTerm::close called'
        try:
            proc = psutil.Process(self.main_window.current_pid)
            neighbors = [p.pid for p in proc.children()]
            if self.pid in neighbors:
                print 'GshellTerm::close pid %d' % self.pid
                os.kill(self.pid, signal.SIGHUP)
        except Exception, ex:
            print 'GshellTerm::close failed: %s' % ex

    def zoom_in(self):
        print 'GshellTerm::zoom_in called'
        self.zoom_font(True)

    def zoom_out(self):
        print 'GshellTerm::zoom_out called'
        self.zoom_font(False)

    def zoom_orig(self):
        print 'GshellTerm::zoom_orig called'
        if self.config['use_system_font'] == True:
            font = self.config.get_system_font()
        else:
            font = self.config['font']
        self.set_font(pango.FontDescription(font))
        self.custom_font_size = None

    def zoom_font(self, zoom_in):
        print 'GshellTerm::zoom_font called'
        pangodesc = self.get_font()
        fontsize = pangodesc.get_size()

        if fontsize > pango.SCALE and not zoom_in:
            fontsize -= pango.SCALE
        elif zoom_in:
            fontsize += pango.SCALE

        pangodesc.set_size(fontsize)
        self.set_font(pangodesc)
        self.custom_font_size = fontsize

    def set_font(self, fontdesc):
        """Set the font we want in VTE"""
        antialias = True
        if antialias:
            try:
                antialias = vte.ANTI_ALIAS_FORCE_ENABLE
            except AttributeError:
                antialias = 1
        else:
            try:
                antialias = vte.ANTI_ALIAS_FORCE_DISABLE
            except AttributeError:
                antialias = 2
        self.set_font_full(fontdesc, antialias)

    def send_data(self, data, timeout=0, reset=False):
        if timeout > 0:
            gobject.timeout_add(timeout, self.feed_child, '%s\r' % data)
            if reset:
                gobject.timeout_add(timeout+5, self.reset, True, True)
                gobject.timeout_add(timeout+10, self.feed_child, '')
        else:
            self.feed_child('%s\r' % (data))
            if reset:
                self.reset(True, True)
                self.feed_child('')
        return True
