# -*- coding: utf-8 -
"""
TODO config.py的设计思想
"""


import argparse
import copy
import grp
import inspect
import os
import pwd
import re
import shlex
import ssl
import sys
import textwrap

from gunicorn import __version__, util
from gunicorn.errors import ConfigError
from gunicorn.reloader import reloader_engines


KNOWN_SETTINGS = []
PLATFORM = sys.platform


def make_settings(ignore=None):
    settings = {}
    ignore = ignore or {}
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
            lines.append("{k:{kmax}} = {v}".format(k=k, v=v, kmax=kmax))
        return "\n".join(lines)

    def __getattr__(self, name):
        if name not in self.settings:
            raise AttributeError("No configuration setting for: %s" % name)
        return self.settings[name].get()

    def __setattr(self, name, value):
        if name != "settings" and name in self.settings:
            raise AttributeError("Invalid access!")
        super().__setattr__(name, value)

    def set(self, name, value):
        if name not in self.settings:
            raise AttributeError("No configuration setting for: %s" % name)
        self.settings[name].set(value)

    def get_cmd_args_from_env(self):
        if "GUNICORN_CMD_ARGS" in self.env_orig:
            return shlex.split(self.env_orig["GUNICORN_CMD_ARGS"])
        return []

    def parser(self):
        kwargs = {"usage": self.usage, "prog": self.prog}
        parser = argparse.ArgumentParser(**kwargs)
        parser.add_argument(
            "-v",
            "--version",
            action="version",
            default=argparse.SUPPRESS,
            version="%(prog)s (version " + __version__ + ")\n",
            help="show program's version number and exit",
        )
        parser.add_argument("args", nargs="*", help=argparse.SUPPRESS)

        keys = sorted(self.settings, key=self.settings.__getitem__)
        for k in keys:
            self.settings[k].add_option(parser)

        return parser

    @property
    def worker_class_str(self):
        uri = self.settings["worker_class"].get()

        # are we using a threaded worker?
        is_sync = uri.endswith("SyncWorker") or uri == "sync"
        if is_sync and self.threads > 1:
            return "gthread"
        return uri

    @property
    def worker_class(self):
        uri = self.settings["worker_class"].get()

        # are we using a threaded worker?
        is_sync = uri.endswith("SyncWorker") or uri == "sync"
        if is_sync and self.threads > 1:
            uri = "gunicorn.workers.gthread.ThreadWorker"

        worker_class = util.load_class(uri)
        if hasattr(worker_class, "setup"):
            worker_class.setup()
        return worker_class

    @property
    def address(self):
        s = self.settings["bind"].get()
        return [util.parse_address(util.bytes_to_str(bind)) for bind in s]

    @property
    def uid(self):
        return self.settings["user"].get()

    @property
    def gid(self):
        return self.settings["group"].get()

    @property
    def proc_name(self):
        pn = self.settings["proc_name"].get()
        if pn is not None:
            return pn
        else:
            return self.settings["default_proc_name"].get()

    @property
    def logger_class(self):
        uri = self.settings["logger_class"].get()
        if uri == "simple":
            # support the default
            uri = LoggerClass.default

        # if default logger is in use, and statsd is on, automagically switch
        # to the stats logger
        if uri == LoggerClass.default:
            if (
                "statsd_host" in self.settings
                and self.settings["statsd_host"].value is not None
            ):
                uri = "gunicorn.instrument.statsd.Statsd"

        logger_class = util.load_class(
            uri, default="gunicorn.glogging.Logger", section="gunicorn.loggers"
        )

        if hasattr(logger_class, "install"):
            logger_class.install()

        return logger_class

    @property
    def is_ssl(self):
        return self.certfile or self.keyfile

    @property
    def ssl_options(self):
        opts = {}
        for name, value in self.settings.items():
            if value.section == "SSL":
                opts[name] = value.get()
        return opts

    @property
    def env(self):
        raw_env = self.settings["raw_env"].get()
        env = {}

        if not raw_env:
            return env

        for e in raw_env:
            s = util.bytes_to_str(e)
            try:
                k, v = s.split("=", 1)
            except ValueError:
                raise RuntimeError("environment setting %r invalid" % s)

            env[k] = v

        return env

    @property
    def sendfile(self):
        if self.settings["senfile"].get() is not None:
            return False

        if "SENDFILE" in os.environ:
            sendfile = os.environ["SENDFILE"].lower()
            return sendfile in ["y", "1", "yes", "true"]

        return True

    @property
    def reuse_port(self):
        return self.settings["reuse_port"].get()

    @property
    def paste_global_conf(self):
        raw_global_conf = self.settings["raw_paste_global_conf"].get()
        if raw_global_conf is None:
            return None

        global_conf = {}
        for e in raw_global_conf:
            s = util.bytes_to_str(e)
            try:
                k, v = re.split(r"(?<!\\)=", s, 1)
            except ValueError:
                raise RuntimeError("environment setting %r invalid" % s)
            k = k.replace("\\=", "=")
            v = v.replace("\\=", "=")
            global_conf[k] = v

        return global_conf


