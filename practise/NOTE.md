

# 总学习路径与工程结构

```
# 入口文件, myapp.py
def app(environ, start_response):
    data = b"Hello, World!\n"
    start_response("200 OK", [
        ("Content-Type", "text/plain"),
        ("Content-Length", str(len(data)))
    ])
    return iter([data])

# 执行启动
$ gunicorn -w 4 myapp:app

# 启动Log
 [2014-09-10 10:22:28 +0000] [30869] [INFO] Listening at: http://127.0.0.1:8000 (30869)
 [2014-09-10 10:22:28 +0000] [30869] [INFO] Using worker: sync
 [2014-09-10 10:22:28 +0000] [30874] [INFO] Booting worker with pid: 30874
 [2014-09-10 10:22:28 +0000] [30875] [INFO] Booting worker with pid: 30875
 [2014-09-10 10:22:28 +0000] [30876] [INFO] Booting worker with pid: 30876
 [2014-09-10 10:22:28 +0000] [30877] [INFO] Booting worker with pid: 30877

```
## 执行启动命令后，发生了什么
启动命令`gunicorn -w 4 myapp:app`
看`venv`下`gunicorn`的执行代码
```python

import re
import sys
from gunicorn.app.wsgiapp import run 

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw|\.exe)?$', '', sys.argv[0])
    sys.exit(run())

```

其中要重点学习`sys.exit(run())`
1. sys.exit()
**sys.exit([arg])**
Raise a *SystemExit* exception, signaling an intention to exit the interpreter.

The optional argument arg can be an integer giving the exit status (defaulting to zero), or another type of object. 
If it is an integer, zero is considered **successful termination** and any **nonzero** value is considered *abnormal termination* by shells and the like. Most systems require it to be in the range 0–127, and produce undefined results otherwise. Some systems have a convention for assigning specific meanings to specific exit codes, but these are generally underdeveloped; Unix programs generally use *2* for command line syntax errors and *1* for all other kind of errors. If another type of object is passed, None is equivalent to passing zero, and any other object is printed to stderr and results in an exit code of 1. In particular, *sys.exit("some error message") is a quick way to exit a program when an error occurs*.

Since exit() ultimately “only” raises an exception, it will only exit the process when called from the main thread, and **the exception is not intercepted**. Cleanup actions specified by finally clauses of try statements are honored, and it is possible to intercept the exit attempt at an outer level.

Changed in version 3.6: If an error occurs in the cleanup after the Python interpreter has caught SystemExit (such as an error flushing buffered data in the standard streams), the exit status is changed to 120.
```
简单可以总结为，run()函数会返回执行状态，exit根据得到的状态，决定是否退出进程(sys)

2. gunicorn.app.wsgiapp.run


### 调试Python代码
1. VSCode中的调试
```
cd /Users/jj/Desktop/dev/python/gunicorn-mastery ; /usr/bin/env /opt/homebrew/bin/python3 
/Users/jj/.vscode/extensions/ms-python.debugpy-2024.10.0-darwin-arm64/bundled/libs/debugpy/adapter/../../debugpy/launcher 51156 -- -m gunicorn --workers 2 practise.index:app 
```
1.1 `/usr/bin/env`
1.2 `/opt/homebrew/bin/python3`
1.3 `/Users/jj/.vscode/extensions/ms-python.debugpy-2024.10.0-darwin-arm64/bundled/libs/debugpy/adapter/../../debugpy/launcher 51156`
1.4 `-- -m gunicorn --workers 2 practise.index:app`


## 启动完成后，处于什么状态

## 程序等待状态，发生了什么


# NOTE
1. 学习`venv`的源码



# TODO
- [ ] 什么是 `pre-fork worker model`
> Kimi: 一种在服务器启动时就创建多个进程(线程)的模型，每个进程可以独立地处理客户端请求。这样做的好处是可以提前创建好一定数量的工作进程，避免了高负载情况下动态创建进程的开销
- [ ] Nginx 
    - 业务服务器上层为什么要部署一个代理服务器(HTTP Proxy Server), 如Gunicorn上再部署一个Nginx; 即Nginx的作用、优势
    - 为什么又叫"Reverse Proxy Server"
- WSGI callable: Gunicorn启动的web应用， 入口应该是 WSGI callable的
    + [ ] flask的 app.run(), 是否是WSGI callable


# Python可执行文件
1. pip install gunicorn后，会在venv/bin下生成一个gunicorn的Unix可执行文件
## 问题
1. gunicorn-Unix可执行文件是如何生成的
2. 生成的gunicorn-Unix有什么作用？


# 工程结构
- examples
    - deep 
        - __init__.py: empty
        - test.py
    - frameworks
    - websocket
- gunicorn