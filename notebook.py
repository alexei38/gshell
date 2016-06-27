# -*- coding: utf-8 -*-
import vte
import gtk
import pango
from terminal import GshellTerm
from tablabel import GshellTabLabel


class GshellNoteBook(gtk.Notebook):

    def __init__(self, main_window):
        gtk.Notebook.__init__(self)
        self.set_tab_pos(gtk.POS_TOP)
        self.set_scrollable(True)
        self.set_show_tabs(True)
        self.main_window = main_window
        self.config = main_window.config
        self.show_all()

    def add_tab(self, title=None, command=None, argv=[], envv=[], terminal=None):
        print 'GshellNoteBook::add_tab called'
        if terminal:
            self.terminal = terminal
        else:
            self.terminal = GshellTerm(self.main_window)
        self.terminal.spawn_child(command=command, argv=argv, envv=envv)
        print "PID Terminal: %s" % self.terminal.pid
        if command in ['sshpass', 'ssh']:
            self.terminal.mark_close = True
        if not terminal:
            self.terminalbox = self.create_terminalbox()
            self.page_term = self.append_page(self.terminalbox)
            self.terminal.page_term = self.page_term
            if not title:
                title = 'Term%s' % (int(self.page_term) + 1)
            self.label = GshellTabLabel(title, self)
            self.terminal.label = self.label
            self.label.terminal = self.terminal
            self.label.connect('close-clicked', self.close_tab)
            self.terminal.connect('child-exited', self.on_terminal_exit, {'terminalbox' : self.terminalbox, 'label' : self.label, 'terminal' : self.terminal})
            self.set_tab_label(self.terminalbox, self.label)
            self.set_page(self.page_term)
        else:
            self.label = self.terminal.label
            self.label.unmark_close()
        self.reconfigure()
        self.show_all()
        self.terminal.grab_focus()
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
        if host['password']:
            terminal.send_data(data=host['password'], timeout=2000, reset=True)

    def get_terminal_by_page(self, tabnum):
        print 'GshellNoteBook::get_terminal_by_page called'
        tab_parent = self.get_nth_page(tabnum)
        if isinstance(tab_parent, gtk.HBox):
            for child in tab_parent.get_children():
                if isinstance(child, vte.Terminal):
                    return child
        return None

    def get_current_terminal(self):
        print 'GshellNoteBook::get_current_terminal called'
        current_page = self.get_current_page()
        return self.get_terminal_by_page(current_page)

    def get_all_terminals(self, exclude_current_page=False):
        print 'GshellNoteBook::get_all_terminals called'
        terminals = []
        current_page = self.get_current_page()
        for i in xrange(0, self.get_n_pages() + 1):
            if i == current_page and exclude_current_page:
                continue
            term = self.get_terminal_by_page(i)
            if term:
                terminals.append(term)
        return terminals

    def on_terminal_exit(self, widget, data):
        print 'GshellNoteBook::on_terminal_exit called'
        if data['terminal'].mark_close:
            data['terminal'].terminal_active = False
            data['label'].mark_close()
        else:
            pagepos = self.page_num(data['terminalbox'])
            if pagepos != -1:
                self.remove_page(pagepos)

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
                    dialog = gtk.MessageDialog(self.main_window.window, gtk.DIALOG_MODAL, gtk.MESSAGE_INFO, gtk.BUTTONS_YES_NO, "This terminal is active?\nAre you sure you want to close?")
                    response = dialog.run()
                    dialog.destroy()
                    if response == gtk.RESPONSE_YES:
                        term.close()
                        self.remove_page(tabnum)
                        del(label)
                else:
                    term.close()
                    del(label)
                    self.remove_page(tabnum)

    def create_terminalbox(self):
        print 'GshellNoteBook::create_terminalbox called'
        terminalbox = gtk.HBox()
        self.scrollbar = gtk.VScrollbar(self.terminal.get_adjustment())
        self.scrollbar.set_no_show_all(True)
        self.scrollbar_position = self.config['scrollbar_position']
        if self.scrollbar_position not in ('hidden', 'disabled'):
            self.scrollbar.show()
        if self.scrollbar_position == 'left':
            func = terminalbox.pack_end
        else:
            func = terminalbox.pack_start
        func(self.terminal)
        func(self.scrollbar, False)
        terminalbox.show_all()
        return terminalbox

    def on_terminal_focus_in(self, _widget, _event):
        print 'GshellNoteBook::on_terminal_focus_in called'
        self.terminal.set_colors(self.fgcolor_active, self.bgcolor,
                            self.palette_active)

    def on_terminal_focus_out(self, _widget, _event):
        print 'GshellNoteBook::on_terminal_focus_out called'
        self.terminal.set_colors(self.fgcolor_inactive, self.bgcolor,
                            self.palette_inactive)

    def reconfigure(self):
        print 'GshellNoteBook::reconfigure called'
        if hasattr(self.terminal, 'set_alternate_screen_scroll'):
            self.terminal.set_alternate_screen_scroll(self.config['alternate_screen_scroll'])
        if self.config['copy_on_selection']:
            self.terminal.connect('selection-changed', lambda widget: self.terminal.copy_clipboard())
        self.terminal.set_emulation(self.config['emulation'])
        self.terminal.set_encoding(self.config['encoding'])
        self.terminal.set_word_chars(self.config['word_chars'])
        self.terminal.set_mouse_autohide(self.config['mouse_autohide'])
        if self.config['use_system_font'] == True:
            font = self.config.get_system_font()
        else:
            font = self.config['font']
        self.terminal.set_font(pango.FontDescription(font))
        self.terminal.set_allow_bold(self.config['allow_bold'])
        if self.config['use_theme_colors']:
            self.fgcolor_active = self.terminal.get_style().text[gtk.STATE_NORMAL]
            self.bgcolor = self.terminal.get_style().base[gtk.STATE_NORMAL]
        else:
            self.fgcolor_active = gtk.gdk.color_parse(self.config['foreground_color'])
            self.bgcolor = gtk.gdk.color_parse(self.config['background_color'])

        factor = self.config['inactive_color_offset']
        if factor > 1.0:
          factor = 1.0
        self.fgcolor_inactive = self.fgcolor_active.copy()

        for bit in ['red', 'green', 'blue']:
            setattr(self.fgcolor_inactive, bit,
                    getattr(self.fgcolor_inactive, bit) * factor)

        colors = self.config['palette'].split(':')
        self.palette_active = []
        self.palette_inactive = []
        for color in colors:
            if color:
                newcolor = gtk.gdk.color_parse(color)
                newcolor_inactive = newcolor.copy()
                for bit in ['red', 'green', 'blue']:
                    setattr(newcolor_inactive, bit, getattr(newcolor_inactive, bit) * factor)
                self.palette_active.append(newcolor)
                self.palette_inactive.append(newcolor_inactive)
        self.terminal.set_colors(self.fgcolor_active, self.bgcolor, self.palette_active)
        if hasattr(self.terminal, 'set_cursor_shape'):
            self.terminal.set_cursor_shape(getattr(vte, 'CURSOR_SHAPE_%s' % self.config['cursor_shape'].upper()))

        background_type = self.config['background_type']
        if background_type == 'image' and self.config['background_image'] is not None and self.config['background_image'] != '':
            self.terminal.set_background_image_file(self.config['background_image'])
            self.terminal.set_scroll_background(self.config['scroll_background'])
        else:
            try:
                self.terminal.set_background_image(None)
            except TypeError:
                pass
            self.terminal.set_scroll_background(False)

        if background_type in ('image', 'transparent'):
            self.terminal.set_background_tint_color(gtk.gdk.color_parse(
                                               self.config['background_color']))
            opacity = int(self.config['background_darkness'] * 65536)
            saturation = 1.0 - float(self.config['background_darkness'])
            self.terminal.set_background_saturation(saturation)
        else:
            opacity = 65535
            self.terminal.set_background_saturation(1)

        if self.terminal.composite_support:
            self.terminal.set_opacity(opacity)
        if not self.terminal.composite_support or self.config['disable_real_transparency']:
            background_transparent = True
        else:
            if self.terminal.is_composited() == False:
                background_transparent = True
            else:
                background_transparent = False
        if self.config['background_type'] == 'transparent':
            self.terminal.set_background_transparent(background_transparent)
        else:
            self.terminal.set_background_transparent(False)

        if hasattr(vte, 'VVVVTE_CURSOR_BLINK_ON'):
            if self.config['cursor_blink'] == True:
                self.terminal.set_cursor_blink_mode('VTE_CURSOR_BLINK_ON')
            else:
                self.terminal.set_cursor_blink_mode('VTE_CURSOR_BLINK_OFF')
        else:
            self.terminal.set_cursor_blinks(self.config['cursor_blink'])

        if self.config['scrollback_infinite'] == True:
            scrollback_lines = -1
        else:
            scrollback_lines = self.config['scrollback_lines']
        self.terminal.set_scrollback_lines(scrollback_lines)
        self.terminal.set_scroll_on_keystroke(self.config['scroll_on_keystroke'])
        self.terminal.set_scroll_on_output(self.config['scroll_on_output'])

        #self.terminal.connect('focus-in-event', self.on_terminal_focus_in)
        #self.terminal.connect('focus-out-event', self.on_terminal_focus_out)

        self.terminal.queue_draw()
