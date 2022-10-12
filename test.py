from ast import Sub
from tokenize import Triple
import functional_python

@functional_python.functional_class
def Class():
    def __init__(self, number):
        self.number = number

    def method(self):
        return "base class"

    # Descriptors work
    @property
    def prop(self):
        return 10

    def add(self, number):
        return self.number + number

@functional_python.functional_class(base=Class)
def SubClass():
    def subclass_method(self):
        return "subclass"

cls = Class(10)

print(cls.add(5))


sub = SubClass(15)
print(sub.number)
print(sub.add(5))
