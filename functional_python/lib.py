from __future__ import annotations


from copy import copy
import functools
from types import FunctionType
import inspect
import types
from typing import Iterable


_stack_frame = None

_NO_ATTR = object()


def stack_frame() -> inspect.FrameInfo:
    global _stack_frame
    _stack_frame = inspect.stack()[1]


class Metaclass:
    def __init__(self, superclass) -> None:
        self.__superclass__ = superclass

    def __call__(self, *args, **kwds):
        cls = Class(self.__superclass__, *args, **kwds)

        cls.__init__ = _NO_ATTR

        for key, value in self.__dict__.items():
            if key == "__superclass__":
                continue
            if isinstance(value, types.FunctionType):
                value = BoundMethod(cls, value)

            cls.__dict__[key] = value

        if cls.__hasattr__("__init__"):
            cls.__init__(*args, **kwds)

        return cls


class Class:

    def __init__(self, superclass, *args, **kwds) -> None:
        if superclass:
            self.__superclass__ = superclass(*args, **kwds)
        else:
            self.__superclass__ = None

    def __getattribute__(self, name: str):
        try:
            attr = super().__getattribute__(name)
        except AttributeError:
            if superclass := super().__getattribute__("__superclass__"):
                attr = getattr(superclass, name)
            else:
                raise
        if hasattr(attr, "__get__"):
            return attr.__get__(self, name)
        return attr

    def __setattr__(self, name: str, value):
        try:
            attr = super().__getattribute__(name)
            if hasattr(attr, "__set__"):
                return attr.__set__(self, name, value)
            return super().__setattr__(name, value)
        except AttributeError:
            return super().__setattr__(name, value)

    def __hasattr__(self, name):
        try:
            if super().__getattribute__("__superclass__"):
                return (hasattr(self, name) or super().__hasattr__(super().__getattribute__("__superclass__"), name)) and getattr(self, name) is not _NO_ATTR
            else:
                return hasattr(self, name) and getattr(self, name) is not _NO_ATTR
        except AttributeError:
            return False


class BoundMethod:
    def __init__(self, sl, meth) -> None:
        self.sl = sl
        self.meth = meth

    def __call__(self, *args, **kwds):
        return self.meth(self.sl, *args, **kwds)


_NAME = None


def _sort_code_lines(code_lines: list[str]) -> Iterable[str]:
    global _NAME
    _NAME = None

    next_line_insert = False
    in_body = False

    for line in code_lines:
        if line.strip().startswith("@") and not in_body:
            continue
        if next_line_insert:
            next_line_insert = False
            indents = []
            for c in line:
                if c.isspace():
                    indents += [c]
                else:
                    break

            whitespace = ''.join(indents)

            yield f"{whitespace}__fp__stack_frame__()"
        if line.strip().startswith("def"):
            in_body = True
            if _NAME is None:
                _NAME = line.strip().split("def ")[1].split("(")[0]
                next_line_insert = True

        yield line


def functional_class(f: FunctionType = None, /, *, base=None, metaclass=None):
    if not f:
        return functools.partial(
            functional_class,
            base=base,
        )

    return _functional_class_inner(f, metaclass or Metaclass, base)


def _functional_class_inner(f: FunctionType, metaclass: Metaclass, base=None):
    code_lines = inspect.getsource(f).splitlines()
    sorted = _sort_code_lines(code_lines)
    code = '\n'.join(sorted)
    locals_ = {}

    g_ = copy(f.__globals__)
    g_["__fp__stack_frame__"] = stack_frame

    bytecode = compile(code, f.__code__.co_filename, "exec")
    exec(bytecode, g_, locals_)


    new_f = locals_[_NAME]
    new_f.__code__ = new_f.__code__.replace(co_firstlineno=f.__code__.co_firstlineno - 1)
    new_f()

    out = metaclass(base)

    for key, value in _stack_frame.frame.f_locals.items():
        setattr(out, key, value)

    return out
