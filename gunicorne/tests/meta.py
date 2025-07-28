

class Singleton:
    _instance = None
    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            
        # 始终返回同一实例
        print(f"__new__: {cls._instance}") 
        return cls._instance 
    
    def __init__(self):
        print(f"__init__: {self}") 
        pass
    
    
class CustomReturn:
    def __new__(cls):
        print(f"__new__: {cls}")
        # return super().__new__(cls)
        # return object
        return object()
    
    def __init__(self):
        print(f"__init__: {self}") 
    

class Meta():
    # def __new__(meta, name, bases, class_dict):
    #     print(f"meta: {meta}")
    #     print(f"name: {name}")
    #     print(f"bases: {bases}")
    #     print(f"class_dict: {class_dict}")
    #     print(f"---------------------------------------------")
    #     return type.__new__(meta, name, bases, class_dict)
    def __init_subclass__(cls):
        super().__init_subclass__()
        print(f"cls: {cls}")
        print(f"cls super: {cls.__bases__[0] is Meta}")
    

class MyClass(Meta):
    stuff = 123
    def foo(self):
        pass

        
    
if __name__ == "__main__":
    print("============ main ============")
    # c1 = CustomReturn() 
    # print("c1 => %s" % c1) 