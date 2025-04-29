
# Logging from multiple threads
"""
3. thread.join()是干嘛的
"""

# The following example shows logging from the main(initial) thread and another thread.abs
import logging
import threading
import time

logging.basicConfig(level=logging.DEBUG, format='%(relativeCreated)6d => [%(threadName)s] %(message)s')
logger = logging.getLogger('mul_thd')

def worker(arg):
    while not arg['stop']:
        logger.debug('log from worker')
        time.sleep(0.5)
    logger.debug('arg %s', arg)
    
def main():

    info = {'stop':False}
    thd = threading.Thread(target=worker, args=(info,))
    thd.start()
    while True:
        try:
            logger.debug('log from main')
            time.sleep(0.5)
        except KeyboardInterrupt:
            info['stop'] = True
            break
    thd.join()
    
if __name__ == '__main__':
    main()