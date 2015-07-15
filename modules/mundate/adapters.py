import inspect
from pulo import Labeled, Entry

# https://en.wikipedia.org/wiki/Adapter_pattern
# &this for later
#
# Interface/Instance adapter class::
#
class Adaptor(object):
    def __init__(self, adaptee, adapted):
        pass
#
# Decorator helper for adapting interfaces
#
def adapt(fmethod, name1, name2):
    pass
    
# 
# This is only to get us thru' inception phase, not a proper testing code piece
#
def eyecheck_Adapt():
    class Foo:
        def __init__(self, baz):
            self.baz = baz
            
    class Bar:
        def __init__(self, baz):
            self.baz = baz
            
    a = Foo(11)
    b = Foo(13)
    ab = Adaptor(a, b)

    ab.baz = 23 ##:3 no it wasn't like this... damn... 
    print a.baz
    print b.baz
    print ab.baz

