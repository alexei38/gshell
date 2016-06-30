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
        self.set_property('homogeneous', True)
        self.search = None
        self.gshell = gshell
        self.config = gshell.config
        self.connect('switch-page', self.on_switch_page)
        self.show_all()



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
