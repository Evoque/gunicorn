# -*- coding: utf-8 -

# supported gunicorn workers.
# 基于工作负载的性质和并发需求
SUPPORTED_WORKERS = {
    # 描述：默认的worker类型，一次处理一个请求
    # 场景：适合处理短时间、同步任务的应用程序，不涉及长时间的I/O操作或外部请求。理想用于CPU密集型人物，阻塞时间较短
    # 局限：请求处理时间过长，可能会导致超时，因为它不支持并发连接
    "sync": "gunicorn.workers.sync.SyncWorker",
    
    # 描述：使用Eventlet库进行非阻塞I/O操作
    # 场景：理想用于需要高并发且有大量I/O操作的应用，如网络爬虫或处理多个同时连接
    # 注意：要求所有使用的库与Eventlet兼容，可能需要额外的配置
    "eventlet": "gunicorn.workers.geventlet.EventletWorker",
    
    # 描述：类似于Eventlet，但使用Gevent库，基于协作式多任务处理的greenlet
    # 场景：最佳用于需要高并发的应用，特别是执行多个I/O操作（如数据库查询或API调用）
    # 局限：在许多场景下，Gevent提供比Eventlet更好的性能
    "gevent": "gunicorn.workers.ggevent.GeventWorker",
    
    # 描述：专门为WSGI应用设计的Gevent worker变体
    # 场景：适用于需要异步处理并可受益于Gevent的协作多任务处理的WSGI应用
    "gevent_wsgi": "gunicorn.workers.ggevent.GeventPyWSGIWorker",
    
    # 描述：针对PyWSGI应用优化的Gevent改编版
    # 场景：对于使用PyWSGI构建的需要有效处理并发请求的应用游泳
    "gevent_pywsgi": "gunicorn.workers.ggevent.GeventPyWSGIWorker",
    
    # 描述：设计用于与支持异步网络的Tornado框架配合使用
    # 场景：最适合使用Tornado构建的需要处理长连接或WebSocket的应用
    # 局限：虽然可以为WSGI应用提供服务，但由于潜在的兼容性问题，不建议这样做
    "tornado": "gunicorn.workers.gtornado.TornadoWorker",
    
    # 描述：多线程
    # 场景：适合中等I/O密集型人物（如文件访问或网络调用）的应用，适度的并发可以提高性能，同时内存占用相对较低
    # 优势：相比同步，可以处理更多的并发请求，配置相对简单
    "gthread": "gunicorn.workers.gthread.ThreadWorker"
    
}

'''

Worker Type	    Concurrency Model	    Blocking Behavior	    Ideal Use Case
Sync	        Process-based	        Blocks requests	        Low concurrency, minimal I/O
Eventlet	    Green threads	        Non-blocking	        High concurrency, I/O-bound tasks
Gevent	        Green threads	        Non-blocking	        High concurrency, I/O-bound tasks
Gevent WSGI	    Green threads	        Non-blocking	        WSGI apps needing efficient handling
Gevent PyWSGI   Green threads	        Non-blocking	        Interchangeable with Gevent WSGI
Tornado	        Event-driven	        Requires async code	    Real-time web applications
Gthread	        Thread-based	        Subject to GIL	        I/O-bound tasks with shared memory

'''
# Understanding these differences allows developers to choose the appsopriate worker type based on their
# application's specific needs and workload characteristics. For instances, if your application is heavily
# I/O-bound, using `gevent` or `eventlet` would likely yield better performance than using a synchronous worker.