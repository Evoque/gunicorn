
# Using logging in multiple modules 


import logging
import auxiliary_module

# create logger with 'spam_application' 
logger = logging.getLogger('spam_application')
logger.setLevel(logging.DEBUG)

# create file handler which logs even debug messages 
fh = logging.FileHandler('spam.log')
fh.setLevel(logging.DEBUG)

# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)

# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)

# add the handlerss to the logger
logger.addHandler(fh)
logger.addHandler(ch)

logger.info('[main] Creating an instance of auxiliary_module.Auxiliary')
a = auxiliary_module.Auxiliary()
logger.info('[main] Created an instance of auxiliary_module.Auxiliary')
logger.info('[main] Calling auxiliary_module.Auxiliary.do_something')
a.do_something()
logger.info('[main] Finished auxiliary_module.Auxiliary.do_something')
logger.info('[main] auxiliary_module.Auxiliary.do_something was succcessful')
auxiliary_module.some_function()
logger.info('[main] done with auxiliary_module.some_function()')



