#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import gtk
import vte
import pango
import signal
import gobject
from config import Config
from itertools import groupby
from collections import OrderedDict
from editablelabel import EditableLabel


class GshellTerm(vte.Terminal):

    def __init__(self, *args, **kwds):
        super(GshellTerm, self).__init__(*args, **kwds)
        self.pid = None
        self.config = Config()
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


class GshellTabLabel(gtk.HBox):

    __gsignals__ = {
        'close-clicked': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,(gobject.TYPE_OBJECT,)),
    }

    def __init__(self, title, notebook):
        gtk.HBox.__init__(self)
        self.notebook = notebook
        self.label = EditableLabel(title)
        self.update_angle()
        self.pack_start(self.label, True, True)
        self.update_button()
        self.show_all()

    def update_button(self):
        self.button = gtk.Button()
        self.icon = gtk.Image()
        self.icon.set_from_stock(gtk.STOCK_CLOSE, gtk.ICON_SIZE_MENU)
        self.button.set_focus_on_click(False)
        self.button.set_relief(gtk.RELIEF_NONE)
        style = gtk.RcStyle()
        style.xthickness = 0
        style.ythickness = 0
        self.button.modify_style(style)
        self.button.add(self.icon)
        self.button.connect('clicked', self.on_close)
        self.button.set_name('tab-close-button')
        if hasattr(self.button, 'set_tooltip_text'):
            self.button.set_tooltip_text('Close Tab')
        self.pack_start(self.button, False, False)
        self.show_all()

    def update_angle(self):
        """Update the angle of a label"""
        position = self.notebook.get_tab_pos()
        if position == gtk.POS_LEFT:
            if hasattr(self, 'set_orientation'):
                self.set_orientation(gtk.ORIENTATION_VERTICAL)
            self.label.set_angle(90)
        elif position == gtk.POS_RIGHT:
            if hasattr(self, 'set_orientation'):
                self.set_orientation(gtk.ORIENTATION_VERTICAL)
            self.label.set_angle(270)
        else:
            if hasattr(self, 'set_orientation'):
                self.set_orientation(gtk.ORIENTATION_HORIZONTAL)
            self.label.set_angle(0)

    def on_close(self, widget, data=None):
        print 'GshellTabLabel::on_close called'
        self.emit('close-clicked', self)


