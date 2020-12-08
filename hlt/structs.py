import types

class Struct(types.SimpleNamespace):
    """
    A structure to put fields into. Has .keys(), .values(), .items(), .pop(),
    .update() that all perform same as a dict(). Also has .setAll(value) that
    sets all fields in the object to 'value' and .clear() that removes all fields
    from the object.
    Struct is also subcriptable, and supports basic +/-, +=/-=, ==, !=.

    also supported:
        Struct() == dict()
        Struct() != dict()
        dict() == Struct()
        dict != Struct()
        Struct() +/- dict()
        Struct() +=/-= dict()

    obj = Struct(a=2, b=[3,4], c='hello')
    *OR
    obj = Struct({'a':2, 'b':[3,4], 'c':'hello'})

    Example usage after construction:
    obj.a += 1
    obj.d = 'world'
    obj.setItem(b, 42)
    obj['c'] = 3
    obj.update({'a':2})
    del obj['a']
    del obj.c
    obj.clear()

    Iterators
    for k, v in obj.items()
    for k in obj.keys()
    for v in obj.values()
    """

    def __init__(self, *arg, **kwargs):
        if arg and not kwargs:
            if len(arg) == 1 and type(arg[0]) == dict().__class__:
                self.update(*arg)
            else:
                raise Exception('Struct() takes either a dict or keyword arguments. {} provided'.format(type(arg[0])))
        elif kwargs and not arg:
            super().__init__(**kwargs)
        elif not arg and not kwargs:
            pass
        else:
            raise ValueError

    def __str__(self):
        if self.__dict__:
            out = [type(self).__name__ + '(']
            repr = []
            for k, v in self.__dict__.items():
                repr.append('{}=\'{}\''.format(k, v) if type(v) == type('') else '{}={}'.format(k, v))
            for field in repr[0:len(repr) - 1]:
                out += field
                out += ','
            out += repr[-1]
            out += ')'
            return ''.join(out)
        return type(self).__name__ + '()'

    def __repr__(self):
        return self.__str__()

    def setItem(self, key, value):
        self.__dict__.update({key:value})

    def setAll(self, value):
        self.__dict__.update({k:value for k in self.__dict__.keys()})

    def update(self, d):
        self.__dict__.update(d)

    def __add__(self, other):
        return dict(self.__dict__, **other)

    def __iadd__(self, other):
        self.__dict__.update(other)
        return self

    def __sub__(self, other):
        temp = dict(self.__dict__)
        for k in list(other.keys()):
            try:
                temp.pop(k)
            except KeyError:
                pass
        return Struct(temp)

    def __isub__(self, other):
        keys = list(other.keys())
        for k in list(self.__dict__.keys()):
            if k in keys:
                self.__dict__.pop(k)
        return self

    def __getitem__(self, key, failure=None):
        try:
            return self.__dict__.__getitem__(key)
        except KeyError:
            return failure

    def __setitem__(self, key, value):
        self.update({key:value})

    def __setattr__(self, key, value):
        self.update({key:value})

    def __delitem__(self, key):
        self.__dict__.__delitem__(key)

    def keys(self):
        for k in self.__dict__.keys():
            yield k

    def values(self):
        for v in self.__dic__.values():
            yield v

    def items(self):
        for k, v in self.__dict__.items():
            yield k,v

    def __eq__(self, other):
        keys = list(other.keys())
        for k, v in self.__dict__.items():
            if k not in keys or v != other[k]:
                return False
        return True

    def __ne__(self, other):
        return not self == other

    def pop(self, key, *args):
        if args:
            return self.__dict__.pop(key, *args)
        return self.__dict__.pop(key)

    def clear(self):
        self.__dict__.clear()