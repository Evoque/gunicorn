
import logging

# create logger 
module_logger = logging.getLogger('spam_application.auxiliary')

class Auxiliary:
    def __init__(self):
        self.logger = logging.getLogger('spam_application.auxiliary.Auxiliary')
        self.logger.info('[auxiliary_module __init__]  of Auxiliary')
        
    def do_something(self):
        self.logger.info('[auxiliary_module do_something] doing something')
        x = 1 + 1
        self.logger.info('[auxiliary_module do_something] done doing something')
        
        
        
def some_function():
    module_logger.info('[auxiliary_module] received a call to "some_function"')