class GshellNoteBook(gtk.Notebook):

    def __init__(self, widget):
        gtk.Notebook.__init__(self)
        self.widget = widget
        self.set_tab_pos(gtk.POS_TOP)
        self.set_scrollable(True)
        self.set_show_tabs(True)
        self.config = Config()
        self.show_all()

    def add_tab(self, title=None, command=None):
        print 'GshellNoteBook::add_tab called'
        self.terminal = GshellTerm()
        self.terminal.spawn_child(command)
        self.terminalbox = self.create_terminalbox()
        print "PID Terminal: %s" % self.terminal.pid
        self.page_term = self.append_page(self.terminalbox)
        if not title and not command:
            title = 'Local%s' % (int(self.page_term) + 1)
        self.label = GshellTabLabel(title + ' ', self)

        self.label.connect('close-clicked', self.close_tab)
        self.terminal.connect('child-exited', self.on_terminal_exit, self.terminalbox)
        self.set_tab_label(self.terminalbox, self.label)
        self.set_page(self.page_term)
        self.reconfigure()
        self.show_all()
        self.terminal.grab_focus()

    def close_tab(self, widget, label):
        print 'GshellNoteBook::close_tab called'
        tabnum = -1
        for i in xrange(0, self.get_n_pages() + 1):
            if label == self.get_tab_label(self.get_nth_page(i)):
                tabnum = i
                break
        if tabnum != -1:
            term = self.get_terminal_by_page(tabnum)
            if term:
                term.close()
            del(label)
            self.remove_page(tabnum)

    def get_terminal_by_page(self, tabnum):
        print 'GshellNoteBook::get_terminal_by_page called'
        tab_parent = self.get_nth_page(tabnum)
        if isinstance(tab_parent, gtk.HBox):
            for child in tab_parent.get_children():
                if isinstance(child, vte.Terminal):
                    return child
        return None

    def get_current_terminal(self):
        print 'GshellNoteBook::get_current_terminal called'
        current_page = self.get_current_page()
        return self.get_terminal_by_page(current_page)

    def get_all_terminals(self, exclude_current_page=False):
        print 'GshellNoteBook::get_all_terminals called'
        terminals = []
        current_page = self.get_current_page()
        for i in xrange(0, self.get_n_pages() + 1):
            if i == current_page and exclude_current_page:
                continue
            term = self.get_terminal_by_page(i)
            if term:
                terminals.append(term)
        return terminals

    def on_terminal_exit(self, widget, terminalbox):
        print 'GshellNoteBook::on_terminal_exit called'
        pagepos = self.page_num(terminalbox)
        if pagepos != -1:
            self.remove_page(pagepos)

    def create_terminalbox(self):
        print 'GshellNoteBook::create_terminalbox called'
        terminalbox = gtk.HBox()
        self.scrollbar = gtk.VScrollbar(self.terminal.get_adjustment())
        self.scrollbar.set_no_show_all(True)
        self.scrollbar_position = self.config['scrollbar_position']
        if self.scrollbar_position not in ('hidden', 'disabled'):
            self.scrollbar.show()

        if self.scrollbar_position == 'left':
            func = terminalbox.pack_end
        else:
            func = terminalbox.pack_start
        func(self.terminal)
        func(self.scrollbar, False)
        terminalbox.show_all()
        return terminalbox

    def on_terminal_focus_in(self, _widget, _event):
        print 'GshellNoteBook::on_terminal_focus_in called'
        self.terminal.set_colors(self.fgcolor_active, self.bgcolor,
                            self.palette_active)

    def on_terminal_focus_out(self, _widget, _event):
        print 'GshellNoteBook::on_terminal_focus_out called'
        self.terminal.set_colors(self.fgcolor_inactive, self.bgcolor,
                            self.palette_inactive)

    def reconfigure(self):
        print 'GshellNoteBook::reconfigure called'
        if hasattr(self.terminal, 'set_alternate_screen_scroll'):
            self.terminal.set_alternate_screen_scroll(self.config['alternate_screen_scroll'])
        if self.config['copy_on_selection']:
            self.terminal.connect('selection-changed', lambda widget: self.terminal.copy_clipboard())
        self.terminal.set_emulation(self.config['emulation'])
        self.terminal.set_encoding(self.config['encoding'])
        self.terminal.set_word_chars(self.config['word_chars'])
        self.terminal.set_mouse_autohide(self.config['mouse_autohide'])
        if self.config['use_system_font'] == True:
            font = self.config.get_system_font()
        else:
            font = self.config['font']
        self.terminal.set_font(pango.FontDescription(font))
        self.terminal.set_allow_bold(self.config['allow_bold'])
        if self.config['use_theme_colors']:
            self.fgcolor_active = self.terminal.get_style().text[gtk.STATE_NORMAL]
            self.bgcolor = self.terminal.get_style().base[gtk.STATE_NORMAL]
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
        self.terminal.set_colors(self.fgcolor_active, self.bgcolor, self.palette_active)
        if hasattr(self.terminal, 'set_cursor_shape'):
            self.terminal.set_cursor_shape(getattr(vte, 'CURSOR_SHAPE_%s' % self.config['cursor_shape'].upper()))

        background_type = self.config['background_type']
        if background_type == 'image' and self.config['background_image'] is not None and self.config['background_image'] != '':
            self.terminal.set_background_image_file(self.config['background_image'])
            self.terminal.set_scroll_background(self.config['scroll_background'])
        else:
            try:
                self.terminal.set_background_image(None)
            except TypeError:
                pass
            self.terminal.set_scroll_background(False)

        if background_type in ('image', 'transparent'):
            self.terminal.set_background_tint_color(gtk.gdk.color_parse(
                                               self.config['background_color']))
            opacity = int(self.config['background_darkness'] * 65536)
            saturation = 1.0 - float(self.config['background_darkness'])
            self.terminal.set_background_saturation(saturation)
        else:
            opacity = 65535
            self.terminal.set_background_saturation(1)

        if self.terminal.composite_support:
            self.terminal.set_opacity(opacity)
        if not self.terminal.composite_support or self.config['disable_real_transparency']:
            background_transparent = True
        else:
            if self.terminal.is_composited() == False:
                background_transparent = True
            else:
                background_transparent = False
        if self.config['background_type'] == 'transparent':
            self.terminal.set_background_transparent(background_transparent)
        else:
            self.terminal.set_background_transparent(False)

        if hasattr(vte, 'VVVVTE_CURSOR_BLINK_ON'):
            if self.config['cursor_blink'] == True:
                self.terminal.set_cursor_blink_mode('VTE_CURSOR_BLINK_ON')
            else:
                self.terminal.set_cursor_blink_mode('VTE_CURSOR_BLINK_OFF')
        else:
            self.terminal.set_cursor_blinks(self.config['cursor_blink'])

        if self.config['scrollback_infinite'] == True:
            scrollback_lines = -1
        else:
            scrollback_lines = self.config['scrollback_lines']
        self.terminal.set_scrollback_lines(scrollback_lines)
        self.terminal.set_scroll_on_keystroke(self.config['scroll_on_keystroke'])
        self.terminal.set_scroll_on_output(self.config['scroll_on_output'])

        self.terminal.connect('focus-in-event', self.on_terminal_focus_in)
        self.terminal.connect('focus-out-event', self.on_terminal_focus_out)

        self.terminal.queue_draw()

