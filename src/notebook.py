# -*- coding: utf-8 -*-

import vte
import gtk
import pango
import gobject
from logger import GshellLogger
from terminal import GshellTerm
from tablabel import GshellTabLabel
from search import GshellSearch
from menu import GshellTerminalPopupMenu

class GshellNoteBook(gtk.Notebook):

    def __init__(self, gshell):
        gtk.Notebook.__init__(self)
        self.set_tab_pos(gtk.POS_TOP)
        self.set_scrollable(True)
        self.set_show_tabs(True)
        self.search = None
        self.gshell = gshell
        self.config = gshell.config
        self.connect('switch-page', self.on_switch_page)
        self.show_all()

    def add_tab(self, title=None, command=None, argv=[], envv=[], terminal=None):
        print 'GshellNoteBook::add_tab called'
        if terminal:
            self.terminal = terminal
        else:
            self.terminal = GshellTerm(self.gshell)
        self.terminal.spawn_child(command=command, argv=argv, envv=envv)
        print "PID Terminal: %s" % self.terminal.pid
        if command in ['sshpass', 'ssh']:
            self.terminal.mark_close = True
        if not terminal:
            logger = GshellLogger(self.terminal)
            self.terminal.logger = logger
            self.terminalbox = self.create_terminalbox()
            page_term = self.append_page(self.terminalbox)
            if not title:
                title = 'Term%s ' % (int(page_term) + 1)
            else:
                title = title + ' '
            label = GshellTabLabel(title, self)
            self.terminal.label = label
            self.terminal.notebook = self
            label.terminal = self.terminal
            label.connect('close-clicked', self.close_tab)
            self.terminal.connect('child-exited', self.on_terminal_exit, {'terminalbox' : self.terminalbox, 'label' : label, 'terminal' : self.terminal})
            self.terminal.connect('button-press-event', self.terminal_popup)
            self.set_tab_label(self.terminalbox, label)
            self.set_tab_reorderable(self.terminalbox, True)
        else:
            label = self.terminal.label
            label.unmark_close()
            page_term = self.get_page_by_terminal(self.terminal)
        self.show_all()
        self.set_current_page(page_term)
        return self.terminal

    def new_tab_by_host(self, host, terminal=None):
        print 'GshellNoteBook::new_tab_by_host called'
        argv = []
        envv = []
        password = self.config.decrypt_password(host)
        if password:
            command = 'sshpass'
            argv += ['sshpass']
        else:
            command = 'ssh'
        argv += ['ssh']
        argv += ['-p', host['port']]
        if host['username']:
            argv += ['-l', host['username']]
        argv += ['-o', 'StrictHostKeyChecking=no']
        argv += [host['host']]
        terminal = self.add_tab(title=host['name'], command=command, argv=argv, envv=envv, terminal=terminal)
        terminal.host = host
        if host['log']:
            terminal.logger.start_logger(host['log'])
        self.gshell.switch_toolbar_sensitive(terminal)
        if password:
            terminal.send_data(data=password, timeout=2000, reset=True)
        if host['start_commands']:
            commands = []
            basetime = 3000
            for line in host['start_commands'].splitlines():
                if line.startswith("##SUDO"):
                    terminal.send_data(data='sudo -i', timeout=basetime)
                    if password:
                        basetime += 500
                        terminal.send_data(data=password, timeout=basetime)
                        basetime += 500
                else:
                    terminal.send_data(data=line, timeout=basetime)
                basetime += 500

    def get_terminal_by_page(self, tabnum):
        tab_parent = self.get_nth_page(tabnum)
        return self.find_children_terminal(tab_parent)

    def get_page_by_terminal(self, terminal):
        return self.page_num(terminal.get_parent().get_parent())

    def find_children_terminal(self, parent):
        if parent:
            for child in parent.get_children():
                if isinstance(child, vte.Terminal):
                    return child
                else:
                    return self.find_children_terminal(child)
        return None

    def get_current_terminal(self):
        current_page = self.get_current_page()
        return self.get_terminal_by_page(current_page)

    def get_all_terminals(self):
        terminals = []
        for i in xrange(0, self.get_n_pages() + 1):
            term = self.get_terminal_by_page(i)
            if term:
                terminals.append(term)
        return terminals

    def on_switch_page(self, widget, page, page_num, *args):
        print 'GshellNoteBook::on_switch_page called'
        terminal = self.get_terminal_by_page(page_num)
        self.gshell.switch_toolbar_sensitive(terminal)
        gobject.timeout_add(10, terminal.grab_focus)

    def on_terminal_exit(self, widget, data):
        print 'GshellNoteBook::on_terminal_exit called'
        if data['terminal'].mark_close:
            data['terminal'].terminal_active = False
            data['label'].mark_close()
            self.gshell.switch_toolbar_sensitive(data['terminal'])
        else:
            pagepos = self.page_num(data['terminalbox'])
            if pagepos != -1:
                data['terminal'].destroy()
                self.remove_page(pagepos)
                self.gshell.switch_toolbar_sensitive()

    def close_tab(self, widget, label):
        print 'GshellNoteBook::close_tab called'
        terminal, page = self.get_terminal_by_label(label)
        if terminal:
            if terminal.terminal_active:
                dialog = gtk.MessageDialog(self.gshell.window, gtk.DIALOG_MODAL, gtk.MESSAGE_INFO, gtk.BUTTONS_YES_NO, "This terminal is active?\nAre you sure you want to close?")
                response = dialog.run()
                dialog.destroy()
                if response == gtk.RESPONSE_YES:
                    self.remove_page(page)
                    terminal.close()
                    terminal.destroy()
                    label.destroy()
                    self.gshell.switch_toolbar_sensitive()
            else:
                self.remove_page(page)
                terminal.close()
                terminal.destroy()
                label.destroy()
                self.gshell.switch_toolbar_sensitive()

    def close_tabs(self, widget, label, data=None):
        current_terminal, page = self.get_terminal_by_label(label)
        if data == 'current':
            current_terminal.mark_close = False
            current_terminal.close()
        else:
            for terminal in self.get_all_terminals():
                if data == 'other' and terminal == current_terminal:
                    continue
                terminal.mark_close = False
                terminal.close()

    def get_terminal_by_label(self, label):
        page = -1
        terminal = None
        for i in xrange(0, self.get_n_pages() + 1):
            if label == self.get_tab_label(self.get_nth_page(i)):
                page = i
                break
        if page != -1:
            terminal = self.get_terminal_by_page(page)
        return (terminal, page)

    def create_terminalbox(self):
        print 'GshellNoteBook::create_terminalbox called'
        vbox = gtk.VBox()
        hbox = gtk.HBox()
        vbox.pack_start(hbox, True, True)
        self.terminal.search = GshellSearch(self.terminal)
        vbox.pack_start(self.terminal.search, False, False, 5)
        adj = self.terminal.get_adjustment()
        self.scrollbar = gtk.VScrollbar(adj)
        self.terminal.scrollbar = self.scrollbar
        self.scrollbar.set_no_show_all(True)
        self.scrollbar_position = self.config['scrollbar_position']
        if self.scrollbar_position not in ('hidden', 'disabled'):
            self.scrollbar.show()
        if self.scrollbar_position == 'left':
            func = hbox.pack_end
        else:
            func = hbox.pack_start
        func(self.terminal)
        func(self.scrollbar, False)
        hbox.show_all()
        return vbox

    def all_emit(self, terminal, type, event):
        for term in self.get_all_terminals():
            if term != terminal and term.broadcast:
                term.emit(type, event)

    def terminal_popup(self, terminal, event):
        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 3 and self.terminal:
            menu = GshellTerminalPopupMenu(terminal, self.gshell)
            menu.show_all()
            menu.popup(None, None, None, event.button, event.time)
