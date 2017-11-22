# -*- coding: utf-8 -*-

import gtk

PROGRAM_NAME = 'Gshell'
VERSION = '0.0.1-44'
AUTHOR = 'Alexei Margasov'
COMMENT = 'Terminal emulator'
WEBSITE = 'https://github.com/alexei38/gshell'

class AboutDialog(gtk.AboutDialog):

    def __init__(self, *args):
        super(AboutDialog, self).__init__()
        self.set_program_name(PROGRAM_NAME)
        self.set_version(VERSION)
        self.set_copyright(AUTHOR)
        self.set_comments(COMMENT)
        self.set_website(WEBSITE)
        self.run()
        self.destroy()
