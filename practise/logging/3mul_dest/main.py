import logging

# 如果不basicConfig，则默认level=WARNING，所以消息无法传递到Handler中
# logging.basicConfig(level=logging.DEBUG, format='--%(name)-10s %(levelname)-8s %(message)s', datefmt="%m-%d %H:%M")

root_logger = logging.getLogger('')

f = logging.FileHandler("myapp1.log", "w")
f.setLevel(logging.DEBUG)
f.setFormatter(logging.Formatter('%(asctime)s %(name)-6s %(levelname)-8s %(message)s'))
root_logger.addHandler(f)

# console = logging.StreamHandler()
# console.setLevel(logging.INFO)
# console.setFormatter(logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s'))
# root_logger.addHandler(console)


# Now, we can log to the root logger, or any other logger. First the root...
logging.info('[logging] Jackdaws love my big sphinx of quartz.')
# root_logger.info('[root logger] Jackdaws love my big sphinx of quartz.')

# Now, define a couple of other loggers which might represent areas in your
# application:

# logger1 = logging.getLogger('myapp.area1')
# logger2 = logging.getLogger('myapp.area2')

# logger1.debug('Quick zephyrs blow, vexing daft Jim.')
# logger1.info('How quickly daft jumping zebras vex.')
# logger2.warning('Jail zesty vixen who grabbed pay from quack.')
# logger2.error('The five boxing wizards jump quickly.')


handlers = logging.getLogger('').handlers
print('---------------------------')
for h in handlers:
    print(type(h), h)
