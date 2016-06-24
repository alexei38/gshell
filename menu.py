# -*- coding: utf-8 -*-

import gtk
from itertools import groupby
from collections import OrderedDict

class GshellMenu(gtk.MenuBar):
    def __init__(self, main_window):
        super(GshellMenu, self).__init__()
        self.main_window = main_window
        self.menu = self.build_menu()

    def build_menu(self):
        menus = OrderedDict()
        menus['File'] = (
        {
            'name' : 'New',
            'action' : self.main_window.on_new_terminal,
            'data' : None,
            'icon' : gtk.STOCK_NEW,
            'position' : 0,
            'group' : 1,
            'children' : None,
        },
        {
            'name' : 'Open',
            'action' : self.main_window.menu_open,
            'data' : None,
            'icon' : gtk.STOCK_OPEN,
            'position' : 1,
            'group' : 1,
            'children' : None,
        },
        {
            'name' : 'Save as',
            'action' : self.main_window.menuitem_response,
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
                    'action' : self.main_window.menuitem_response,
                    'data' : None,
                    'icon' : None,
                    'group' : 1,
                    'position' : 0,
                    'children' : None,
                },
                {
                    'name' : 'Stop',
                    'action' : self.main_window.menuitem_response,
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
            'action' : self.main_window.main_window_destroy,
            'data' : None,
            'icon' : gtk.STOCK_QUIT,
            'position' : 0,
            'group' : 3,
            'children' : None,
        })

        menus['Edit'] = (
        {
            'name' : 'Copy',
            'action' : self.main_window.menu_copy,
            'data' : None,
            'icon' : gtk.STOCK_COPY,
            'position' : 0,
            'group' : 1,
            'children' : None
        },
        { 
           'name' : 'Paste',
            'action' : self.main_window.menu_paste,
            'data' : None,
            'icon' : gtk.STOCK_PASTE,
            'position' : 1,
            'group' : 1,
            'children' : None
        },
        {
            'name' : 'Select All',
            'action' : self.main_window.menu_select_all,
            'data' : None,
            'icon' : gtk.STOCK_SELECT_ALL,
            'position' : 0,
            'group' : 2,
            'children' : None
        })

        menus['Tab'] = (
        {
            'name' : 'New Tab',
            'action' : self.main_window.on_new_terminal,
            'data' : None,
            'icon' : None,
            'position' : 0,
            'group' : 1,
            'children' : None
        },
        { 
           'name' : 'New Tab Group',
            'action' : self.main_window.menuitem_response,
            'data' : None,
            'icon' : None,
            'position' : 1,
            'group' : 1,
            'children' : None
        },
        {
            'name' : 'Arrange',
            'action' : self.main_window.menuitem_response,
            'data' : None,
            'icon' : None,
            'position' : 2,
            'group' : 1,
            'children' : (
                {
                    'name' : 'Arrange Vertical',
                    'action' : self.main_window.menuitem_response,
                    'data' : None,
                    'icon' : None,
                    'group' : 1,
                    'position' : 0,
                    'children' : None,
                },
                {
                    'name' : 'Arrange Horizontal',
                    'action' : self.main_window.menuitem_response,
                    'data' : None,
                    'icon' : None,
                    'group' : 1,
                    'position' : 1,
                    'children' : None,
                },
                {
                    'name' : 'Arrange Tiled',
                    'action' : self.main_window.menuitem_response,
                    'data' : None,
                    'icon' : None,
                    'group' : 1,
                    'position' : 2,
                    'children' : None,
                },
                {
                    'name' : 'Merge All Tab Groups',
                    'action' : self.main_window.menuitem_response,
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
            'action' : self.main_window.menu_close_tab,
            'data' : 'current',
            'icon' : None,
            'position' : 0,
            'group' : 2,
            'children' : None
        },
        {
            'name' : 'Close Other Tabs',
            'action' : self.main_window.menu_close_tab,
            'data' : 'other',
            'icon' : None,
            'position' : 1,
            'group' : 2,
            'children' : None
        },
        {
            'name' : 'Close All Tabs',
            'action' : self.main_window.menu_close_tab,
            'data' : 'all',
            'icon' : None,
            'position' : 2,
            'group' : 2,
            'children' : None
        },
       {
            'name' : 'Zoom In',
            'action' : self.main_window.menu_zoom_tab,
            'data' : 'zoom_in',
            'icon' : gtk.STOCK_ZOOM_IN,
            'position' : 0,
            'group' : 3,
            'children' : None
        },
        {
            'name' : 'Zoom Out',
            'action' : self.main_window.menu_zoom_tab,
            'data' : 'zoom_out',
            'icon' : gtk.STOCK_ZOOM_OUT,
            'position' : 1,
            'group' : 3,
            'children' : None
        },
        {
            'name' : 'Zoom Default',
            'action' : self.main_window.menu_zoom_tab,
            'data' : 'zoom_orig',
            'icon' : gtk.STOCK_ZOOM_100,
            'position' : 2,
            'group' : 3,
            'children' : None
        })

        menus['Tools'] = (
        {
            'name' : 'Scripts',
            'action' : self.main_window.menuitem_response,
            'data' : None,
            'icon' : None,
            'position' : 0,
            'group' : 1,
            'children' : None
        },
        {
            'name' : 'Options',
            'action' : self.main_window.menuitem_response,
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
            'action' : self.main_window.menuitem_response,
            'data' : None,
            'icon' : gtk.STOCK_HELP,
            'position' : 0,
            'group' : 1,
            'children' : None
        },
        {
            'name' : 'About',
            'action' : self.main_window.menu_about,
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
