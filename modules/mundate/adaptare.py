#
# Interface/Instance adapter class::
#
class Adapter(object):
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
    ab = Adapt(a, b, _adapted_magikal_memory = 'baz')
    ab.baz = 23 ##:3 no it wasn't like this... damn... 
    print a.baz
    print b.baz
    print ab.baz