"""
TODO 
问题:
1. `__new__`参数为什么是`name`,`bases`,`attrs`，及调用super_new也用这些参数
2. `__new__`中什么情况下满足`parents`不为空，不为空时剩余代码的作用是什么
3. 用SettingMeta(type)、Setting(object)这种方式声明的设计模式是什么
"""


class SettingMeta(type):
    def __new__(cls, name, bases, attrs):
        super_new = super().__new__
        parents = [b for b in bases if isinstance(b, SettingMeta)]
        if not parents:
            return super_new(cls, name, bases, attrs)

        attrs["order"] = len(KNOWN_SETTINGS)
        attrs["validator"] = staticmethod(attrs["validator"])

        new_class = super_new(cls, name, bases, attrs)
        new_class.fmt_desc(attrs.get("desc", ""))
        KNOWN_SETTINGS.append(new_class)
        return new_class

    def fmt_desc(cls, desc):
        desc = textwrap.dedent(desc).strip()
        setattr(cls, "desc", desc)
        setattr(cls, "short", desc.splitlines()[0])


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

    def __init__(self):
        if self.default is not None:
            self.set(self.default)

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
            "help": help_txt,
        }

        if self.meta is not None:
            kwargs["metavar"] = self.meta

        if kwargs["action"] != "store":
            kwargs.pop("type")

        if self.nargs is not None:
            kwargs["nargs"] = self.nargs

        if self.const is not None:
            kwargs["const"] = self.const

        parser.add_argument(*args, **kwargs)

    def copy(self):
        return copy.copy(self)

    def get(self):
        return self.value

    def set(self, val):
        if not callable(self.validator):
            raise TypeError("Invalid validator: %s" % self.name)
        self.value = self.validator(val)

    def __lt__(self, other):
        return self.section == other.section and self.order < other.order

    __cmp__ = __lt__

    def __repr__(self):
        return "<%s.%s object at %x with value %r>" % (
            self.__class__.__module__,
            self.__class__.__name__,
            id(self),
            self.value,
        )

Setting = SettingMeta("Setting", (SettingMeta,), {})


def validate_bool(val):
    if val is None:
        return

    if isinstance(val, bool):
        return val
    if not isinstance(val, str):
        raise TypeError("Invalid type for casting: %s" % val)
    if val.lower().strip() == "true":
        return True
    elif val.lower().strip() == "false":
        return False
    else:
        raise ValueError("Invalid boolean: %s" % val)

def validate_dict(val):
    if not isinstance(val, dict):
        raise TypeError("Value is not a dictionary: %s " % val)
    return val

def validate_pos_int(val):
    if not isinstance(val, int):
        val = int(val, 0)
    else:
        val = int(val)

    if val < 0:
        raise ValueError("Value must be positive: %s" % val)
    return val

def validate_string(val):
    if val is None:
        return None
    if not isinstance(val, str):
        raise TypeError("Not a string: %s" % val)
    return val.strip()

