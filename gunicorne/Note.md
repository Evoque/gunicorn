1. 执行`python -m gunicorne`时，`__init__.py`仍然`__main__.py`先执行。
2. `gunicorn`是如何与各种Web框架协作的(Django, Flask, FastAPI等)，CGI？WSGI？
3. python与C如何协作的，或者说，C语言是如何实现python的部分模块的，如`sys`?

### `__new__`与`__init__`的区别与关系
1. `__new__`: 类方法(接收cls参数)，负责创建实例对象(分配内存空间),并返回创建的实例；
    1.1: 若返回的不是当前类的实例(None或其他类的实例)，则__init__不会被调用。
2. `__init__`: 实例方法(接收self参数), 负责初始化已创建的实例(设置属性)，无返回值(若返回非None会报错).




# QA
1. `config.py -> make_settings`中setting.copy(): 每个Config都有自己独立的配置项副本，独立修改不影响其他实例；
