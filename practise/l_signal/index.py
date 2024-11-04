
''' signal.alarm ''' 
import signal, os, time

def handler(signum, frame):
    signame = signal.Signals(signum).name
    print(f'Signal handler called with signal {signame} ({signum}) -- > {os.getpid()}')
 
signal.signal(signal.SIGINT, handler) 
signal.signal(signal.SIGWINCH, handler)

while True:
    user_input = input("请输入内容")
    print(os.getpid())
    print(f"\n您输入了: {user_input} \n")
    

 
# fd = os.open('/dev/ttyS0', os.O_RDWR) 

''' SIGPIPE  NOT WORK ''' 
# import os
# import sys
# import signal

# def main():
#     try:
#         # simulate large output (your code replaces this loop)
#         for x in range(10000):
#             print('y??', x)
   
#         print(__name__)
#         # flush output here to force SIGPIPE to be triggered
#         # while inside this try block.
#         sys.stdout.flush()
#     except BrokenPipeError:
#         print('BrokenPipeError')
#         # Python flushes standard streams on exit; redirect remaining output
#         # to devnull to avoid another BrokenPipeError at shutdown
#         devnull = os.open(os.devnull, os.O_WRONLY)
#         os.dup2(devnull, sys.stdout.fileno())
#         sys.exit(1) # Python exits with error code 1 on EPIPE 

# def pipe_handler(signum, frame):
#     sig = signal.Signals(signum)
#     print('sig', sig)
#     print('frame', frame)

# signal.signal(signal.SIGPIPE, pipe_handler)

# if __name__ == '__main__':
#     main()


# import threading

# class SpamContext:
#     def __init__(self):
#         self.lock = threading.Lock()


#     def __enter__(self):
#         # If KeyboardInterrupt occurs here, everything is fine
#         self.lock.acquire()
#         ... 

#     def __exit__(self, exc_type, exc_val, exc_tb):
#         ...
#         self.lock.release()