def validate_file_exists(val):
    if val is None:
        return None
    if not os.path.exists(val):
        raise ValueError("File %s does not exists." % val)
    return val

def validate_list_string(val):
    if not val:
        return []

    # legacy syntax
    if isinstance(val, str):
        val = [val]

    return [validate_string(v) for v in val]

def validate_list_of_existing_files(val):
    return [validate_file_exists(v) for v in validate_list_string(val)]

def validate_string_to_list(val):
    val = validate_string(val)

    if not val:
        return []

    return [v.strip() for v in val.split(".") if v]

def validate_class(val):
    if inspect.isfunction(val) or inspect.ismethod(val):
        val = val()
    if inspect.isclass(val):
        return val
    return validate_string(val)

def validate_callable(arity):
    def _validate_callable(val):
        if isinstance(val, str):
            try:
                mod_name, obj_name = val.rsplit(".", 1)
            except ValueError:
                raise TypeError(
                    "Value '%s' is not import string. "
                    "Format: module[.submodules...].object" % val
                )

            try:
                mod = __import__(mod_name, fromlist=[obj_name])
                val = getattr(mod, obj_name)
            except ImportError as e:
                raise TypeError(str(e))
            except AttributeError:
                raise TypeError("Can not load '%s' from '%s'" "" % (obj_name, mod_name))

        if not callable(val):
            raise TypeError("Value is not callable: %s" % val)
        if arity != -1 and arity != util.get_arity(val):
            raise TypeError("Value must have an arity of %s" % arity)
        return val

    return _validate_callable

def validate_user(val):
    if val is None:
        return os.geteuid()
    if isinstance(val, int):
        return val
    elif val.isdigit():
        return int(val)
    else:
        try:
            return pwd.getpwnam(val).pw_uid
        except KeyError:
            raise ConfigError("No such user: '%s'" % val)

def validate_group(val):
    if val is None:
        return os.getegid()

    if isinstance(val, int):
        return val
    elif val.isdigit():
        return int(val)
    else:
        try:
            return grp.getgrnam(val).gr_gid
        except KeyError:
            raise ConfigError("No such group: '%s'" % val)

def validate_post_request(val):
    val = validate_callable(-1)(val)

    largs = util.get_arity(val)
    if largs == 4:
        return val
    elif largs == 3:
        return lambda worker, req, env, _r: val(worker, req, env)
    elif largs == 2:
        return lambda worker, req, _e, _r: val(worker, req)
    else:
        raise TypeError("Value must have an arity of 4")

def validate_chdir(val):
    val = validate_string(val)

    path = os.path.abspath(os.path.normpath(os.path.join(util.getcwd(), val)))

    if not os.path.exists(path):
        raise ConfigError("can't chdir to %r" % val)

    return path

def validate_statsd_address(val):
    val = validate_string(val)
    if val is None:
        return None

    # As of major release 20, `util.parse_address` would recognize unix:PORT
    # as a UDS address, breaking backwards compatibility. We defend against
    # that regression here (this is also unit-tested)
    # Feel free to remove in the next major release.
    unix_hostname_regression = re.match(r"^unix:(\d+)$", val)
    if unix_hostname_regression:
        return ("unix", int(unix_hostname_regression.group(1)))

    try:
        address = util.parse_address(val, default_port="8125")
    except RuntimeError:
        raise TypeError(("Value must be one of ('host:port', 'unix://PATH')"))

    return address

def validate_reload_engine(val):
    if val not in reloader_engines:
        raise ConfigError("Invalid reload_engine: %r" % val)

    return val

def get_default_config_file():
    config_path = os.path.join(os.path.abspath(os.getcwd()), "gunicorn.conf.py")
    if os.path.exists(config_path):
        return config_path
    return None

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
           
class WSGIApp(Setting):
    name = "wsgi_app"
    section = "Config File"
    meta = "STRING"
    validator = validate_string
    default = None
    desc = """\
        A WSGI application path in pattern ``$(MODULE_NAME):$(VARIABLE_NAME)``,
        
        .. versionadded:: 20.1.0
        """
        
