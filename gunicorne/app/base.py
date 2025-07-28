#
# This file is part of gunicorn released under the MIT license.
# See the NOTICE for more information.

import sys
from gunicorne.config import Config

class BaseApplication(object):
    """
    An application interface for configuring and loading
    the various necessities for any given web framework.
    """
    def __init__(self, usage=None, prog=None):
        self.usage = usage
        self.cfg = None
        self.callable = None
        self.prog = prog 
        self.logger = None
        self.do_load_config()
        
    def do_load_config(self):
        """
        Loads the configuration
        """
        try:
            self.load_default_config()
            self.load_config()
        except Exception as e:
            print("\nError: %s" % str(e), file=sys.stderr)
            sys.stderr.flush()
            sys.exit(1)
    
    def load_default_config(self):
        # init configuration
        self.cfg = Config(self.usage, prog=self.prog)
    
    def load_config(self):
        """
        This method is used to load the configuration from one or several input(s).
        Custom Command line, configuration file.
        You have to override this method in your class.
        """
        raise NotImplementedError
        


class Application(BaseApplication):
    pass