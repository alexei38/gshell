# -*- coding: utf-8 -*-

import os
import gtk
import vte
import pango
import signal
from config import Config

class GshellTerm(vte.Terminal):

    def __init__(self, main_window, *args, **kwds):
        super(GshellTerm, self).__init__(*args, **kwds)
        self.pid = None
        self.config = main_window.config
        self.show_all()
        self.composite_support = hasattr(self, "set_opacity") or hasattr(self, "is_composited")

    def spawn_child(self, command=None):
        if not command:
            command = os.getenv('SHELL')
        self.pid = self.fork_command(command=command, directory=os.getenv('HOME'))

    def close(self):
        print 'GshellTerm::close called'
        print 'GshellTerm::close pid %d' % self.pid
        try:
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