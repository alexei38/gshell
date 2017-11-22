# -*- coding: utf-8 -*-

import gtk
import gobject
import pango


class ManageHost(gtk.Window):

    def __init__(self, gshell, *args):
        gtk.Window.__init__(self, *args)
        self.notebook = gshell.notebook
        self.config = gshell.config
        self.hosts_tree = GshellHostTree(gshell)
        self.hosts_tree.tree.connect('cursor-changed', self.on_cursor_changed)

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

    def on_add_host(self, *args):
        GshellHost(self)

    def on_edit_host(self, *args):
        hosts, host_groups = self.hosts_tree.find_selected_hosts()
        host = hosts[0]
        GshellHost(self, host=host)
        gobject.timeout_add(50, self.on_cursor_changed)

    def on_remove_host(self, *args):
        hosts, host_groups = self.hosts_tree.find_selected_hosts()
        uniq_hosts = []
        for host in (hosts + host_groups):
            if host not in uniq_hosts:
                uniq_hosts.append(host)
                self.config.remove_host(host)
                gobject.timeout_add(50, self.hosts_tree.rebuild_host_store)
        gobject.timeout_add(50, self.on_cursor_changed)

    def on_copy_host(self, *args):
        hosts, host_groups = self.hosts_tree.find_selected_hosts()
        host = hosts[0].copy()
        host['uuid'] = None
        host['name'] += '_copy'
        GshellHost(self, host=host)
        gobject.timeout_add(50, self.on_cursor_changed)

    def on_cursor_changed(self, *args):
        hosts, host_groups = self.hosts_tree.find_selected_hosts()
        if len(hosts) == 1:
            self.edit_button.set_sensitive(True)
            self.copy_button.set_sensitive(True)
        else:
            self.edit_button.set_sensitive(False)
            self.copy_button.set_sensitive(False)
        if len(hosts) > 0 or len(host_groups) > 0:
            self.remove_button.set_sensitive(True)
            self.connect_button.set_sensitive(True)
        else:
            self.remove_button.set_sensitive(False)
            self.connect_button.set_sensitive(False)

    def build_window(self):
        self.set_size_request(550, 700)
        self.set_title("Open connections")
        self.set_resizable(True)

        self.vbox = gtk.VBox()
        self.add(self.vbox)

        """ Toolbar """
        toolbar = gtk.Toolbar()
        toolbar.set_orientation(gtk.ORIENTATION_HORIZONTAL)
        toolbar.set_style(gtk.TOOLBAR_BOTH)

        self.new_button = gtk.ToolButton(gtk.STOCK_ADD)
        self.new_button.connect('clicked', self.on_add_host)
        self.new_button.set_tooltip(gtk.Tooltips(), 'Add')
        self.new_button.set_label("Add")
        toolbar.insert(self.new_button, -1)

        self.edit_button = gtk.ToolButton(gtk.STOCK_EDIT)
        self.edit_button.connect('clicked', self.on_edit_host)
        self.edit_button.set_tooltip(gtk.Tooltips(), 'Edit')
        self.edit_button.set_label("Edit")
        toolbar.insert(self.edit_button, -1)

        self.copy_button = gtk.ToolButton(gtk.STOCK_COPY)
        self.copy_button.connect('clicked', self.on_copy_host)
        self.copy_button.set_tooltip(gtk.Tooltips(), 'Copy')
        self.copy_button.set_label("Copy")
        toolbar.insert(self.copy_button, -1)

        self.remove_button = gtk.ToolButton(gtk.STOCK_ADD)
        self.remove_button.set_label("Remove")
        self.remove_button.set_tooltip(gtk.Tooltips(), 'Remove')
        self.remove_button.connect('clicked', self.on_remove_host)
        toolbar.insert(self.remove_button, -1)

        toolbar.insert(gtk.SeparatorToolItem(), -1)

        self.connect_button = gtk.ToolButton(gtk.STOCK_CONNECT)
        self.connect_button.set_label("Connect")
        self.connect_button.set_tooltip(gtk.Tooltips(), 'Connect')
        self.connect_button.connect('clicked', self.hosts_tree.on_connect)
        toolbar.insert(self.connect_button, -1)

        toolbar.insert(gtk.SeparatorToolItem(), -1)

        self.vbox.pack_start(toolbar, False, False, 0)
        self.vbox.pack_start(self.hosts_tree, True, True)

        """ Run """
        self.connect("delete_event", self.on_exit)
        self.connect("key-press-event",self._key_press_event)
        self.show_all()
        self.on_cursor_changed()
        self.hosts_tree.entry.grab_focus()
        self.window.focus(0)


