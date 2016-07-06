# -*- coding: utf-8 -*-

import vte
import gtk
import pango
import gobject
from logger import GshellLogger
from terminal import GshellTerm
from tablabel import GshellTabLabel
from search import GshellSearch

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
            self.terminal.page_term = page_term
            if not title:
                title = 'Term%s ' % (int(page_term) + 1)
            else:
                title = title + ' '
            self.label = GshellTabLabel(title, self)
            self.terminal.label = self.label
            self.terminal.notebook = self
            self.label.terminal = self.terminal
            self.label.connect('close-clicked', self.close_tab)
            self.terminal.connect('child-exited', self.on_terminal_exit, {'terminalbox' : self.terminalbox, 'label' : self.label, 'terminal' : self.terminal})
            self.set_tab_label(self.terminalbox, self.label)
            self.set_tab_reorderable(self.terminalbox, True)
        else:
            self.label = self.terminal.label
            self.label.unmark_close()
        self.show_all()
        self.set_current_page(self.terminal.page_term)
        return self.terminal

    def new_tab_by_host(self, host, terminal=None):
        print 'GshellNoteBook::new_tab_by_host called'
        argv = []
        envv = []
        if host['password']:
            command = 'sshpass'
        else:
            command = 'ssh'
        argv += [command]
        argv += ['ssh']
        argv += ['-p', host['port']]
        argv += ['-l', host['username']]
        argv += ['-o', 'StrictHostKeyChecking=no']
        argv += [host['host']]
        terminal = self.add_tab(title=host['name'], command=command, argv=argv, envv=envv, terminal=terminal)
        terminal.host = host
        if host['log']:
            terminal.logger.start_logger(host['log'])
        self.gshell.switch_toolbar_sensitive(terminal)
        if host['password']:
            terminal.send_data(data=host['password'], timeout=2000, reset=True)

    def get_terminal_by_page(self, tabnum):
        tab_parent = self.get_nth_page(tabnum)
        return self.find_children_terminal(tab_parent)

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

    def get_all_terminals(self, exclude_current_page=False):
        terminals = []
        current_page = self.get_current_page()
        for i in xrange(0, self.get_n_pages() + 1):
            if i == current_page and exclude_current_page:
                continue
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
        tabnum = -1
        for i in xrange(0, self.get_n_pages() + 1):
            if label == self.get_tab_label(self.get_nth_page(i)):
                tabnum = i
                break
        if tabnum != -1:
            term = self.get_terminal_by_page(tabnum)
            if term:
                if term.terminal_active:
                    dialog = gtk.MessageDialog(self.gshell.window, gtk.DIALOG_MODAL, gtk.MESSAGE_INFO, gtk.BUTTONS_YES_NO, "This terminal is active?\nAre you sure you want to close?")
                    response = dialog.run()
                    dialog.destroy()
                    if response == gtk.RESPONSE_YES:
                        term.close()
                        term.destroy()
                        label.destroy()
                        self.remove_page(tabnum)
                        self.gshell.switch_toolbar_sensitive()
                else:
                    term.close()
                    term.destroy()
                    label.destroy()
                    self.remove_page(tabnum)
                    self.gshell.switch_toolbar_sensitive()

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
