# -*- coding: utf-8 -*-

import os
import gtk
import gobject

class ManageHost(gtk.Window):

    def __init__(self, gshell, *args):
        gtk.Window.__init__(self, *args)
        self.gshell = gshell
        self.notebook = self.gshell.notebook
        self.config = self.gshell.config
        self.connect("delete_event", self.on_exit)
        self.connect("key-press-event",self._key_press_event)
        self.build_window()
        self.window.focus(0)

    def on_exit(self, *args):
        self.destroy()
        return True

    def _key_press_event(self, widget, event):
        keyval = event.keyval
        keyval_name = gtk.gdk.keyval_name(keyval)
        if keyval_name == 'Escape':
            self.destroy()
            return True
        return False

    def on_connect(self, *args):
        print 'ManageHost::on_connect called'
        selected_hosts, selected_group_hosts = self.find_selected_hosts()
        uniq_hosts = []
        for host in (selected_hosts + selected_group_hosts):
            if host not in uniq_hosts:
                uniq_hosts.append(host)
                self.notebook.new_tab_by_host(host=host)

    def on_cursor_changed(self, *args):
        print 'ManageHost::on_cursor_changed called'
        selected_hosts, selected_group_hosts = self.find_selected_hosts()
        if len(selected_hosts) == 1:
            self.edit_button.set_sensitive(True)
        else:
            self.edit_button.set_sensitive(False)
        if len(selected_hosts) > 0 or len(selected_group_hosts) > 0:
            self.remove_button.set_sensitive(True)
            self.connect_button.set_sensitive(True)
        else:
            self.remove_button.set_sensitive(False)
            self.connect_button.set_sensitive(False)

    def find_selected_hosts(self):
        model, paths = self.treeselection.get_selected_rows()
        uuids = []
        groups = []
        for path in paths:
            tree_iter = model.get_iter(path)
            uuid = model.get_value(tree_iter, 5)
            name = model.get_value(tree_iter, 1)
            if uuid:
                uuids.append(uuid)
            else:
                groups.append(name)
        hosts = [host for host in self.config.hosts if host['uuid'] in uuids]
        group_hosts = [host for host in self.config.hosts if host['group'] in groups]
        return (hosts, group_hosts)

    def search(self, model, column, key, iter, data):
        print 'ManageHost::search called'
        name = model.get_value(iter, 1).lower()
        if name != '' and key.lower() in name:
            return False
        host = model.get_value(iter, 2).lower()
        if host != '' and key.lower() in host:
            return False
        username = model.get_value(iter, 3).lower()
        if username != '' and key.lower() in username:
            return False
        return True

    def build_window(self):
        self.set_size_request(700, 450)
        self.set_title("Open connections")
        self.set_resizable(True)

        self.vbox = gtk.VBox()
        self.add(self.vbox)

        """ Toolbar """
        toolbar = gtk.Toolbar()
        toolbar.set_orientation(gtk.ORIENTATION_HORIZONTAL)
        toolbar.set_style(gtk.TOOLBAR_BOTH)

        self.new_button = gtk.ToolButton(gtk.STOCK_ADD)
        self.new_button.set_label("Add")
        self.new_button.set_sensitive(True)
        self.new_button.set_size_request(60, 50)
        self.new_button.connect('clicked', self.gshell.menuitem_response)
        toolbar.append_widget(self.new_button, "Add", "Add")

        self.edit_button = gtk.ToolButton(gtk.STOCK_EDIT)
        self.edit_button.set_label("Edit")
        self.edit_button.set_sensitive(False)
        self.edit_button.set_size_request(60, 50)
        self.edit_button.connect('clicked', self.gshell.menuitem_response)
        toolbar.append_widget(self.edit_button, "Edit", "Edit")

        self.remove_button = gtk.ToolButton(gtk.STOCK_ADD)
        self.remove_button.set_label("Remove")
        self.remove_button.set_sensitive(False)
        self.remove_button.set_size_request(60, 50)
        self.remove_button.connect('clicked', self.gshell.menuitem_response)
        toolbar.append_widget(self.remove_button, "Remove", "Remove")

        toolbar.append_widget(gtk.SeparatorToolItem(), None, None)

        self.connect_button = gtk.ToolButton(gtk.STOCK_CONNECT)
        self.connect_button.set_label("Connect")
        self.connect_button.set_sensitive(True)
        self.connect_button.set_size_request(60, 50)
        self.connect_button.connect('clicked', self.on_connect)
        toolbar.append_widget(self.connect_button, "Connect", "Connect")

        toolbar.append_widget(gtk.SeparatorToolItem(), None, None)

        self.vbox.pack_start(toolbar, False, False, 0)

        """ Search """
        hbox = gtk.HBox()
        self.vbox.pack_start(hbox, False, False, 5)
        hbox.pack_start(gtk.Label('Search: '), False, False, 5)
        self.entry = gtk.Entry()
        self.entry.set_size_request(250, -1)
        hbox.pack_start(self.entry, False, False, 0)

        """ Host List """
        store = gtk.TreeStore(gtk.gdk.Pixbuf, str, str, str, str, str)
        tree_model = gtk.TreeModelSort(store)
        self.tree = gtk.TreeView(tree_model)

        self.tree.connect('row-activated', self.on_connect)
        self.tree.connect('cursor-changed', self.on_cursor_changed)

        self.tree.set_search_entry(self.entry)
        self.tree.set_search_equal_func(self.search, None)

        self.tree.set_rubber_banding(True)
        self.treeselection = self.tree.get_selection()
        self.treeselection.set_mode(gtk.SELECTION_MULTIPLE)

        renderer_name = gtk.CellRendererText()
        render_pixbuf = gtk.CellRendererPixbuf()
        column = gtk.TreeViewColumn('Name')
        column.pack_start(render_pixbuf, False)
        column.pack_start(renderer_name, True)
        column.set_attributes(render_pixbuf, pixbuf=0)
        column.set_attributes(renderer_name, text=1)
        column.set_resizable(True)
        column.set_sort_column_id(1)
        self.tree.append_column(column)

        renderer_host = gtk.CellRendererText()
        renderer_host.set_padding(3, 0)
        column = gtk.TreeViewColumn('Host', renderer_host, text=2)
        column.set_resizable(True)
        column.set_sort_column_id(2)
        self.tree.append_column(column)

        renderer_username = gtk.CellRendererText()
        column = gtk.TreeViewColumn('Username', renderer_username, text=3)
        column.set_resizable(True)
        column.set_sort_column_id(3)
        self.tree.append_column(column)

        renderer_description = gtk.CellRendererText()
        column = gtk.TreeViewColumn('Description', renderer_description, text=4)
        column.set_resizable(True)
        self.tree.append_column(column)

        renderer_description = gtk.CellRendererText()
        column = gtk.TreeViewColumn('Uuid', renderer_description, text=5)
        column.set_visible(False)
        self.tree.append_column(column)

        host_groups = {}
        for host in self.gshell.config.hosts:
            group = host['group']
            host_addr = '%s:%s' % (host['host'], host['port'])
            if group not in host_groups:
                icon_file = os.path.join(self.gshell.config.work_dir, 'icon/cubes.png')
                icon = gtk.gdk.pixbuf_new_from_file_at_size(icon_file, 20, 20)
                host_groups[group] = store.append(None, [icon, group, '','','', ''])
            icon_file = os.path.join(self.gshell.config.work_dir, 'icon/connect.png')
            icon = gtk.gdk.pixbuf_new_from_file_at_size(icon_file, 20, 20)
            store.append(host_groups[group], (icon, host['name'], host_addr, host['username'], host['description'], host['uuid']))

        scroll = gtk.ScrolledWindow()
        scroll.add(self.tree)
        self.vbox.pack_start(scroll, True, True, 0)

        """ Run """
        self.show_all()
        self.tree.expand_all()
        self.tree.grab_focus()
