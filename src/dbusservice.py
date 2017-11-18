# -*- coding: utf-8 -*-

import dbus.service
import dbus.glib

BUS_NAME = 'com.github.Gshell'
BUS_PATH = '/com/github/Gshell'

class GshellDbus(dbus.service.Object):

    def __init__(self, gshell):
        self.bus_name = dbus.service.BusName(BUS_NAME, bus=dbus.SessionBus())
        self.bus_path = BUS_PATH
        self.gshell = gshell
        dbus.service.Object.__init__(self, self.bus_name, BUS_PATH)

    @dbus.service.method(BUS_NAME)
    def new_window(self):
        self.gshell.build_window()

    @dbus.service.method(BUS_NAME)
    def new_tab(self):
        self.gshell.notebook.add_tab()

    @dbus.service.method(BUS_NAME)
    def show_hide(self):
        self.gshell.show_hide()

    @dbus.service.method(BUS_NAME, in_signature='s')
    def execute_command(self, command):
        cmd = command.split()[0]
        argv = command.split()
        self.gshell.notebook.add_tab(command=cmd, argv=argv)
