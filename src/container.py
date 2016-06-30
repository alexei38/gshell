# -*- coding: utf-8 -*-

import vte
import gtk
import pango
import gobject
from terminal import GshellTerm
from tablabel import GshellTabLabel
from search import GshellSearch

class GshellContainer(gtk.VBox):
    def __init__(self, gshell):
        gtk.VBox.__init__(self)
        self.gshell = gshell
        self.config = self.gshell.config
        self.notebooks = []
        self.terminal_maps = {}
        """
        {
            "notebook" : {
                "terminal" : vte.Terminal(),
                "label" : GshellTabLabel()
            }
        }
        """

    def add_tab(self, notebook, title=None, command=None, argv=[], envv=[], terminal=None):
        print 'GshellNoteBook::add_tab called'
        if terminal:
            terminal.spawn_child(command=command, argv=argv, envv=envv)
            label = terminal.label
            label.unmark_close()
        else:
            terminal = GshellTerm(self.gshell)
            terminal.spawn_child(command=command, argv=argv, envv=envv)
            terminalbox = self.create_terminalbox(terminal)
            page_term = notebook.append_page(terminalbox)
            terminal.page_term = page_term
            if not title:
                title = 'Term%s ' % (int(page_term) + 1)
            else:
                title = title + ' '
            label = GshellTabLabel(title, notebook)
            terminal.label = label
            label.terminal = terminal
            label.connect('close-clicked', self.close_tab)
            terminal.connect('child-exited', self.on_terminal_exit, {'terminalbox' : terminalbox, 'label' : label, 'terminal' : terminal})
            notebook.set_tab_label(terminalbox, label)
            notebook.set_tab_reorderable(terminalbox, True)
        self.show_all()
        notebook.set_current_page(terminal.page_term)
        return terminal

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

    def create_terminalbox(self, terminal):
        print 'GshellContainer::create_terminalbox called'
        vbox = gtk.VBox()
        hbox = gtk.HBox()
        vbox.pack_start(hbox, True, True)
        terminal.search = GshellSearch(terminal)
        vbox.pack_start(terminal.search, False, False, 5)
        adj = terminal.get_adjustment()
        scrollbar = gtk.VScrollbar(adj)
        terminal.scrollbar = scrollbar
        scrollbar.set_no_show_all(True)
        scrollbar_position = self.config['scrollbar_position']
        if scrollbar_position not in ('hidden', 'disabled'):
            scrollbar.show()
        if scrollbar_position == 'left':
            func = hbox.pack_end
        else:
            func = hbox.pack_start
        func(terminal)
        func(scrollbar, False)
        hbox.show_all()
        return vbox
