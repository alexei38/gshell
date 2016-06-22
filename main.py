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
from thread import start_new_thread
from time import sleep


class GshellTerm(vte.Terminal):

    def __init__(self, *args, **kwds):
        super(GshellTerm, self).__init__(*args, **kwds)
        self.pid = None
        self.config = Config()
        self.show_all()
        if not hasattr(self, "set_opacity") or not hasattr(self, "is_composited"):
            self.composite_support = False
        else:
            self.composite_support = True

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


class GshellTabLabel(gtk.HBox):

    __gsignals__ = {
            'close-clicked': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                (gobject.TYPE_OBJECT,)),
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
        self.icon.set_from_stock(gtk.STOCK_CLOSE,
                                 gtk.ICON_SIZE_MENU)
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
        if not title:
            title = 'Unnamed'

        self.label = GshellTabLabel(title, self)
        self.label.connect('close-clicked', self.close_tab)

        self.terminal = GshellTerm()
        self.terminal.spawn_child(command)
        self.terminal.connect('child-exited', self.on_terminal_exit)

        print "PID Terminal: %s" % self.terminal.pid
        self.page_term = self.append_page(self.terminal)
        self.set_tab_label(self.terminal, self.label)
        self.set_page(self.page_term)
        self.reconfigure()
        self.show_all()

    def close_tab(self, widget, label):
        print 'GshellNoteBook::close_tab called'
        tabnum = None
        nb = widget.notebook
        for i in xrange(0, nb.get_n_pages() + 1):
            if label == nb.get_tab_label(nb.get_nth_page(i)):
                tabnum = i
                break
        child = nb.get_nth_page(tabnum)
        if isinstance(child, vte.Terminal):
            child.close()
            del(label)
        nb.remove_page(tabnum)

    def on_terminal_exit(self, widget, data=None):
        print 'GshellNoteBook::on_terminal_exit called'
        pagepos = self.page_num(widget)
        self.remove_page(pagepos)

    def reconfigure(self):
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

        # This is quite hairy, but the basic explanation is that we should
        # set_background_transparent(True) when we have no compositing and want
        # fake background transparency, otherwise it should be False.
        if not self.terminal.composite_support or self.config['disable_real_transparency']:
            # We have no compositing support, fake background only
            background_transparent = True
        else:
            if self.terminal.is_composited() == False:
                # We have compositing and it's enabled. no fake background.
                background_transparent = True
            else:
                # We have compositing, but it's not enabled. fake background
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
        self.terminal.queue_draw()


