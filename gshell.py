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

class Gshell(object):

    def __init__(self):
        super(Gshell, self).__init__()
        gtk_settings = gtk.settings_get_default()
        gtk_settings.props.gtk_menu_bar_accel = None
        self.config = Config()
        self.current_pid = os.getpid()
        self.build_window()

    def build_window(self):
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_full_screen = False
        self.window.set_size_request(1200, 860)
        self.window.set_title("Gshell")
        self.window.set_position(gtk.WIN_POS_CENTER)
        self.window.connect("delete_event", self.gshell_destroy)
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
        Notebook
        """
        self.notebook = GshellNoteBook(self)
        self.vbox_main.pack_start(self.notebook, True, True, 0)

        #self.statusbar = gtk.Statusbar()
        #self.vbox_main.pack_start(self.statusbar, True, True, 0)
        keybinder = GshellKeyBinder(self)
        self.notebook.add_tab()
        self.window.show_all()

    def gshell_destroy(self, *args):
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

    def menu_log(self, widget, action):
        terminal = self.notebook.get_current_terminal()
        if terminal:
            if terminal.logger.logging and action == 'stop':
                terminal.logger.stop_logger()
            if not terminal.logger.logging and action == 'start':
                if terminal.host:
                    terminal.logger.start_logger(terminal.host['log'])
                else:
                    terminal.logger.start_logger()
            self.change_menu_sensitive(self.menu, ['Start'], not terminal.logger.logging)
            self.change_menu_sensitive(self.menu, ['Stop'], terminal.logger.logging)

    def menu_reconnect_tab(self, *args):
        terminal = self.notebook.get_current_terminal()
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

    def menu_search(self, *args):
        terminal = self.notebook.get_current_terminal()
        if terminal:
            if terminal.search.flags() & gtk.VISIBLE:
                terminal.search.hide()
                terminal = self.notebook.get_current_terminal()
                terminal.grab_focus()
            else:
                terminal.search.show()
                terminal.search.entry.grab_focus()

    def key_zoom(self, zoom):
        def callback(*args):
            self.menu_zoom_tab(self, zoom)
            return True
        return callback

    def key_close_term(self, accel_group, widget, key, mask):
        terminal = self.notebook.get_current_terminal()
        if terminal:
            key_d, mask_d = gtk.accelerator_parse('<ctrl>d')
            if key == key_d and mask == mask_d and (terminal.terminal_active or not terminal.host):
                return False
            if not terminal.terminal_active:
                page_num = self.notebook.get_current_page()
                page = self.notebook.get_nth_page(page_num)
                self.notebook.remove(page)
            terminal.close()
            self.switch_toolbar_sensitive()
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

    def new_terminal(self, *args):
        self.notebook.add_tab()
        return True

    def switch_toolbar_sensitive(self, terminal=None, *args):
        if not terminal:
            terminal = self.notebook.get_current_terminal()
        if terminal:
            self.change_menu_sensitive(self.menu, ['Start'], not terminal.logger.logging)
            self.change_menu_sensitive(self.menu, ['Stop'], terminal.logger.logging)
            if terminal.host:
                self.toolbar.reconnect_button.set_sensitive(not terminal.terminal_active)
                self.toolbar.disconnect_button.set_sensitive(terminal.terminal_active)
            else:
                self.toolbar.reconnect_button.set_sensitive(False)
                self.toolbar.disconnect_button.set_sensitive(False)
            self.toolbar.copy_button.set_sensitive(True)
            self.toolbar.paste_button.set_sensitive(True)
            self.toolbar.search_button.set_sensitive(True)
            self.toolbar.zoom_in_button.set_sensitive(True)
            self.toolbar.zoom_out_button.set_sensitive(True)
            self.toolbar.zoom_orig_button.set_sensitive(True)
        else:
            self.toolbar.reconnect_button.set_sensitive(False)
            self.toolbar.disconnect_button.set_sensitive(False)
            self.toolbar.copy_button.set_sensitive(False)
            self.toolbar.paste_button.set_sensitive(False)
            self.toolbar.search_button.set_sensitive(False)
            self.toolbar.zoom_in_button.set_sensitive(False)
            self.toolbar.zoom_out_button.set_sensitive(False)
            self.toolbar.zoom_orig_button.set_sensitive(False)
            self.change_menu_sensitive(self.menu, ['Start', 'Stop'], False)
        self.switch_menu_sensitive(terminal)

    def switch_menu_sensitive(self, terminal=None, *args):
        names = [
            'Log',
            'Edit',
            'New Tab Group',
            'Arrange',
            'Close',
            'Close All Tabs',
            'Close Other Tabs',
            'Zoom In',
            'Zoom Out',
            'Zoom Default',
        ]
        self.change_menu_sensitive(self.menu, names, bool(terminal))

    def change_menu_sensitive(self, menu_item, names, sensitive):
        menu = None
        if isinstance(menu_item, gtk.MenuItem) or isinstance(menu_item, gtk.ImageMenuItem):
            menu = menu_item.get_submenu()
        elif isinstance(menu_item, gtk.Menu) or isinstance(menu_item, gtk.MenuBar):
            menu = menu_item
        else:
            return None
        if menu:
            for child in menu.get_children():
                label = None
                if isinstance(child, gtk.SeparatorMenuItem):
                    continue
                if isinstance(child, gtk.MenuItem):
                    label = child.get_label()
                if isinstance(child, gtk.ImageMenuItem):
                    label = child.get_child().get_text()
                if label in names:
                    child.set_sensitive(sensitive)
                else:
                    self.change_menu_sensitive(child, names, sensitive)

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
    Gshell()
    gtk.main()
