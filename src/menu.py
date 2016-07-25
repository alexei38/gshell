# -*- coding: utf-8 -*-

import gtk
from itertools import groupby
from collections import OrderedDict

class GshellMenu(gtk.MenuBar):
    def __init__(self, gshell):
        super(GshellMenu, self).__init__()
        self.gshell = gshell
        self.menu = self.build_menu()

    def build_menu(self):
        menus = OrderedDict()
        menus['File'] = (
        {
            'name' : 'New',
            'action' : self.gshell.new_terminal,
            'data' : None,
            'icon' : gtk.STOCK_NEW,
            'position' : 0,
            'group' : 1,
            'children' : None,
        },
        {
            'name' : 'Open',
            'action' : self.gshell.menu_open,
            'data' : None,
            'icon' : gtk.STOCK_OPEN,
            'position' : 1,
            'group' : 1,
            'children' : None,
        },
        {
            'name' : 'Save as',
            'action' : self.gshell.menuitem_response,
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
                    'action' : self.gshell.menu_log,
                    'data' : 'start',
                    'icon' : None,
                    'group' : 1,
                    'position' : 0,
                    'children' : None,
                },
                {
                    'name' : 'Stop',
                    'action' : self.gshell.menu_log,
                    'data' : 'stop',
                    'icon' : None,
                    'group' : 1,
                    'position' : 1,
                    'children' : None,
                },
            ) 
        },
        {
            'name' : 'Exit',
            'action' : self.gshell.gshell_destroy,
            'data' : None,
            'icon' : gtk.STOCK_QUIT,
            'position' : 0,
            'group' : 3,
            'children' : None,
        })

        menus['Edit'] = (
        {
            'name' : 'Copy',
            'action' : self.gshell.menu_copy,
            'data' : None,
            'icon' : gtk.STOCK_COPY,
            'position' : 0,
            'group' : 1,
            'children' : None
        },
        { 
           'name' : 'Paste',
            'action' : self.gshell.menu_paste,
            'data' : None,
            'icon' : gtk.STOCK_PASTE,
            'position' : 1,
            'group' : 1,
            'children' : None
        },
        {
            'name' : 'Select All',
            'action' : self.gshell.menu_select_all,
            'data' : None,
            'icon' : gtk.STOCK_SELECT_ALL,
            'position' : 0,
            'group' : 2,
            'children' : None
        })

        menus['Tools'] = (
        {
            'name' : 'Scripts',
            'action' : self.gshell.menuitem_response,
            'data' : None,
            'icon' : None,
            'position' : 0,
            'group' : 1,
            'children' : None
        },
        {
            'name' : 'Options',
            'action' : self.gshell.menuitem_response,
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
            'action' : self.gshell.menuitem_response,
            'data' : None,
            'icon' : gtk.STOCK_HELP,
            'position' : 0,
            'group' : 1,
            'children' : None
        },
        {
            'name' : 'About',
            'action' : self.gshell.menu_about,
            'data' : None,
            'icon' : gtk.STOCK_ABOUT,
            'position' : 0,
            'group' : 2,
            'children' : None
        })

        for main_menu, submenus in menus.iteritems():
            main_menu_item = gtk.MenuItem(main_menu)
            menu = gtk.Menu()
            self.grouped_menu(menu, submenus)
            main_menu_item.set_submenu(menu)
            self.append(main_menu_item)

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

class GshellTabPopupMenu(gtk.Menu):

    def __init__(self, tablabel, notebook):
        super(GshellTabPopupMenu, self).__init__()
        self.tablabel = tablabel
        self.notebook = notebook
        self.terminal_broadcast = gtk.CheckMenuItem('Enable Broadcast')
        self.terminal_broadcast.set_active(self.tablabel.terminal.broadcast)
        self.terminal_broadcast.connect('activate', self.tablabel.on_enable_broadcast)
        self.insert(self.terminal_broadcast, -1)

        self.broadcast_group = gtk.MenuItem('Broadcast Group')
        sub_menu = gtk.Menu()
        for color in self.notebook.config.broadcast_images.keys():
            menu_item = gtk.CheckMenuItem(color)
            menu_item.set_active(self.tablabel.terminal.group == color)
            menu_item.connect('activate', self.tablabel.terminal.on_change_group, color)
            sub_menu.insert(menu_item, -1)
        self.broadcast_group.set_submenu(sub_menu)
        self.insert(self.broadcast_group, -1)

        self.enable_log = gtk.CheckMenuItem('Enable log')
        self.enable_log.set_active(self.tablabel.terminal.logger and self.tablabel.terminal.logger.logging)
        self.enable_log.connect('activate', self.tablabel.enable_log)
        self.insert(self.enable_log, -1)

        self.insert(gtk.SeparatorMenuItem(), -1)

        self.close_tab = gtk.CheckMenuItem('Close This Tab')
        self.close_tab.connect('activate', self.notebook.close_tabs, tablabel, 'current')
        self.insert(self.close_tab, -1)

        self.close_other_tabs = gtk.CheckMenuItem('Close Other Tabs')
        self.close_other_tabs.connect('activate', self.notebook.close_tabs, tablabel, 'other')
        self.insert(self.close_other_tabs, -1)

        self.close_all_tabs = gtk.CheckMenuItem('Close All Tabs')
        self.close_all_tabs.connect('activate', self.notebook.close_tabs, tablabel, 'all')
        self.insert(self.close_all_tabs, -1)

        self.show_all()

class GshellTerminalPopupMenu(gtk.Menu):

    def __init__(self, terminal, gshell):
        super(GshellTerminalPopupMenu, self).__init__()
        self.terminal = terminal
        self.gshell = gshell

        menu_item = gtk.ImageMenuItem(gtk.STOCK_COPY)
        menu_item.get_children()[0].set_label('Copy')
        menu_item.connect('activate', self.gshell.menu_copy)
        self.insert(menu_item, -1)

        menu_item = gtk.ImageMenuItem(gtk.STOCK_PASTE)
        menu_item.get_children()[0].set_label('Paste')
        menu_item.connect('activate', self.gshell.menu_paste)
        self.insert(menu_item, -1)

        self.insert(gtk.SeparatorMenuItem(), -1)

        menu_item = gtk.ImageMenuItem(gtk.STOCK_CLOSE)
        menu_item.get_children()[0].set_label('Close')
        menu_item.connect('activate', self.gshell.notebook.close_tab, self.terminal.label)
        self.insert(menu_item, -1)
