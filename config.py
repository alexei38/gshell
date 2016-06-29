# -*- coding: utf-8 -*-

import gconf
import os
import gtk
from ConfigParser import ConfigParser

DEFAULTS = {
    'allow_bold'            : True,
    'background_color'      : '#000000',
    'background_darkness'   : 0.85,
    'background_type'       : 'transparent',
    'background_image'      : None,
    'backspace_binding'     : 'ascii-del',
    'cursor_blink'          : True,
    'cursor_shape'          : 'block',
    'emulation'             : 'xterm',
    'term'                  : 'xterm',
    'colorterm'             : 'gnome-terminal',
    'font'                  : 'Mono 10',
    'foreground_color'      : '#fff',
    'scrollbar_position'    : "right",
    'scroll_background'     : True,
    'scroll_on_keystroke'   : True,
    'scroll_on_output'      : True,
    'scrollback_lines'      : 1000,
    'scrollback_infinite'   : False,
    'palette'               : '#2e3436:#cc0000:#4e9a06:#c4a000:#3465a4:#75507b:#06989a:#d3d7cf:#555753:#ef2929:#8ae234:#fce94f:#729fcf:#ad7fa8:#34e2e2:#eeeeec',
    'word_chars'            : '-A-Za-z0-9,./?%&#:_',
    'mouse_autohide'        : True,
    'use_system_font'       : True,
    'use_theme_colors'      : False,
    'encoding'              : 'UTF-8',
    'copy_on_selection'     : False,
    'alternate_screen_scroll': True,
    'inactive_color_offset': 0.8,
    'disable_real_transparency' : True,
    'local_keybinder': {
        ('key_zoom', 'zoom_in')     : ['<Control>equal', '<Control>KP_Add'],
        ('key_zoom', 'zoom_out')    : ['<Control>minus', '<Control>KP_Subtract'],
        ('key_zoom', 'zoom_orig')   : ['<Control>KP_0', '<Control>0'],
        'menu_open'                 : '<Shift><Control>O',
        'key_close_term'            : ['<Shift><Control>w', '<Control>d'],
        'menu_copy'                 : '<Shift><Control>c',
        'menu_paste'                : '<Shift><Control>v',
        'new_terminal'              : ['<Shift><Control>t', '<Shift><Control>n'],
        'key_next_tab'              : '<Control>Page_Down',
        'key_prev_tab'              : '<Control>Page_Up',
        'key_full_screen'           : 'F11',
        'menu_select_all'           : '<Shift><Control>A',
        'menu_search'               : '<Shift><Control>F',
    },
    'global_keybinder': {
        'show_hide'                 : '<Control>F12',
    }
}


class Config(object):
    def __init__(self, *args, **kwds):
        super(Config, self).__init__(*args, **kwds)
        self.system_font = None
        self.gconf = None
        self.hosts = []
        self.work_dir = os.path.dirname(os.path.realpath(__file__))
        self.reload_hosts()

    def __getitem__(self, key):
        """Look up a configuration item"""
        return DEFAULTS.get(key)

    def reload_hosts(self):
        config_file = os.path.join(self.work_dir, 'hosts.ini')
        if os.path.exists(config_file):
            parser = ConfigParser()
            parser.read(config_file)
            for section in parser.sections():
                self.hosts.append({
                    'uuid' : section,
                    'name' : parser.get(section, 'name'),
                    'host' : parser.get(section, 'host'),
                    'port' : parser.get(section, 'port'),
                    'username' : parser.get(section, 'username'),
                    'password' : parser.get(section, 'password'),
                    'group' : parser.get(section, 'group'),
                    'description' : parser.get(section, 'description'),
                    'log' : parser.get(section, 'log'),
                })

    def get_system_font(self):
        """Look up the system font"""
        if self.system_font is not None:
            return self.system_font
        elif 'gconf' not in globals():
            return
        else:
            if self.gconf is None:
                self.gconf = gconf.client_get_default()
            value = self.gconf.get('/desktop/gnome/interface/monospace_font_name')
            self.system_font = value.get_string()
            return self.system_font
