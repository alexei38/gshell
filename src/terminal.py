# -*- coding: utf-8 -*-

import os
import gtk
import vte
import pango
import psutil
import signal
import gobject

class GshellTerm(vte.Terminal):

    __gsignals__ = {
        'enable-broadcast': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,(gobject.TYPE_OBJECT,)),
    }


    def __init__(self, gshell, *args, **kwds):
        super(GshellTerm, self).__init__(*args, **kwds)
        self.mark_close = False
        self.label = None
        self.host = None
        self.pid = None
        self.page_term = None
        self.seatch = None
        self.scrollbar = None
        self.logger = None
        self.notebook = None
        self.terminal_active = False
        self.broadcast = False
        self.composite_support = hasattr(self, "set_opacity") or hasattr(self, "is_composited")
        self.config = gshell.config
        self.gshell = gshell
        self.show_all()
        self.configure()

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
            proc = psutil.Process(self.gshell.current_pid)
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

    def configure(self):
        if hasattr(self, 'set_alternate_screen_scroll'):
            self.set_alternate_screen_scroll(self.config['alternate_screen_scroll'])
        if self.config['copy_on_selection']:
            self.connect('selection-changed', lambda widget: self.copy_clipboard())
        self.set_emulation(self.config['emulation'])
        self.set_encoding(self.config['encoding'])
        self.set_word_chars(self.config['word_chars'])
        self.set_mouse_autohide(self.config['mouse_autohide'])
        if self.config['use_system_font'] == True:
            font = self.config.get_system_font()
        else:
            font = self.config['font']
        self.set_font(pango.FontDescription(font))
        self.set_allow_bold(self.config['allow_bold'])
        if self.config['use_theme_colors']:
            self.fgcolor_active = self.get_style().text[gtk.STATE_NORMAL]
            self.bgcolor = self.get_style().base[gtk.STATE_NORMAL]
        else:
            self.fgcolor_active = gtk.gdk.color_parse(self.config['foreground_color'])
            self.bgcolor = gtk.gdk.color_parse(self.config['background_color'])

        factor = self.config['inactive_color_offset']
        if factor > 1.0:
          factor = 1.0
        self.fgcolor_inactive = self.fgcolor_active.copy()

        for bit in ['red', 'green', 'blue']:
            setattr(self.fgcolor_inactive, bit,
                    getattr(self.fgcolor_inactive, bit) * factor)

        colors = self.config['palette'].split(':')
        self.palette_active = []
        self.palette_inactive = []
        for color in colors:
            if color:
                newcolor = gtk.gdk.color_parse(color)
                newcolor_inactive = newcolor.copy()
                for bit in ['red', 'green', 'blue']:
                    setattr(newcolor_inactive, bit, getattr(newcolor_inactive, bit) * factor)
                self.palette_active.append(newcolor)
                self.palette_inactive.append(newcolor_inactive)
        self.set_colors(self.fgcolor_active, self.bgcolor, self.palette_active)
        if hasattr(self, 'set_cursor_shape'):
            self.set_cursor_shape(getattr(vte, 'CURSOR_SHAPE_%s' % self.config['cursor_shape'].upper()))

        background_type = self.config['background_type']
        if background_type == 'image' and self.config['background_image'] is not None and self.config['background_image'] != '':
            self.set_background_image_file(self.config['background_image'])
            self.set_scroll_background(self.config['scroll_background'])
        else:
            try:
                self.set_background_image(None)
            except TypeError:
                pass
            self.set_scroll_background(False)

        if background_type in ('image', 'transparent'):
            self.set_background_tint_color(gtk.gdk.color_parse(
                                               self.config['background_color']))
            opacity = int(self.config['background_darkness'] * 65536)
            saturation = 1.0 - float(self.config['background_darkness'])
            self.set_background_saturation(saturation)
        else:
            opacity = 65535
            self.set_background_saturation(1)

        if self.composite_support:
            self.set_opacity(opacity)
        if not self.composite_support or self.config['disable_real_transparency']:
            background_transparent = True
        else:
            if self.is_composited() == False:
                background_transparent = True
            else:
                background_transparent = False
        if self.config['background_type'] == 'transparent':
            self.set_background_transparent(background_transparent)
        else:
            self.set_background_transparent(False)

        if hasattr(vte, 'VVVVTE_CURSOR_BLINK_ON'):
            if self.config['cursor_blink'] == True:
                self.set_cursor_blink_mode('VTE_CURSOR_BLINK_ON')
            else:
                self.set_cursor_blink_mode('VTE_CURSOR_BLINK_OFF')
        else:
            self.set_cursor_blinks(self.config['cursor_blink'])

        if self.config['scrollback_infinite'] == True:
            scrollback_lines = -1
        else:
            scrollback_lines = self.config['scrollback_lines']
        self.set_scrollback_lines(scrollback_lines)
        self.set_scroll_on_keystroke(self.config['scroll_on_keystroke'])
        self.set_scroll_on_output(self.config['scroll_on_output'])

        self.connect('focus-in-event', self.on_terminal_focus_in)
        self.connect('focus-out-event', self.on_terminal_focus_out)
        self.connect('key-press-event', self.on_keypress)
        self.connect('enable-broadcast', self.enable_broadcast)

        self.queue_draw()
        return False

    def on_keypress(self, widget, event):
        if not event:
            return False
        if self.broadcast and self.is_focus():
            self.notebook.all_emit(self, 'key-press-event', event)
            return False

    def on_terminal_focus_in(self, *args):
        if self:
            self.set_colors(self.fgcolor_active, self.bgcolor, self.palette_active)
        return False

    def on_terminal_focus_out(self, *args):
        if self:
            self.set_colors(self.fgcolor_inactive, self.bgcolor, self.palette_inactive)
        return False

    def enable_broadcast(self, *args):
        self.broadcast = not self.broadcast
        if self.broadcast:
            self.label.broadcast_image = gtk.Image()
            broadcast_icon_file = self.config.get_icon('broadcast.png')
            broadcast_icon = gtk.gdk.pixbuf_new_from_file_at_size(broadcast_icon_file, 18, 18)
            self.label.broadcast_image.set_from_pixbuf(broadcast_icon)
            self.label.broadcast_image.show()
            self.label.prefix_box.pack_start(self.label.broadcast_image, False, False, 1)
        else:
            if isinstance(self.label.broadcast_image, gtk.Image):
                self.label.broadcast_image.destroy()
