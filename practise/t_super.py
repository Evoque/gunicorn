
import logging

class LoggingDict(dict):
    def __setitem__(self, key, value):
        logging.info('Setting %r' % (key, value))
        super().__setitem__(key, value)
        # dict.__setitem__(self, key, value)
        


class Shape:
    def __init__(self, shapeName, **kwds):
        self.shapeName = shapeName
        super().__init__(**kwds)
        
class ColoredShape(Shape):
    def __init__(self, color, **kwds):
        self.color = color
        print('==>', super())
        print('==>', super().__class__.__name__)
        print('type', type(super()))
        super().__init__(**kwds)
        
cs = ColoredShape(color='red', shapeName='circle')


from collections import Counter, OrderedDict

class OrderedCounter(Counter, OrderedDict):
    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, OrderedDict(self))
    
    def __reduce__(self):
        return self.__class__, (OrderedDict(self),)
    
oc = OrderedCounter('abracadabra')

 