class Bind(Setting):
    name = "bind"
    action = "append"
    section = "Server Socket"
    cli = ["-b", "--bind"]
    meta = "ADDRESS"
    validator = validate_list_string
    
    if 'PORT' in os.environ:
        default = ['0.0.0.0:{0}'.format(os.environ.get('PORT'))]
    else:
        default = ['127.0.0.1:8000']
        
    desc = """\
        The socket to bind.
        
        A string of the form: ``HOST``, ``HOST:PORT``, ``unix:PATH``, ``fd://FD``.
        An IP is a valid ``HOST``.
        
        .. versionchanged:: 20.0
           Support for ``fd://FD`` got added.
        
        Multiple addresses can be bound. ex.::
        
            $ gunicorn -b 127.0.0.1:8000 -b [::1]:8000 test:app
            
        will bind the `test:app` application on localhost both on ipv6 and 
        ipv4 interfaces.
        
        If the ``PORT`` environment variable is defined, the default is 
        ``['0.0.0.0:$PORT']``. If it is not defined, the default is 
        ``['127.0.0.1:8000']``
        """

# 「待处理队列」｜「连接请求队列」，特别是在TCP协议时，设置可以同时等待处理的连接请求的最大数量
# listen
class Backlog(Setting):
    name = "backlog"
    section = "Server Socket"
    cli = ["--backlog"]
    meta = "INT"
    validator = validate_pos_int
    type = int
    default = 2048
    desc = """\
        The maximum number of pending connections.
        
        This refers to the number of clients that can be waiting to be served.
        Exceeding this number results in the client getting an error when attempting
        to connect. 
        It should only affect servers under significant load.
        
        Must be positive integer. Generally set in the 64-2048 range.
        """
        
class Workers(Setting):
    name = "workers"
    section = "Worker Processes"
    cli = ["-w", "--workers"]
    meta = "INT"
    validator = validate_pos_int
    type = int
    default = int(os.environ.get("WEB_CONCURRENCY", 1))
    desc = """\
        The number of worker processes for handling requests.
        
        A positive integer generally in the ``2-4 x $(NUM_CORES)`` range.
        You'll want to vary this a bit to find the best for your particular
        application's work load.
        
        By default, the value of the ``WEB_CONCURRENCY`` environment variable,
        which is set by some Platform-as-a-Service providers such as Heroku. If
        it is not defined, the default is ``1``.
        """
        
class WorkerClass(Setting):
    name = "worker_class"
    section = "Worker Processes"
    cli = ["-k", "--worker-class"]
    meta = "STRING"
    validator = validate_class
    default = "sync"
    desc = """\
        The type of workers to use. 
        
        The default calss (``sync``) should handle most "normal" types of workloads.
        You'll want to read :doc:`design` for information on when you might want to 
        choose one of the other worker classes. Required libraries may be installed 
        using setuptools' ``extras_require`` feature.
        
        A string referring to one of the following bundled classes:
        
        * ``sync``
        * ``eventlet`` - Requires eventlet >= 0.24.1 (or install it via ``pip install gunicorn[eventlet]``)
        * ``gevent``   - Requires gevent >= 1.4 (or install it via ``pip install gunicorn[gevent]``)
        * ``tornado``  - Requires tornado >= 0.2 (or install it via ``pip install gunicorn[tornado]``)
        * ``gthread``  - Python 2 requires the futures package to be installed (or install it via ``pip install gunicorn[gthread]``)
        
        Optionally, you can provide your own worker by giving Gunicorn a Python path to 
        a subclass of ``gunicorn.workers.base.Worker``. 
        This alternative syntax will load the gevent class:``gunicorn.workers.ggevent.GeventWorker``.
        """

