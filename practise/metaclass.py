import warnings


class MetaBunch(type):
    def __new__(mcl, classname, bases, classdict):
        """Everything needs to be done in __new__, since
        type.__new__ is where __slots__ are taken into account.
        """

        # Define as local functions the __init__and __repr__ that
        # we'll use in the new class
        def __init__(self, **kw):
            """__init__ is simple: first, set attributes without
            explicit values to their defaults; then, set those
            explicitly passed in kw.
            """
            for k in self.__dflts__:
                if not k in kw:
                    setattr(self, k, self.__dflts__[k])
            for k in kw:
                setattr(self, k, kw[k])

        def __repr__(self):
            """__repr__ is minimal: shows only attributes that
            differ from default values, for compactness.
            """
            rep = [
                f"{k}={getattr(self,k)!r}"
                for k in self.__dflts__
                if getattr(self, k) != self.__dflts__[k]
            ]
            return f"{classname}({','.join(rep)})"

        # Build the newdict that we'll use as class dict for the new class
        newdict = {
            "__slots__": [],
            "__dflts__": {},
            "__init__": __init__,
            "__repr__": __repr__,
        }

        for k in classdict:
            if k.startswith("__") and k.endswith("__"):
                # Dunder methods: copy to newdict, or warn
                # about conflicts
                if k in newdict:
                    warnings.warn(
                        f"Cannot set attr {k!r}" f" in bunch-class {classname!r}"
                    )
                else:
                    newdict[k] = classdict[k]
            else:
                # Class variables: store name in __slots__, and
                # name and value as an item in __dflts__
                newdict["__slots__"].append(k)
                newdict["__dflts__"][k] = classdict[k]
        # Finally, delegate the rest of the work to type.__new__
        return super().__new__(mcl, classname, bases, newdict)


class Bunch(metaclass=MetaBunch):
    """For convenience: inheriting from Bunch can be used to get 
    the new metaclass (same as defining metaclass=yourself).
    """
    pass



# class Philosopher:
#     # If defined as a normal instance method, this method is implicitly
#     # converted to a class method.
#     def __init_subclass__(cls, /, default_name, **kwargs):
#         print('in init subclass')
        
#         # The default implementation but raises an error if it is called with any arguments.
#         super().__init_subclass__(**kwargs)
#         cls.default_name = default_name
        
#     def __new__(cls, name, bases, attrs):
#         print('in new')
#         return super().__new__(cls, name, bases, attrs)
        
# class APhilosopher(Philosopher, default_name="name111"):
#     pass

# a = APhilosopher()

'''
- When a class is created, `type.__new__()` scans the class variables and makes callbacks to those with a `__set_name__()` hook.

'''

class ValidatePolygon(type):
    def __new__(meta, name, bases, class_dict):
        print('in new')
        # Only validate subclasses of the Polygon class
        if bases:
            if class_dict['sides'] < 3:
                raise ValueError('Polygons need 3+ sides')
        return type.__new__(meta, name, bases, class_dict)
    
    
'''
Using `metaclass` in the base class of polygon class hierarchy.
Note that it's important not to apply the same validation to the base class.
'''
# metaclass=ValidatePolygon
class Polygon():
    # Must be specified by subclasses
    sides = None
    
    def __init_subclass__(cls):
        # TODO: this should be necessary
        super().__init_subclass__()
        if cls.sides < 3:
            raise ValueError('Polygons need 3+ sides')
    
    @classmethod
    def interior_angles(cls):
        print(cls, cls.sides)
        return (cls.sides - 2) * 180


# class Triangle(Polygon):
#     sides = 3

# class Rectangle(Polygon):
#     sides = 4
    
print('Before class')

class Line(Polygon):
    print('Before sides')
    sides = 2
    print('After sides')
    
print('After class')