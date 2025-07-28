
import argparse
import copy
import sys
import shlex
import os
import textwrap

KNOWN_SETTINGS = []
PLATFORM = sys.platform

def make_settings(ignore=None):
    settings = {}
    ignore = ignore or ()
    for s in KNOWN_SETTINGS:
        setting = s()
        if setting.name in ignore:
            continue
        settings[setting.name] = setting.copy()
    return settings
    

class Config(object):

    def __init__(self, usage=None, prog=None):
        self.settings = make_settings()
        self.usage = usage
        self.prog = prog or os.path.basename(sys.argv[0])
        self.env_orig = os.environ.copy()
        
    def __str__(self):
        lines = []
        kmax = max(len(k) for k in self.settings)
        for k in sorted(self.settings):
            v = self.settings[k].value
            if callable(v):
                v = "<{}()>".format(v.__qualname__)
            lines.append("{k:{kmax}} = {v}".format(k=k,v=v,kmax=kmax))
        return "\n".join(lines)
    
    def __getattr__(self, name):
        if name not in self.settings:
            raise AttributeError("No configuration setting for: %s" % name)
        return self.settings[name].get()
    
    def __setattr__(self, name, value):
        if name != "settings" and name in self.settings:
            raise AttributeError("Invalid access!")
        super().__setattr__(name, value)
        
    def set(self, name, value):
        if name not in self.settings:
            raise AttributeError("No configuration setting for: %s" % name)
        self.settings[name].set(value)
        
    def get_cmd_args_from_env(self):
        if 'GUNICORN_CMD_ARGS' in self.env_orig:
            return shlex.split(self.env_orig['GUNICORN_CMD_ARGS'])
        return []
    
    def parser(self):
        kwargs = {
            "usage": self.usage,
            "prog": self.prog
        }
        parser = argparse.ArgumentParser(**kwargs)
        parser.add_argument("-v", "--version",
                            action="version", default=argparse.SUPPRESS,
                            version="%(prog)s (version " + __version__ + ")\n",
                            help="show program's version number and exit")
        parser.add_argument("args", nargs="*", help=argparse.SUPPRESS)
        
        keys = sorted(self.settings, key=self.settings.__getitem__)
        for k in keys:
            self.settings[k].add_option(parser)
            
        return parser
    
    @property
    def worker_class_str(self):
        uri = self.settings["worker_class"].get()
        
        # are we using a threaded worker?
        is_sync = uri.endswith('SyncWorker') or uri == 'sync'
        if is_sync and self.threads > 1:
            return "gthread"
        return uri
    
    @property
    def worker_class(self):
        
        worker_class = util.load_class(self.worker_class_str)
        if hasattr(worker_class, "setup"):
            worker_class.setup()
        return worker_class
    
    
        
    
        
        
class Setting(object):
    name = None
    value = None
    section = None
    cli = None
    validator = None
    type = None
    meta = None
    action = None
    default = None
    short = None
    desc = None
    nargs = None
    const = None  
    
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        
        cls.order = len(KNOWN_SETTINGS)
        cls.validator = staticmethod(cls.validator)
        cls.fmt_desc(getattr(cls, 'desc', ''))
        KNOWN_SETTINGS.append(cls)
        
    def __init__(self):
        if self.default is not None:
            self.set(self.default)
    
    @classmethod
    def fmt_desc(cls, desc):
        desc = textwrap.dedent(desc).strip()
        setattr(cls, "desc", desc)
        setattr(cls, "short", desc.splitlines()[0])
        
    def add_option(self, parser):
        if not self.cli:
            return
        args = tuple(self.cli)
        
        help_txt = "%s [%s]" % (self.short, self.default)
        help_txt = help_txt.replace("%", "%%")
        
        kwargs = {
            "dest": self.name,
            "action": self.action or "store",
            "type": self.type or str, 
            "default": None, 
            "help": help_txt
        }
        
        if kwargs["action"] != "store":
            kwargs.pop("type")
            
        if self.meta is not None:
            kwargs['metavar'] = self.meta
        if self.nargs is not None: 
            kwargs['nargs'] = self.nargs
        if self.const is not None:
            kwargs["const"] = self.const
            
        parser.add_argument(*args, **kwargs)
        
        
        
    
    def copy(self):
        return copy.copy(self)
    
    def get(self):
        return self.value
        
    def set(self, val):
        if not callable(self.validator):
            raise TypeError("Invalid validator: %s " % self.name)
        self.value = self.validator(val)
        
    def __lt__(self, other):
        return (self.section == other.section and
                self.order < other.order)
    
    __cmp__ = __lt__
    
    def __repr__(self):
        return "<%s.%s object at %x with value %r>" % (
            self.__class__.__module__,
            self.__class__.__name__,
            id(self),
            self.value
        )
        
        
def validate_string(val):
    if val is None:
        return None
    if not isinstance(val, str):
        raise TypeError("Not a string: %s" % val)
    return val.strip()

class ConfigFile(Setting):
    name = "config"
    section = "Config File"
    cli = ["-c", "--config"]
    meta = "CONFIG"
    validator = validate_string
    default = "./gunicorn.conf.py"
    desc = """\
        :ref:`The Gunicorn config file<configuration_file>`.

        A string of the form ``PATH``, ``file:PATH``, or ``python:MODULE_NAME``.

        Only has an effect when specified on the command line or as part of an
        application specific configuration.

        By default, a file named ``gunicorn.conf.py`` will be read from the same
        directory where gunicorn is being run.

        .. versionchanged:: 19.4
           Loading the config from a Python module requires the ``python:``
           prefix.
        """
        
    