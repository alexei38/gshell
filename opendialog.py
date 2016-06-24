# -*- coding: utf-8 -*-

import gtk
import os

class OpenDialog(gtk.Dialog):
    def __init__(self, main_window):
        super(OpenDialog, self).__init__()
        self.main_window = main_window
        self.build_window()

    def build_window(self):
        self.set_size_request(700, 450)
        self.set_title("Open connections")
        self.set_resizable(True)

        """ Toolbar """
        toolbar = gtk.Toolbar()
        toolbar.set_orientation(gtk.ORIENTATION_HORIZONTAL)
        toolbar.set_style(gtk.TOOLBAR_BOTH)

        icon_new = gtk.Image()
        icon_new.set_from_stock(gtk.STOCK_ADD, 4)
        toolbar.append_item("Add", "Add", "Add", icon_new, self.main_window.menuitem_response)

        icon_new = gtk.Image()
        icon_new.set_from_stock(gtk.STOCK_EDIT, 4)
        toolbar.append_item("Edit", "Edit", "Edit", icon_new, self.main_window.menuitem_response)

        icon_new = gtk.Image()
        icon_new.set_from_stock(gtk.STOCK_REMOVE, 4)
        toolbar.append_item("Remove", "Remove", "Remove", icon_new, self.main_window.menuitem_response)

        toolbar.append_widget(gtk.SeparatorToolItem(), None, None)

        icon_connect = gtk.Image()
        icon_connect.set_from_stock(gtk.STOCK_CONNECT, 4)
        toolbar.append_item("Connect", "Connect", "Connect", icon_connect, self.main_window.menuitem_response)

        toolbar.append_widget(gtk.SeparatorToolItem(), None, None)

        self.vbox.pack_start(toolbar, False, False, 0)

        """ Host List """
        store = gtk.TreeStore(gtk.gdk.Pixbuf, str, str, str, str)
        tree_model = gtk.TreeModelSort(store)
        tree = gtk.TreeView(tree_model)
        tree.set_rubber_banding(True)
        tree.get_selection().set_mode(gtk.SELECTION_MULTIPLE)

        renderer_name = gtk.CellRendererText()
        renderer_name.set_fixed_size(80, -1)
        render_pixbuf = gtk.CellRendererPixbuf()
        column = gtk.TreeViewColumn('Name')
        column.pack_start(render_pixbuf, False)
        column.pack_start(renderer_name, True)
        tree.append_column(column)
        column.set_attributes(render_pixbuf, pixbuf=0)
        column.set_attributes(renderer_name, text=1)

        renderer_host = gtk.CellRendererText()
        renderer_host.set_fixed_size(140, -1)
        renderer_host.set_padding(3, 0)
        column = gtk.TreeViewColumn('Host', renderer_host, text=2)
        tree.append_column(column)

        renderer_username = gtk.CellRendererText()
        renderer_username.set_fixed_size(80, -1)
        column = gtk.TreeViewColumn('Username', renderer_username, text=3)
        tree.append_column(column)

        renderer_description = gtk.CellRendererText()
        column = gtk.TreeViewColumn('Description', renderer_description, text=4)
        tree.append_column(column)

        host_groups = {}
        for host in self.main_window.config.hosts:
            group = host['group']
            host_addr = '%s:%s' % (host['host'], host['port'])
            if group not in host_groups:
                icon_file = os.path.join(self.main_window.config.work_dir, 'icon/cubes.png')
                icon = gtk.gdk.pixbuf_new_from_file_at_size(icon_file, 20, 20)
                host_groups[group] = store.append(None, [icon, group, '','',''])
            icon_file = os.path.join(self.main_window.config.work_dir, 'icon/connect.png')
            icon = gtk.gdk.pixbuf_new_from_file_at_size(icon_file, 20, 20)
            store.append(host_groups[group], (icon, host['name'], host_addr, host['username'], host['description']))

        scroll = gtk.ScrolledWindow()
        scroll.add(tree)
        self.vbox.pack_start(scroll, True, True, 0)

        """ Run """
        self.show_all()
        tree.expand_all()
        tree.show_all()
        self.run()
        self.destroy()
