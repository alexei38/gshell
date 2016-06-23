import gconf
import gtk

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
    'copy_on_selection'     : True,
    'alternate_screen_scroll': True,
    'inactive_color_offset': 0.8,
    'disable_real_transparency' : True,
    'keybinder': {
        'zoom_in'          : '<Shift><Control>plus',
        'zoom_out'         : '<Shift><Control>minus',
        'zoom_normal'      : '<Shift><Control>0',
        'close_term'       : '<Shift><Control>w',
        'copy'             : '<Shift><Control>c',
        'paste'            : '<Shift><Control>v',
        'new_tab'          : '<Shift><Control>t',
        'next_tab'         : '<Control>Page_Down',
        'prev_tab'         : '<Control>Page_Up',
        'full_screen'      : 'F11',
        'reset'            : '<Shift><Control>r',
        'reset_clear'      : '<Shift><Control>g',
    }
}


class Config(object):
    def __init__(self, *args, **kwds):
        super(Config, self).__init__(*args, **kwds)
        self.system_font = None
        self.gconf = None

    def __getitem__(self, key):
        """Look up a configuration item"""
        DEFAULTS.get(key)

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