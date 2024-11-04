import inspect
import importlib
import traceback
import re
import os

from gunicorn.workers import SUPPORTED_WORKERS

try:
    import importlib.metadata as importlib_metadata
except (ModuleNotFoundError, ImportError):
    import importlib_metadata

# uri: sync
def load_class(
    uri, 
    default="gunicorn.workers.sync.SyncWorker", 
    section="gunicorn.workers"
):
    if inspect.isclass(uri):
        return uri
    # TODO `egg`是什么场景？
    if uri.startswith("egg:"):
        # uses entry points
        entry_str = uri.split("egg:")[1]
        try:
            dist, name = entry_str.rsplit("#", 1)
        except ValueError:
            dist = entry_str
            name = default

        try:
            return load_entry_point(dist, section, name)
        except Exception:
            pass

    else:
        components = uri.split('.')
        if len(components) == 1:
            while True:
                if uri.startswith("#"):
                    uri = uri[1:]
                
                if uri in SUPPORTED_WORKERS:
                    components = SUPPORTED_WORKERS[uri].split(".")
                    break
                
                try:
                    return load_entry_point("gunicorn", section, uri)
                except Exception:
                    exc = traceback.format_exc()
                    msg = "class uri %r invalid or not found: \n\n[%s]"
                    raise RuntimeError(msg % (uri, exc))
        
        klass = components.pop(-1)
        
        try:
            mod = importlib.import_module('.'.join(components))
        except Exception:
            exc = traceback.format_exc()
            msg = "class uri %r invalid or not found: \n\n[%s]"
            raise RuntimeError(msg % (uri, exc))
        
        return getattr(mod, klass)


def load_entry_point(distribution, group, name):
    dist_obj = importlib_metadata.distribution(distribution)
    eps = [ep for ep in dist_obj.entry_points 
           if ep.group == group and ep.name == name]
    if not eps:
        raise ImportError("Entry point %r not found" % ((group, name),))
    return eps[0].load()

def bytes_to_str(b):
    if isinstance(b, str):
        return b
    return str(b, 'latin1')

def parse_address(netloc, default_port='8000'):
    if re.match(r'unix:(//)?', netloc):
        return re.split(r'unix:(//)?', netloc)[-1]

    if netloc.startswith("fd://"):
        fd = netloc[5:]
        try:
            return int(fd)
        except ValueError:
            raise RuntimeError("%r is not a valid file descriptor." % fd) from None

    if netloc.startswith("tcp://"):
        netloc = netloc.split("tcp://")[1]

    host, port = netloc, default_port

    if '[' in netloc and ']' in netloc:
        host = netloc.split(']')[0][1:]
        port = (netloc.split(']:') + [default_port])[1]
    elif ':' in netloc:
        host, port = (netloc.split(':') + [default_port])[:2]
    elif netloc == "":
        host, port = "0.0.0.0", default_port

    try:
        port = int(port)
    except ValueError:
        raise RuntimeError("%r is not a valid port number." % port)

    return host.lower(), port

positionals = (
    inspect.Parameter.POSITIONAL_ONLY,
    inspect.Parameter.POSITIONAL_OR_KEYWORD,
)

def get_arity(f):
    sig = inspect.signature(f)
    arity = 0
    
    for param in sig.parameters.values():
        if param.kind in positionals:
            arity += 1
    
    return arity

def getcwd():
    ''' get current path, try to use PWD env first '''
    try:
        a = os.stat(os.environ['PWD'])
        b = os.stat(os.getcwd())
        
        if a.st_ino == b.st_ino and a.st_dev == b.st_dev:
            cwd = os.environ['PWD']
        else:
            cwd = os.getcwd()
    except Exception:
        cwd = os.getcwd()
    
    return cwd