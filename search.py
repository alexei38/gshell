# -*- coding: utf-8 -*-

import gtk
import gobject
import re
from config import Config

class GshellSearch(gtk.HBox):

    def __init__(self, terminal):
        super(GshellSearch, self).__init__()
        self.__gobject_init__()
        self.config = Config()
        self.terminal = terminal

        self.searchstring = None
        self.searchrow = 0
        self.searchre = None

        label = gtk.Label('Search:')
        label.show()
        self.pack_start(label, False, False, 5)

        self.entry = gtk.Entry()
        self.entry.set_activates_default(True)
        self.entry.connect('activate', self.do_search)
        self.entry.connect('key-press-event', self.search_keypress)
        self.entry.show()
        self.pack_start(self.entry)

        self.result = gtk.Label('')
        self.result.show()
        self.pack_start(self.result, False, False, 5)

        self.prev = gtk.Button('Prev')
        self.prev.show()
        self.prev.set_sensitive(False)
        self.prev.connect('clicked', self.prev_search)
        self.pack_start(self.prev, False, False, 1)

        self.next = gtk.Button('Next')
        self.next.show()
        self.next.set_sensitive(False)
        self.next.connect('clicked', self.next_search)
        self.pack_start(self.next, False, False, 1)

        close = gtk.Button()
        close.set_relief(gtk.RELIEF_NONE)
        close.set_focus_on_click(False)
        icon = gtk.Image()
        icon.set_from_stock(gtk.STOCK_CLOSE, gtk.ICON_SIZE_MENU)
        close.add(icon)
        close.set_name('search-close-button')
        if hasattr(close, 'set_tooltip_text'):
            close.set_tooltip_text('Close Search bar')
        close.connect('clicked', self.end_search)
        close.show_all()
        self.pack_end(close, False, False, 1)

        self.hide()
        self.set_no_show_all(True)

    def do_search(self, *args):
        searchtext = self.entry.get_text()
        if searchtext == '':
            return
        if searchtext != self.searchstring:
            self.searchstring = searchtext
            self.searchre = re.compile(searchtext)
        self.next.set_sensitive(True)
        self.prev.set_sensitive(True)
        self.next_search()

    def search_keypress(self, widget, event):
        key = gtk.gdk.keyval_name(event.keyval)
        if key == 'Escape':
            self.end_search()
            return True
        return False

    def prev_search(self, *args):
        startrow, endrow = self.get_vte_buffer_range()
        while True:
            if self.searchrow <= startrow:
                self.searchrow = endrow
                self.result.set_text('No more results')
                return
            buff = self.terminal.get_text_range(self.searchrow, 0,
                                             self.searchrow+1, 0,
                                             self.search_character)
            matches = self.searchre.search(buff)
            if matches:
                self.search_hit(self.searchrow)
                self.searchrow -= 1
                return
            self.searchrow -= 1

    def next_search(self, *args):
        startrow, endrow = self.get_vte_buffer_range()
        while True:
            if self.searchrow >= endrow:
                self.searchrow = startrow
                self.result.set_text('No more results')
                return
            buff = self.terminal.get_text_range(self.searchrow, 0,
                                             self.searchrow+1, 0,
                                             self.search_character)
            matches = self.searchre.search(buff)
            if matches:
                self.search_hit(self.searchrow)
                self.searchrow += 1
                return
            self.searchrow += 1

    def end_search(self, *args):
        self.searchrow = 0
        self.searchstring = None
        self.searchre = None
        self.result.set_text('')
        self.hide()
        self.terminal.grab_focus()

    def search_hit(self, row):
        self.result.set_text("%s %d" % ('Found at row', row))
        self.terminal.scrollbar.set_value(row)
        self.next.show()
        self.prev.show()

    def search_character(self, widget, col, row, junk):
        return True

    def get_vte_buffer_range(self):
        column, endrow = self.terminal.get_cursor_position()
        if self.config['scrollback_lines'] < 0:
            startrow = 0
        else:
            startrow = max(0, endrow - self.config['scrollback_lines'])
        return(startrow, endrow)