class GshellHostTree(gtk.VBox):

    def __init__(self, gshell, *args):
        gtk.VBox.__init__(self, *args)
        self.config = gshell.config
        self.notebook = gshell.notebook
        self.build_tree()

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
        group_hosts = []
        for host in self.config.hosts:
            if host['group'] in groups and self.search_host(host, list_host=True):
                group_hosts.append(host)
        return (hosts, group_hosts)

    def search_host(self, host, list_host=False):
        searchtext = self.entry.get_text().decode('utf-8').lower()
        if len(searchtext) >= 2:
            if [v for v in host['name'], host['host'], host['username'], host['group']
                           if searchtext in v.decode('utf-8').lower()]:
                return True
            else:
                return False
        else:
            return list_host

    def on_connect(self, *args):
        hosts, host_groups = self.find_selected_hosts()
        uniq_hosts = []
        for host in (hosts + host_groups):
            if host not in uniq_hosts:
                uniq_hosts.append(host)
                self.notebook.new_tab_by_host(host=host)

    def on_key_entry(self, *args):
        gobject.timeout_add(50, self.rebuild_host_store)

    def build_tree(self):
        hbox = gtk.HBox()
        self.pack_start(hbox, False, False, 5)
        hbox.pack_start(gtk.Label('Search: '), False, False, 5)
        self.entry = gtk.Entry()
        self.entry.connect('key-press-event', self.on_key_entry)
        self.entry.set_size_request(250, -1)
        hbox.pack_start(self.entry, False, False, 0)

        """ Host List """
        self.store = gtk.TreeStore(gtk.gdk.Pixbuf, str, str, str, str, str)
        tree_model = gtk.TreeModelSort(self.store)
        self.tree = gtk.TreeView(tree_model)

        self.tree.connect('row-activated', self.on_connect)

        self.tree.set_rubber_banding(True)
        self.treeselection = self.tree.get_selection()
        self.treeselection.set_mode(gtk.SELECTION_MULTIPLE)

        pango_font = pango.FontDescription(self.config['font_host_tree'])

        renderer_name = gtk.CellRendererText()
        renderer_name.set_property('font-desc', pango_font)
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
        renderer_host.set_property('font-desc', pango_font)
        column = gtk.TreeViewColumn('Host', renderer_host, text=2)
        column.set_resizable(True)
        column.set_sort_column_id(2)
        self.tree.append_column(column)

        renderer_username = gtk.CellRendererText()
        renderer_username.set_property('font-desc', pango_font)
        column = gtk.TreeViewColumn('Username', renderer_username, text=3)
        column.set_resizable(True)
        column.set_sort_column_id(3)
        self.tree.append_column(column)

        renderer_description = gtk.CellRendererText()
        renderer_description.set_property('font-desc', pango_font)
        column = gtk.TreeViewColumn('Description', renderer_description, text=4)
        column.set_resizable(True)
        self.tree.append_column(column)

        renderer_description = gtk.CellRendererText()
        column = gtk.TreeViewColumn('Uuid', renderer_description, text=5)
        column.set_visible(False)
        self.tree.append_column(column)

        scroll = gtk.ScrolledWindow()
        scroll.add(self.tree)
        self.pack_start(scroll, True, True, 0)
        self.rebuild_host_store()

    def rebuild_host_store(self):
        self.store.clear()
        host_groups = {}
        for host in self.config.hosts:
            group = host['group']
            host_addr = '%s:%s' % (host['host'], host['port'])
            if not self.search_host(host, True):
                continue
            if group not in host_groups:
                icon_file = self.config.get_icon('cubes.png')
                icon = gtk.gdk.pixbuf_new_from_file_at_size(icon_file, 15, 15)
                host_groups[group] = self.store.append(None, [icon, group, '','','', ''])
            icon_file = self.config.get_icon('connect.png')
            icon = gtk.gdk.pixbuf_new_from_file_at_size(icon_file, 15, 15)
            self.store.append(host_groups[group], (icon, host['name'], host_addr, host['username'], host['description'], host['uuid']))
        self.tree.expand_all()