class MainWindow(object):

    def __init__(self):
        super(MainWindow, self).__init__()
        gtk_settings = gtk.settings_get_default()
        gtk_settings.props.gtk_menu_bar_accel = None

    def build_window(self):
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_size_request(1200, 860)
        self.window.set_title("Gshell")
        self.window.set_position(gtk.WIN_POS_CENTER)
        self.window.connect("delete_event", self.main_window_destroy)
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
        toolbar_conn = gtk.Toolbar()
        toolbar_conn.set_orientation(gtk.ORIENTATION_HORIZONTAL)
        toolbar_conn.set_style(gtk.TOOLBAR_ICONS)
        self.conn_string = gtk.Entry()
        self.conn_string.set_size_request(350, 25)
        self.conn_string.set_editable(True)
        icon_disconnect = gtk.Image()
        icon_disconnect.set_from_stock(gtk.STOCK_CONNECT, 4)
        toolbar_conn.append_widget(self.conn_string, None, None)
        toolbar_conn.append_item("Connect", "Connect", "Connect", icon_disconnect, self.menuitem_response)
        self.vbox_main.pack_start(toolbar_conn, False, False, 0)


        """
        Notebook
        """
        self.notebook = GshellNoteBook(self.vbox_main)
        self.notebook.add_tab(title='Local')
        self.vbox_main.pack_start(self.notebook, True, True, 0)

        #self.statusbar = gtk.Statusbar()
        #self.vbox_main.pack_start(self.statusbar, True, True, 0)
        self.window.show_all()

    def main_window_destroy(self, *args):
        gtk.main_quit(*args)

    def menuitem_response(self, widget, data=None):
        print 'Click menu %s' % widget

    def on_new_terminal(self, widget, data=None):
        self.notebook.add_tab(title='Local')

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

        icon_disconnect = gtk.Image()
        icon_disconnect.set_from_stock(gtk.STOCK_DISCONNECT, 4)
        toolbar.append_item("Disconnect", "Disconnect", "Disconnect", icon_disconnect, self.menuitem_response)

        icon_connect = gtk.Image()
        icon_connect.set_from_stock(gtk.STOCK_CONNECT, 4)
        toolbar.append_item("Recconnect", "Recconnect", "Recconnect", icon_connect, self.menuitem_response)

        toolbar.append_widget(gtk.SeparatorToolItem(), None, None)

        icon_prop = gtk.Image()
        icon_prop.set_from_stock(gtk.STOCK_PROPERTIES, 4)
        toolbar.append_item("Properties", "Properties", "Properties", icon_prop, self.menuitem_response)

        toolbar.append_widget(gtk.SeparatorToolItem(), None, None)

        icon_copy = gtk.Image()
        icon_copy.set_from_stock(gtk.STOCK_COPY, 4)
        toolbar.append_item("Copy", "Copy", "Copy", icon_copy, self.menuitem_response)

        icon_paste = gtk.Image()
        icon_paste.set_from_stock(gtk.STOCK_PASTE, 4)
        toolbar.append_item("Paste", "Paste", "Paste", icon_paste, self.menuitem_response)

        icon_find = gtk.Image()
        icon_find.set_from_stock(gtk.STOCK_FIND, 4)
        toolbar.append_item("Search", "Search", "Search", icon_find, self.menuitem_response)

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
            'action' : self.menuitem_response,
            'position' : 0,
            'group' : 1,
            'children' : None,
        },
        {
            'name' : 'Open',
            'action' : self.menuitem_response,
            'position' : 1,
            'group' : 1,
            'children' : None,
        },
        {
            'name' : 'Save as',
            'action' : self.menuitem_response,
            'position' : 2,
            'group' : 1,
            'children' : None,
        },
        {
            'name' : 'Log',
            'action' : None,
            'position' : 0,
            'group' : 2,
            'children' : (
                {
                    'name' : 'Start',
                    'action' : self.menuitem_response,
                    'group' : 1,
                    'position' : 0,
                    'children' : None,
                },
                {
                    'name' : 'Stop',
                    'action' : self.menuitem_response,
                    'group' : 1,
                    'position' : 1,
                    'children' : None,
                },
            ) 
        },
        {
            'name' : 'Exit',
            'action' : self.menuitem_response,
            'position' : 0,
            'group' : 3,
            'children' : None,
        })

        menus['Edit'] = (
        {
            'name' : 'Copy',
            'action' : self.menuitem_response,
            'position' : 0,
            'group' : 1,
            'children' : None
        },
        { 
           'name' : 'Paste',
            'action' : self.menuitem_response,
            'position' : 1,
            'group' : 1,
            'children' : None
        },
        {
            'name' : 'Select All',
            'action' : self.menuitem_response,
            'position' : 0,
            'group' : 2,
            'children' : None
        },
        {
            'name' : 'Select Screen',
            'action' : self.menuitem_response,
            'position' : 0,
            'group' : 2,
            'children' : None
        })

        menus['Tab'] = (
        {
            'name' : 'New Tab',
            'action' : self.menuitem_response,
            'position' : 0,
            'group' : 1,
            'children' : None
        },
        { 
           'name' : 'New Tab Group',
            'action' : self.menuitem_response,
            'position' : 1,
            'group' : 1,
            'children' : None
        },
        {
            'name' : 'Arrange',
            'action' : self.menuitem_response,
            'position' : 2,
            'group' : 1,
            'children' : (
                {
                    'name' : 'Arrange Vertical',
                    'action' : self.menuitem_response,
                    'group' : 1,
                    'position' : 0,
                    'children' : None,
                },
                {
                    'name' : 'Arrange Horizontal',
                    'action' : self.menuitem_response,
                    'group' : 1,
                    'position' : 1,
                    'children' : None,
                },
                {
                    'name' : 'Arrange Tiled',
                    'action' : self.menuitem_response,
                    'group' : 1,
                    'position' : 2,
                    'children' : None,
                },
                {
                    'name' : 'Merge All Tab Groups',
                    'action' : self.menuitem_response,
                    'group' : 2,
                    'position' : 0,
                    'children' : None,
                },

            )
        },
        {
            'name' : 'Close',
            'action' : self.menuitem_response,
            'position' : 0,
            'group' : 2,
            'children' : None
        },
        {
            'name' : 'Close Other Tabs',
            'action' : self.menuitem_response,
            'position' : 1,
            'group' : 2,
            'children' : None
        },
        {
            'name' : 'Close All Tabs',
            'action' : self.menuitem_response,
            'position' : 2,
            'group' : 2,
            'children' : None
        },
        {
            'name' : 'Rename',
            'action' : self.menuitem_response,
            'position' : 0,
            'group' : 3,
            'children' : None
        },
        {
            'name' : 'Set Color',
            'action' : self.menuitem_response,
            'position' : 3,
            'group' : 4,
            'children' : (
                {
                    'name' : 'Default',
                    'action' : self.menuitem_response,
                    'group' : 1,
                    'position' : 0,
                    'children' : None,
                },
                {
                    'name' : 'Red',
                    'action' : self.menuitem_response,
                    'group' : 2,
                    'position' : 0,
                    'children' : None,
                },
                {
                    'name' : 'Yellow',
                    'action' : self.menuitem_response,
                    'group' : 2,
                    'position' : 1,
                    'children' : None,
                },
                {
                    'name' : 'Pink',
                    'action' : self.menuitem_response,
                    'group' : 2,
                    'position' : 2,
                    'children' : None,
                },
            )
        })

        menus['Tools'] = (
        {
            'name' : 'Scripts',
            'action' : self.menuitem_response,
            'position' : 0,
            'group' : 1,
            'children' : None
        },
        {
            'name' : 'Options',
            'action' : self.menuitem_response,
            'position' : 0,
            'group' : 2,
            'children' : None
        },
        )

        menus['Help'] = (
        {
            'name' : 'Help',
            'action' : self.menuitem_response,
            'position' : 0,
            'group' : 1,
            'children' : None
        },
        {
            'name' : 'About',
            'action' : self.menuitem_response,
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
                menu_item = gtk.MenuItem(menu['name'])
                if menu['action']:
                    menu_item.connect("activate", menu['action'])
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
