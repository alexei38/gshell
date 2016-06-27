#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import gtk
from config import Config
from menu import GshellMenu
from about import AboutDialog
from urlparse import urlparse
from toolbar import GshellToolbar
from managehost import ManageHost
from notebook import GshellNoteBook

class MainWindow(object):

    def __init__(self):
        super(MainWindow, self).__init__()
        gtk_settings = gtk.settings_get_default()
        gtk_settings.props.gtk_menu_bar_accel = None
        self.config = Config()
        self.current_pid = os.getpid()

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
        self.menu = GshellMenu(self)
        self.vbox_main.pack_start(self.menu, False, False, 0)

        """
        ToolBar
        """
        self.toolbar = GshellToolbar(self)
        self.vbox_main.pack_start(self.toolbar, False, False, 0)

        """
           Connection String
        """
        self.toolbar_conn = gtk.Toolbar()
        self.toolbar_conn.set_orientation(gtk.ORIENTATION_HORIZONTAL)
        self.toolbar_conn.set_style(gtk.TOOLBAR_ICONS)
        self.conn_string = gtk.Entry()
        self.conn_string.set_text('ssh://')
        self.conn_string.set_size_request(350, 25)
        self.conn_string.set_editable(True)
        self.conn_string.connect('key-press-event', self.on_return_conn_string)
        icon_connect = gtk.Image()
        icon_connect.set_from_stock(gtk.STOCK_CONNECT, 4)
        self.toolbar_conn.append_widget(self.conn_string, None, None)
        self.toolbar_conn.append_item("Connect", "Connect", "Connect", icon_connect, self.menu_connect_from_string, self.conn_string)
        self.vbox_main.pack_start(self.toolbar_conn, False, False, 0)

        """
        Notebook
        """
        self.notebook = GshellNoteBook(self)
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
        terminals = self.notebook.get_all_terminals()
        if len(terminals) > 0:
            dialog = gtk.MessageDialog(self.window, gtk.DIALOG_MODAL,
                                       gtk.MESSAGE_INFO, gtk.BUTTONS_YES_NO,
                                       "There are open terminals.\nAre you sure you want to quit?")
            dialog.set_title("Are you sure you want to quit?")
            response = dialog.run()
            dialog.destroy()
            if response == gtk.RESPONSE_YES:
                gtk.main_quit(*args)
                return False
            else:
                return True
        else:
            gtk.main_quit(*args)
            return False

    def menuitem_response(self, widget, data=None):
        print 'Click menu %s' % widget

    def menu_reconnect_tab(self, *args):
        terminal = self.notebook.get_current_terminal()
        print terminal
        if terminal and terminal.host:
            self.notebook.new_tab_by_host(host=terminal.host, terminal=terminal)

    def menu_disconnect_tab(self, *args):
        terminal = self.notebook.get_current_terminal()
        if terminal:
            terminal.close()

    def menu_select_all(self, *args):
        terminal = self.notebook.get_current_terminal()
        if terminal:
            terminal.select_all()
        return True

    def menu_copy(self, *args):
        terminal = self.notebook.get_current_terminal()
        if terminal:
            terminal.copy_clipboard()
        return True

    def menu_paste(self, *args):
        terminal = self.notebook.get_current_terminal()
        if terminal:
            terminal.paste_clipboard()
        return True

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

    def menu_open(self, *args):
        ManageHost(self)
        return True

    def menu_about(self, *args):
        AboutDialog()

    def key_zoom(self, zoom):
        def callback(*args):
            self.menu_zoom_tab(self, zoom)
            return True
        return callback

    def key_close_term(self, accel_group, widget, key, mask):
        terminal = self.notebook.get_current_terminal()
        if terminal:
            key_d, mask_d = gtk.accelerator_parse('<ctrl>d')
            if key == key_d and mask == mask_d and terminal.terminal_active:
                return False
            if not terminal.terminal_active:
                page_num = self.notebook.get_current_page()
                page = self.notebook.get_nth_page(page_num)
                self.notebook.remove(page)
            terminal.close()
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

    def on_return_conn_string(self, widget, event):
        if event.keyval in [gtk.keysyms.Return, gtk.keysyms.KP_Enter]:
            self.connect_from_string(widget)
            return True
        return False

    def menu_connect_from_string(self, widget, conn_string):
        return self.connect_from_string(conn_string)

    def connect_from_string(self, widget):
        if not isinstance(widget, gtk.Entry):
            return False
        text = widget.get_text()
        parse = urlparse(text)
        if parse.scheme == 'ssh' and parse.hostname:
            cmd = 'ssh %s' % parse.hostname
            if parse.username:
                cmd += ' -l %s' % parse.username
            port = parse.port or '22'
            cmd += ' -p %s' % port
            terminal = self.notebook.add_tab(title=parse.hostname)
            terminal.feed_child(cmd + '\r')
        else:
            terminal = self.notebook.add_tab()
            terminal.feed_child(text + '\r')
        widget.set_text('ssh://')

    def new_terminal(self, *args):
        self.notebook.add_tab()
        return True

class GshellKeyBinder(object):

    def __init__(self, main):
        super(GshellKeyBinder, self).__init__()
        self.main = main
        self.window = self.main.window
        self.config = self.main.config
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


if __name__ == '__main__':
    main_window = MainWindow()
    main_window.build_window()
    gtk.main()
