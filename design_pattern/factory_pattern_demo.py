#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Factory Pattern Demo
-------------------

The Factory Method pattern defines an interface for creating objects but
lets subclasses decide which classes to instantiate.
"""

from abc import ABC, abstractmethod


# Product interface
class Product(ABC):

    @abstractmethod
    def operation(self):
        pass


# Concrete Products
class ConcreteProductA(Product):
    def operation(self): 
        return "[Result of ConcreteProductA]"


class ConcreteProductB(Product):
    def operation(self):
        return "[Result of ConcreteProductB]"


# Creator abstract class
class Creator(ABC):
    
    @abstractmethod
    def factory_method(self):
        pass
    
    def some_operation(self):
        product = self.factory_method()
        return f"Creator: The same creator's code has just worked with {product.operation()}"

class ConcreteCreatorA(Creator):
    def factory_method(self):
        return ConcreteProductA()


class ConcreteCreatorB(Creator):
    def factory_method(self):
        return ConcreteProductB()


# Client code
def client_code(creator):
    print(f"Client: I'm only aware of the scheme.\n {creator.some_operation()}")


if __name__ == "__main__":
    print("App: Launched with ConcreteCreatorA.")
    client_code(ConcreteCreatorA())
    print("\n")
    
    print("App: Launched with ConcreteCreatorB.")
    client_code(ConcreteCreatorB())