class WorkerThreads(Setting):
    name = "threads"
    section = "Worker Processes"
    cli = ["--threads"]
    meta = "INT"
    validator = validate_pos_int
    type = int 
    default = 1
    desc = """\
        The number of worker threads for handling requests.
        
        Run each worker with the specifid number of threads.
        
        A positive integer generally in the ``2-4 x $(NUM_CORES)`` range.
        You'll want to vary this a bit to find the best for your particular 
        application's work load.
        
        If it is not defined, the default is ``1``.
        
        This setting only affects the Gthread worker type.
        
        .. note::
            If you try to use the ``sync`` worker type and set the ``threads``
            setting to more than 1, the ``gthread`` worker type will be used instead.
        """

class WorkerConnections(Setting):
    name = "worker_connections"
    section = "Worker Processes"
    cli = ["--worker-connections"]
    meta = "INT"
    validator = validate_pos_int
    type = int
    default = 1000
    desc = """\
        The maximum number of simultaneous clients.
        
        This setting only affects the ``gthread``, ``eventlet`` and ``gevent`` worker types.
        """

class MaxRequests(Setting):
    name = "max_requests"
    section = "Worker Processes"
    cli = ["--max-requests"]
    meta = "INT"
    validator = validate_pos_int
    type = int
    default = 0
    desc = """\
        The maximum number of requests a worker will process before restarting.
        
        Any value greater than zero will limit the number of requests a worker
        will process before automatically restarting.
        This is a simple method to help limit the damage of memory leaks.
        
        If this is set to zero (the default) then the automatic worker 
        restarts are disabled.
        """
        
class MaxRequestsJitter(Setting):
    name = "max_requests_jitter"
    section = "Worker Processes"
    cli = ["--max-requests-jitter"]
    meta = "INT"
    validator = validate_pos_int
    type = int
    default = 0
    desc = """\
        The maximum jitter to add to the *max_requests* setting.

        The jitter causes the restart per worker to be randomized by
        ``randint(0, max_requests_jitter)``. This is intended to stagger worker
        restarts to avoid all workers restarting at the same time.

        .. versionadded:: 19.2
        """

class Timeout(Setting):
    name = "timeout"
    section = "Worker Processes"
    cli = ["-t", "--timeout"]
    meta = "INT"
    validator = validate_pos_int
    type = int
    default = 30
    desc = """\
        Workers silent for more than this many seconds are killed and restarted.

        Value is a positive number or 0. Setting it to 0 has the effect of
        infinite timeouts by disabling timeouts for all workers entirely.

        Generally, the default of thirty seconds should suffice. Only set this
        noticeably higher if you're sure of the repercussions for sync workers.
        For the non sync workers it just means that the worker process is still
        communicating and is not tied to the length of time required to handle a
        single request.
        """
        
class GracefulTimeout(Setting):
    name = "graceful_timeout"
    section = "Worker Processes"
    cli = ["--graceful-timeout"]
    meta = "INT"
    validator = validate_pos_int
    type = int
    default = 30
    desc = """\
        Timeout for graceful workers restart.

        After receiving a restart signal, workers have this much time to finish
        serving requests. Workers still alive after the timeout (starting from
        the receipt of the restart signal) are force killed.
        """

class Keepalive(Setting):
    name = "keepalive"
    section = "Worker Processes"
    cli = ["--keep-alive"]
    meta = "INT"
    validator = validate_pos_int
    type = int
    default = 2
    desc = """\
        The number of seconds to wait for requests on a Keep-Alive connection.

        Generally set in the 1-5 seconds range for servers with direct connection
        to the client (e.g. when you don't have separate load balancer). When
        Gunicorn is deployed behind a load balancer, it often makes sense to
        set this to a higher value.

        .. note::
           ``sync`` worker does not support persistent connections and will
           ignore this option.
        """  

class LimitRequestLine(Setting):
    name = "limit_request_line"
    section = "Security"
    cli = ["--limit-request-line"]
    meta = "INT"
    validator = validate_pos_int
    type = int
    default = 4094
    desc = """\
        The maximum size of HTTP request line in bytes.

        This parameter is used to limit the allowed size of a client's
        HTTP request-line. Since the request-line consists of the HTTP
        method, URI, and protocol version, this directive places a
        restriction on the length of a request-URI allowed for a request
        on the server. A server needs this value to be large enough to
        hold any of its resource names, including any information that
        might be passed in the query part of a GET request. Value is a number
        from 0 (unlimited) to 8190.

        This parameter can be used to prevent any DDOS attack.
        """