class GshellKeyBinder(object):

    def __init__(self, main):
        super(GshellKeyBinder, self).__init__()
        self.main = main
        self.window = self.main.window
        self.config = Config()
        self.keybinder = self.config['keybinder']
        self.accel_group = None
        self.reload_accelerators()

    def reload_accelerators(self):
        if self.accel_group:
            self.window.remove_accel_group(self.accel_group)
        self.accel_group = gtk.AccelGroup()
        self.window.add_accel_group(self.accel_group)
        self.load_accelerators()

    def load_accelerators(self):
        for action, keys in self.keybinder.iteritems():
            param = None
            if isinstance(action, tuple):
                action, param = action
            if not isinstance(keys, list):
                keys = [keys]
            for key in keys:
                g_key, mask = gtk.accelerator_parse(key)
                if g_key > 0:
                    if hasattr(self.main, action):
                        if param:
                            func = getattr(self.main, action)(param)
                        else:
                            func = getattr(self.main, action)
                        self.accel_group.connect_group(g_key, mask, gtk.ACCEL_VISIBLE, func)

class MainWindow(object):

    def __init__(self):
        super(MainWindow, self).__init__()
        gtk_settings = gtk.settings_get_default()
        gtk_settings.props.gtk_menu_bar_accel = None

    def build_window(self):
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_full_screen = False
        self.window.set_size_request(1200, 860)
        self.window.set_title("Gshell")
        self.window.set_position(gtk.WIN_POS_CENTER)
        self.window.connect("delete_event", self.main_window_destroy)
        self.window.connect("key-press-event",self._key_press_event)
        self.vbox_main = gtk.VBox()
        self.window.add(self.vbox_main)

        """ 
        Menu
        """
        self.menu = self.build_menu()
        self.vbox_main.pack_start(self.menu, False, False, 0)

        """
        ToolBar
        """
        self.toolbar = self.build_toolbar()
        self.vbox_main.pack_start(self.toolbar, False, False, 0)

        """
           Connection String
        """
        self.toolbar_conn = gtk.Toolbar()
        self.toolbar_conn.set_orientation(gtk.ORIENTATION_HORIZONTAL)
        self.toolbar_conn.set_style(gtk.TOOLBAR_ICONS)
        self.conn_string = gtk.Entry()
        self.conn_string.set_size_request(350, 25)
        self.conn_string.set_editable(True)
        icon_connect = gtk.Image()
        icon_connect.set_from_stock(gtk.STOCK_CONNECT, 4)
        self.toolbar_conn.append_widget(self.conn_string, None, None)
        self.toolbar_conn.append_item("Connect", "Connect", "Connect", icon_connect, self.menuitem_response)
        self.vbox_main.pack_start(self.toolbar_conn, False, False, 0)


        """
        Notebook
        """
        self.notebook = GshellNoteBook(self.vbox_main)
        self.vbox_main.pack_start(self.notebook, True, True, 0)

        #self.statusbar = gtk.Statusbar()
        #self.vbox_main.pack_start(self.statusbar, True, True, 0)
        keybinder = GshellKeyBinder(self)
        self.notebook.add_tab()
        self.window.show_all()


    def _key_press_event(self, widget, event):
        keyval = event.keyval
        keyval_name = gtk.gdk.keyval_name(keyval)
        state = event.state
        ctrl = (state & gtk.gdk.CONTROL_MASK)
        shift = (state & gtk.gdk.SHIFT_MASK)
        print 'State %s' % state
        print 'Keyval %s' % keyval_name
        return False

    def main_window_destroy(self, *args):
        gtk.main_quit(*args)

    def menuitem_response(self, widget, data=None):
        print 'Click menu %s' % widget

    def menu_select_all(self, widget, data=None):
        terminal = self.notebook.get_current_terminal()
        if terminal:
            terminal.select_all()

    def menu_copy(self, widget, data=None):
        terminal = self.notebook.get_current_terminal()
        if terminal:
            terminal.copy_clipboard()

    def menu_paste(self, widget, data=None):
        terminal = self.notebook.get_current_terminal()
        if terminal:
            terminal.paste_clipboard()

    def menu_close_tab(self, widget, data=None):
        terminals = []
        if data == 'current':
            terminals.append(self.notebook.get_current_terminal())
        if data == 'other':
            terminals += self.notebook.get_all_terminals(exclude_current_page=True)
        if data == 'all':
            terminals += self.notebook.get_all_terminals()
        for terminal in terminals:
            terminal.close()

    def menu_zoom_tab(self, widget, data=None):
        terminal = self.notebook.get_current_terminal()
        if hasattr(terminal, data):
            func = getattr(terminal, data)
            func()

    def key_zoom(self, zoom):
        def callback(*args):
            self.menu_zoom_tab(self, zoom)
            return True
        return callback

    def key_close_term(self, *args):
        terminal = self.notebook.get_current_terminal()
        terminal.close()
        return True

    def key_new_tab(self, *args):
        self.notebook.add_tab()
        return True

    def key_full_screen(self, *args):
        self.window.set_full_screen = not self.window.set_full_screen
        if self.window.set_full_screen:
            self.window.fullscreen()
        else:
            self.window.unfullscreen()
        return True

    def key_next_tab(self, *args):
        self.notebook.next_page()
        return True

    def key_prev_tab(self, *args):
        self.notebook.prev_page()
        return True

    def key_copy(self, *args):
        self.menu_copy(self)
        return True

    def key_paste(self, *args):
        self.menu_paste(self)
        return True

    def on_new_terminal(self, widget, data=None):
        self.notebook.add_tab()

    def build_toolbar(self):
        toolbar = gtk.Toolbar()
        toolbar.set_orientation(gtk.ORIENTATION_HORIZONTAL)
        toolbar.set_style(gtk.TOOLBAR_ICONS)

        icon_new = gtk.Image()
        icon_new.set_from_stock(gtk.STOCK_NEW, 4)
        toolbar.append_item("New", "New", "New", icon_new, self.on_new_terminal)

        icon_open = gtk.Image()
        icon_open.set_from_stock(gtk.STOCK_OPEN, 4)
        toolbar.append_item("Open", "Open", "Open", icon_open, self.menuitem_response)

        toolbar.append_widget(gtk.SeparatorToolItem(), None, None)

        icon_prop = gtk.Image()
        icon_prop.set_from_stock(gtk.STOCK_PROPERTIES, 4)
        toolbar.append_item("Properties", "Properties", "Properties", icon_prop, self.menuitem_response)

        toolbar.append_widget(gtk.SeparatorToolItem(), None, None)

        icon_copy = gtk.Image()
        icon_copy.set_from_stock(gtk.STOCK_COPY, 4)
        toolbar.append_item("Copy", "Copy", "Copy", icon_copy, self.menu_copy)

        icon_paste = gtk.Image()
        icon_paste.set_from_stock(gtk.STOCK_PASTE, 4)
        toolbar.append_item("Paste", "Paste", "Paste", icon_paste, self.menu_paste)

        icon_find = gtk.Image()
        icon_find.set_from_stock(gtk.STOCK_FIND, 4)
        toolbar.append_item("Search", "Search", "Search", icon_find, self.menuitem_response)

        toolbar.append_widget(gtk.SeparatorToolItem(), None, None)

        icon_zoom_in = gtk.Image()
        icon_zoom_in.set_from_stock(gtk.STOCK_ZOOM_IN, 4)
        toolbar.append_item("Zoom In", "Zoom In", "Zoom In", icon_zoom_in, self.menu_zoom_tab, 'zoom_in')

        icon_zoom_out = gtk.Image()
        icon_zoom_out.set_from_stock(gtk.STOCK_ZOOM_OUT, 4)
        toolbar.append_item("Zoom Out", "Zoom Out", "Zoom Out", icon_zoom_out, self.menu_zoom_tab, 'zoom_out')

        icon_zoom_orig = gtk.Image()
        icon_zoom_orig.set_from_stock(gtk.STOCK_ZOOM_100, 4)
        toolbar.append_item("Zoom Default", "Zoom Default", "Zoom Default", icon_zoom_orig, self.menu_zoom_tab, 'zoom_orig')

        toolbar.append_widget(gtk.SeparatorToolItem(), None, None)

        icon_new_group = gtk.Image()
        icon_new_group.set_from_stock(gtk.STOCK_DIRECTORY, 4)
        toolbar.append_item("New Tab Group", "New Tab Group", "New Tab Group", icon_new_group, self.menuitem_response)

        icon_arragne = gtk.Image()
        icon_arragne.set_from_stock(gtk.STOCK_ADD, 4)
        toolbar.append_item("Tab Arrange", "Tab Arrange", "Tab Arrange", icon_arragne, self.menuitem_response)

        toolbar.append_widget(gtk.SeparatorToolItem(), None, None)
        return toolbar

    def build_menu(self):
        menus = OrderedDict()
        menus['File'] = (
        {
            'name' : 'New',
            'action' : self.on_new_terminal,
            'data' : None,
            'icon' : gtk.STOCK_NEW,
            'position' : 0,
            'group' : 1,
            'children' : None,
        },
        {
            'name' : 'Open',
            'action' : self.menuitem_response,
            'data' : None,
            'icon' : gtk.STOCK_OPEN,
            'position' : 1,
            'group' : 1,
            'children' : None,
        },
        {
            'name' : 'Save as',
            'action' : self.menuitem_response,
            'data' : None,
            'icon' : gtk.STOCK_SAVE_AS,
            'position' : 2,
            'group' : 1,
            'children' : None,
        },
        {
            'name' : 'Log',
            'action' : None,
            'data' : None,
            'icon' : None,
            'position' : 0,
            'group' : 2,
            'children' : (
                {
                    'name' : 'Start',
                    'action' : self.menuitem_response,
                    'data' : None,
                    'icon' : None,
                    'group' : 1,
                    'position' : 0,
                    'children' : None,
                },
                {
                    'name' : 'Stop',
                    'action' : self.menuitem_response,
                    'data' : None,
                    'icon' : None,
                    'group' : 1,
                    'position' : 1,
                    'children' : None,
                },
            ) 
        },
        {
            'name' : 'Exit',
            'action' : self.main_window_destroy,
            'data' : None,
            'icon' : gtk.STOCK_QUIT,
            'position' : 0,
            'group' : 3,
            'children' : None,
        })

        menus['Edit'] = (
        {
            'name' : 'Copy',
            'action' : self.menu_copy,
            'data' : None,
            'icon' : gtk.STOCK_COPY,
            'position' : 0,
            'group' : 1,
            'children' : None
        },
        { 
           'name' : 'Paste',
            'action' : self.menu_paste,
            'data' : None,
            'icon' : gtk.STOCK_PASTE,
            'position' : 1,
            'group' : 1,
            'children' : None
        },
        {
            'name' : 'Select All',
            'action' : self.menu_select_all,
            'data' : None,
            'icon' : gtk.STOCK_SELECT_ALL,
            'position' : 0,
            'group' : 2,
            'children' : None
        })

        menus['Tab'] = (
        {
            'name' : 'New Tab',
            'action' : self.on_new_terminal,
            'data' : None,
            'icon' : None,
            'position' : 0,
            'group' : 1,
            'children' : None
        },
        { 
           'name' : 'New Tab Group',
            'action' : self.menuitem_response,
            'data' : None,
            'icon' : None,
            'position' : 1,
            'group' : 1,
            'children' : None
        },
        {
            'name' : 'Arrange',
            'action' : self.menuitem_response,
            'data' : None,
            'icon' : None,
            'position' : 2,
            'group' : 1,
            'children' : (
                {
                    'name' : 'Arrange Vertical',
                    'action' : self.menuitem_response,
                    'data' : None,
                    'icon' : None,
                    'group' : 1,
                    'position' : 0,
                    'children' : None,
                },
                {
                    'name' : 'Arrange Horizontal',
                    'action' : self.menuitem_response,
                    'data' : None,
                    'icon' : None,
                    'group' : 1,
                    'position' : 1,
                    'children' : None,
                },
                {
                    'name' : 'Arrange Tiled',
                    'action' : self.menuitem_response,
                    'data' : None,
                    'icon' : None,
                    'group' : 1,
                    'position' : 2,
                    'children' : None,
                },
                {
                    'name' : 'Merge All Tab Groups',
                    'action' : self.menuitem_response,
                    'data' : None,
                    'icon' : None,
                    'group' : 2,
                    'position' : 0,
                    'children' : None,
                },

            )
        },
        {
            'name' : 'Close',
            'action' : self.menu_close_tab,
            'data' : 'current',
            'icon' : None,
            'position' : 0,
            'group' : 2,
            'children' : None
        },
        {
            'name' : 'Close Other Tabs',
            'action' : self.menu_close_tab,
            'data' : 'other',
            'icon' : None,
            'position' : 1,
            'group' : 2,
            'children' : None
        },
        {
            'name' : 'Close All Tabs',
            'action' : self.menu_close_tab,
            'data' : 'all',
            'icon' : None,
            'position' : 2,
            'group' : 2,
            'children' : None
        },
       {
            'name' : 'Zoom In',
            'action' : self.menu_zoom_tab,
            'data' : 'zoom_in',
            'icon' : gtk.STOCK_ZOOM_IN,
            'position' : 0,
            'group' : 3,
            'children' : None
        },
        {
            'name' : 'Zoom Out',
            'action' : self.menu_zoom_tab,
            'data' : 'zoom_out',
            'icon' : gtk.STOCK_ZOOM_OUT,
            'position' : 1,
            'group' : 3,
            'children' : None
        },
        {
            'name' : 'Zoom Default',
            'action' : self.menu_zoom_tab,
            'data' : 'zoom_orig',
            'icon' : gtk.STOCK_ZOOM_100,
            'position' : 2,
            'group' : 3,
            'children' : None
        })

        menus['Tools'] = (
        {
            'name' : 'Scripts',
            'action' : self.menuitem_response,
            'data' : None,
            'icon' : None,
            'position' : 0,
            'group' : 1,
            'children' : None
        },
        {
            'name' : 'Options',
            'action' : self.menuitem_response,
            'data' : None,
            'icon' : gtk.STOCK_PREFERENCES,
            'position' : 0,
            'group' : 2,
            'children' : None
        },
        )

        menus['Help'] = (
        {
            'name' : 'Help',
            'action' : self.menuitem_response,
            'data' : None,
            'icon' : gtk.STOCK_HELP,
            'position' : 0,
            'group' : 1,
            'children' : None
        },
        {
            'name' : 'About',
            'action' : self.menuitem_response,
            'data' : None,
            'icon' : gtk.STOCK_ABOUT,
            'position' : 0,
            'group' : 2,
            'children' : None
        })

        menu_bar = gtk.MenuBar()
        for main_menu, submenus in menus.iteritems():
            main_menu_item = gtk.MenuItem(main_menu)
            menu = gtk.Menu()
            self.grouped_menu(menu, submenus)
            main_menu_item.set_submenu(menu)
            menu_bar.append(main_menu_item)
        return menu_bar

    def grouped_menu(self, parent, params):
        if type(params) == dict:
            params = [params]
        sorted_menu = sorted(params, key=lambda x:x['group'])
        menu_groups = [tuple(menus) for group, menus in groupby(sorted_menu, lambda x: x['group'])]
        for menus in menu_groups:
            for menu in sorted(menus, key=lambda x: x['position']):
                if menu['icon']:
                    menu_item = gtk.ImageMenuItem(menu['icon'])
                    menu_item.get_children()[0].set_label(menu['name'])
                else:
                    menu_item = gtk.MenuItem(menu['name'])
                if menu['action']:
                    menu_item.connect("activate", menu['action'], menu['data'])
                if menu['children']:
                    children_sub = gtk.Menu()
                    self.grouped_menu(children_sub, menu['children'])
                    menu_item.set_submenu(children_sub)
                parent.add(menu_item)
            if len(menu_groups) > 1 and menus != menu_groups[-1]:
                separator = gtk.SeparatorMenuItem()
                parent.add(separator)


if __name__ == '__main__':
    main_window = MainWindow()
    main_window.build_window()
    gtk.main()
