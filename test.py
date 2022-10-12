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
    def __init__(self):
        functional_python.super(self).__init__(15)

    def subclass_method(self):
        return "subclass"


cls = Class(10)

print(cls.number)  # 10
print(cls.method()) # "base_class"
print(cls.prop)  # 10
print(cls.add(5))  # 15

sub = SubClass()

print(sub.number)  # 15
print(sub.add(5))  # 20
print(sub.subclass_method())  # subclass