class LimitRequestFields(Setting):
    name = "limit_request_fields"
    section = "Security"
    cli = ["--limit-request-fields"]
    meta = "INT"
    validator = validate_pos_int
    type = int
    default = 100
    desc = """\
        Limit the number of HTTP headers fields in a request.

        This parameter is used to limit the number of headers in a request to
        prevent DDOS attack. Used with the *limit_request_field_size* it allows
        more safety. By default this value is 100 and can't be larger than
        32768.
        """ 

class LimitRequestFieldSize(Setting):
    name = "limit_request_field_size"
    section = "Security"
    cli = ["--limit-request-field_size"]
    meta = "INT"
    validator = validate_pos_int
    type = int
    default = 8190
    desc = """\
        Limit the allowed size of an HTTP request header field.

        Value is a positive number or 0. Setting it to 0 will allow unlimited
        header field sizes.

        .. warning::
           Setting this parameter to a very high or unlimited value can open
           up for DDOS attacks.
        """   

class Reload(Setting):
    name = "reload"
    section = 'Debugging'
    cli = ['--reload']
    validator = validate_bool
    action = 'store_true'
    default = False

    desc = '''\
        Restart workers when code changes.

        This setting is intended for development. It will cause workers to be
        restarted whenever application code changes.

        The reloader is incompatible with application preloading. When using a
        paste configuration be sure that the server block does not import any
        application code or the reload will not work as designed.

        The default behavior is to attempt inotify with a fallback to file
        system polling. Generally, inotify should be preferred if available
        because it consumes less system resources.

        .. note::
           In order to use the inotify reloader, you must have the ``inotify``
           package installed.
        '''
    
class ReloadEngine(Setting):
    name = "reload_engine"
    section = "Debugging"
    cli = ["--reload-engine"]
    meta = "STRING"
    validator = validate_reload_engine
    default = "auto"
    desc = """\
        The implementation that should be used to power :ref:`reload`.

        Valid engines are:

        * ``'auto'``
        * ``'poll'``
        * ``'inotify'`` (requires inotify)

        .. versionadded:: 19.7
        """
    
class ReloadExtraFiles(Setting):
    name = "reload_extra_files"
    action = "append"
    section = "Debugging"
    cli = ["--reload-extra-file"]
    meta = "FILES"
    validator = validate_list_of_existing_files
    default = []
    desc = """\
        Extends :ref:`reload` option to also watch and reload on additional files
        (e.g., templates, configurations, specifications, etc.).

        .. versionadded:: 19.8
        """

class Spew(Setting):
    name = "spew"
    section = "Debugging"
    cli = ["--spew"]
    validator = validate_bool
    action = "store_true"
    default = False
    desc = """\
        Install a trace function that spews every line executed by the server.

        This is the nuclear option.
        """
    
class ConfigCheck(Setting):
    name = "check_config"
    section = "Debugging"
    cli = ["--check-config"]
    validator = validate_bool
    action = "store_true"
    default = False
    desc = """\
        Check the configuration and exit. The exit status is 0 if the
        configuration is correct, and 1 if the configuration is incorrect.
        """
    
class PrintConfig(Setting):
    name = "print_config"
    section = "Debugging"
    cli = ["--print-config"]
    validator = validate_bool
    action = "store_true"
    default = False
    desc = """\
        Print the configuration settings as fully resolved. Implies :ref:`check-config`.
        """

class PreloadApp(Setting):
    name = "preload_app"
    section = "Server Mechanics"
    cli = ["--preload"]
    validator = validate_bool
    action = "store_true"
    default = False
    desc = """\
        Load application code before the worker processes are forked.

        By preloading an application you can save some RAM resources as well as
        speed up server boot times. Although, if you defer application loading
        to each worker process, you can reload your application code easily by
        restarting workers.
        """
    
