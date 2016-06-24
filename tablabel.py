# -*- coding: utf-8 -*-
import gtk
import gobject
from editablelabel import EditableLabel

class GshellTabLabel(gtk.HBox):

    __gsignals__ = {
        'close-clicked': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,(gobject.TYPE_OBJECT,)),
    }

    def __init__(self, title, notebook):
        gtk.HBox.__init__(self)
        self.notebook = notebook
        self.label = EditableLabel(title)
        self.update_angle()
        self.pack_start(self.label, True, True)
        self.update_button()
        self.show_all()

    def update_button(self):
        self.button = gtk.Button()
        self.icon = gtk.Image()
        self.icon.set_from_stock(gtk.STOCK_CLOSE, gtk.ICON_SIZE_MENU)
        self.button.set_focus_on_click(False)
        self.button.set_relief(gtk.RELIEF_NONE)
        style = gtk.RcStyle()
        style.xthickness = 0
        style.ythickness = 0
        self.button.modify_style(style)
        self.button.add(self.icon)
        self.button.connect('clicked', self.on_close)
        self.button.set_name('tab-close-button')
        if hasattr(self.button, 'set_tooltip_text'):
            self.button.set_tooltip_text('Close Tab')
        self.pack_start(self.button, False, False)
        self.show_all()

    def update_angle(self):
        """Update the angle of a label"""
        position = self.notebook.get_tab_pos()
        if position == gtk.POS_LEFT:
            if hasattr(self, 'set_orientation'):
                self.set_orientation(gtk.ORIENTATION_VERTICAL)
            self.label.set_angle(90)
        elif position == gtk.POS_RIGHT:
            if hasattr(self, 'set_orientation'):
                self.set_orientation(gtk.ORIENTATION_VERTICAL)
            self.label.set_angle(270)
        else:
            if hasattr(self, 'set_orientation'):
                self.set_orientation(gtk.ORIENTATION_HORIZONTAL)
            self.label.set_angle(0)

    def on_close(self, widget, data=None):
        print 'GshellTabLabel::on_close called'
        self.emit('close-clicked', self)