class GshellHost(gtk.Dialog):

    def __init__(self, main_window, host=None, *args):
        gtk.Dialog.__init__(self, *args)
        self.config = main_window.config
        self.main_window = main_window
        self.host = host
        self.build_dialog()
        self.run_window()

    def run_window(self):
        response = self.run()
        if response == gtk.RESPONSE_OK:
            if not self.host:
                self.host = {'uuid' : None}
            self.host['name'] = self.name_input.get_text()
            self.host['group'] = self.group_input.get_text()
            self.host['host'] = self.host_input.get_text()
            self.host['port'] = self.port_input.get_text()
            self.host['username'] = self.username_input.get_text()
            self.host['password'] = self.password_input.get_text()
            self.host['log'] = self.log_input.get_text()
            self.host['ssh_options'] = self.ssh_options_input.get_text()
            self.host['description'] = self.description_input.get_text()

            command_buffer = self.start_commands_input.get_buffer()
            start_iter =  command_buffer.get_start_iter()
            end_iter = command_buffer.get_end_iter()
            self.host['start_commands'] = command_buffer.get_text(start_iter, end_iter, 0)

            self.config.save_host(self.host)
            gobject.timeout_add(50, self.main_window.rebuild_host_store)
        self.window.destroy()

    def build_dialog(self):
        self.add_buttons(gtk.STOCK_SAVE, gtk.RESPONSE_OK, gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
        self.set_size_request(400, 550)
        self.set_resizable(False)
        if self.host:
            self.set_title("Edit Host")
        else:
            self.set_title("New Host")
        self.hbox = gtk.HBox()
        table = gtk.Table()
        self.vbox.pack_start(table, False, False, 10)

        name_label = gtk.Label('Name')
        self.name_input = gtk.Entry()
        if self.host and self.host['name']:
            self.name_input.set_text(self.host['name'])
        table.attach(name_label, 0, 1, 0, 1, xpadding=15, ypadding=5)
        table.attach(self.name_input, 1, 2, 0, 1, xpadding=15, ypadding=5)

        group_label = gtk.Label('Group')
        self.group_input = gtk.Entry()
        if self.host and self.host['group']:
            self.group_input.set_text(self.host['group'])
        table.attach(group_label, 0, 1, 1, 2, xpadding=15, ypadding=5)
        table.attach(self.group_input, 1, 2, 1, 2, xpadding=15, ypadding=5)

        host_label = gtk.Label('Host')
        self.host_input = gtk.Entry()
        if self.host and self.host['host']:
            self.host_input.set_text(self.host['host'])
        table.attach(host_label, 0, 1, 2, 3, xpadding=15, ypadding=5)
        table.attach(self.host_input, 1, 2, 2, 3, xpadding=15, ypadding=5)

        port_label = gtk.Label('Port')
        self.port_input = gtk.Entry()
        if self.host and self.host['port']:
            self.port_input.set_text(self.host['port'])
        table.attach(port_label, 0, 1, 3, 4, xpadding=15, ypadding=5)
        table.attach(self.port_input, 1, 2, 3, 4, xpadding=15, ypadding=5)

        username_label = gtk.Label('Username')
        self.username_input = gtk.Entry()
        if self.host and self.host['username']:
            self.username_input.set_text(self.host['username'])
        table.attach(username_label, 0, 1, 4, 5, xpadding=15, ypadding=5)
        table.attach(self.username_input, 1, 2, 4, 5, xpadding=15, ypadding=5)

        password_label = gtk.Label('Password')
        self.password_input = gtk.Entry()
        if self.host and self.host['password']:
            password = self.config.decrypt_password(self.host)
            self.password_input.set_text(password)
        self.password_input.set_visibility(False)
        table.attach(password_label, 0, 1, 5, 6, xpadding=15, ypadding=5)
        table.attach(self.password_input, 1, 2, 5, 6, xpadding=15, ypadding=5)

        log_label = gtk.Label('Log file')
        self.log_input = gtk.Entry()
        if self.host and self.host['log']:
            self.log_input.set_text(self.host['log'])
        table.attach(log_label, 0, 1, 6, 7, xpadding=15, ypadding=5)
        table.attach(self.log_input, 1, 2, 6, 7, xpadding=15, ypadding=5)

        ssh_options_label = gtk.Label('SSH Options')
        self.ssh_options_input = gtk.Entry()
        if self.host and self.host['ssh_options']:
            self.ssh_options_input.set_text(self.host['ssh_options'])
        table.attach(ssh_options_label, 0, 1, 7, 8, xpadding=15, ypadding=5)
        table.attach(self.ssh_options_input, 1, 2, 7, 8, xpadding=15, ypadding=5)

        description_label = gtk.Label('Description')
        self.description_input = gtk.Entry()
        if self.host and self.host['description']:
            self.description_input.set_text(self.host['description'])
        table.attach(description_label, 0, 1, 8, 9, xpadding=15, ypadding=5)
        table.attach(self.description_input, 1, 2, 8, 9, xpadding=15, ypadding=5)

        start_commands_label = gtk.Label('Start Commands')
        self.start_commands_input = gtk.TextView()
        self.start_commands_input.set_size_request(-1, 150)
        self.start_commands_input.set_left_margin(5)
        self.start_commands_input.set_editable(True)
        if self.host and self.host['start_commands']:
            buff = self.start_commands_input.get_buffer()
            buff.set_text(self.host['start_commands'])
        table.attach(start_commands_label, 0, 1, 9, 10, xpadding=15, ypadding=5)
        table.attach(self.start_commands_input, 1, 2, 9, 10, xpadding=15, ypadding=5)
        self.show_all()