class Sendfile(Setting):
    name = "sendfile"
    section = "Server Mechanics"
    cli = ["--no-sendfile"]
    validator = validate_bool
    action = "store_const"
    const = False

    desc = """\
        Disables the use of ``sendfile()``.

        If not set, the value of the ``SENDFILE`` environment variable is used
        to enable or disable its usage.

        .. versionadded:: 19.2
        .. versionchanged:: 19.4
           Swapped ``--sendfile`` with ``--no-sendfile`` to actually allow
           disabling.
        .. versionchanged:: 19.6
           added support for the ``SENDFILE`` environment variable
        """
        
class ReusePort(Setting):
    name = "reuse_port"
    section = "Server Mechanics"
    cli = ["--reuse-port"]
    validator = validate_bool
    action = "store_true"
    default = False

    desc = """\
        Set the ``SO_REUSEPORT`` flag on the listening socket.

        .. versionadded:: 19.8
        """
        
class Chdir(Setting):
    name = "chdir"
    section = "Server Mechanics"
    cli = ["--chdir"]
    validator = validate_chdir
    default = util.getcwd()
    default_doc = "``'.'``"
    desc = """\
        Change directory to specified directory before loading apps.
        """
        
class Daemon(Setting):
    name = "daemon"
    section = "Server Mechanics"
    cli = ["-D", "--daemon"]
    validator = validate_bool
    action = "store_true"
    default = False
    desc = """\
        Daemonize the Gunicorn process.

        Detaches the server from the controlling terminal and enters the
        background.
        """
        
class Env(Setting):
    name = "raw_env"
    action = "append"
    section = "Server Mechanics"
    cli = ["-e", "--env"]
    meta = "ENV"
    validator = validate_list_string
    default = []

    desc = """\
        Set environment variables in the execution environment.

        Should be a list of strings in the ``key=value`` format.

        For example on the command line:

        .. code-block:: console

            $ gunicorn -b 127.0.0.1:8000 --env FOO=1 test:app

        Or in the configuration file:

        .. code-block:: python

            raw_env = ["FOO=1"]
        """
        
class Pidfile(Setting):
    name = "pidfile"
    section = "Server Mechanics"
    cli = ["-p", "--pid"]
    meta = "FILE"
    validator = validate_string
    default = None
    desc = """\
        A filename to use for the PID file.

        If not set, no PID file will be written.
        """

class WorkerTmpDir(Setting):
    name = "worker_tmp_dir"
    section = "Server Mechanics"
    cli = ["--worker-tmp-dir"]
    meta = "DIR"
    validator = validate_string
    default = None
    desc = """\
        A directory to use for the worker heartbeat temporary file.

        If not set, the default temporary directory will be used.

        .. note::
           The current heartbeat system involves calling ``os.fchmod`` on
           temporary file handlers and may block a worker for arbitrary time
           if the directory is on a disk-backed filesystem.

           See :ref:`blocking-os-fchmod` for more detailed information
           and a solution for avoiding this problem.
        """

class User(Setting):
    name = "user"
    section = "Server Mechanics"
    cli = ["-u", "--user"]
    meta = "USER"
    validator = validate_user
    default = os.geteuid()
    default_doc = "``os.geteuid()``"
    desc = """\
        Switch worker processes to run as this user.

        A valid user id (as an integer) or the name of a user that can be
        retrieved with a call to ``pwd.getpwnam(value)`` or ``None`` to not
        change the worker process user.
        """



class LoggerClass(Setting):
    name = "logger_class"
    section = "Logging"
    cli = ["--logger-class"]
    meta = "STRING"
    validator = validate_class
    default = "gunicorn.glogging.Logger"
    desc = """\
        The logger you want to use to log events in Gunicorn.
        
        The default class (``gunicorn.glogging.Logger``) handles most 
        normal usages in logging. It provides error and access logging.
        
        You can provide your own logger by giving Gunicorn a Python path to a 
        class that quacks like ``gunicorn.glogging.Logger``
        """
