from pulo import Labeled
import copy

class Text(Labeled):
    """ A piece of text """
    def __init__(self, content, *labels, **context):
        super(Text, self).__init__(content, *labels, **context)

    @property
    def context(self):
        return dict(self)
    
    @context.setter
    def context(self, val = {}):
        for k, v in val.iteritems():
            self[k] = v
    
    @property
    def content(self):
        return self.value
    
    @content.setter
    def content(self, val):
        self.value = val
        
    def render(self):
        pass
    
    def __unicode__(self):
        pass
    
    def __str__(self):
        pass

def check_Text():
    line0 = Text(u"It was coming. The {machine} was ready and", next='a')
    line01 = Text(u"the {machine.owner} made a large {action} over the {machinery1} ", prev='a')
    
    line1 = Text(u"The sky darkened as the {machine} towered over the {settlement}", next='b', prev='a')
    line2 = Text(u"People scrambled for their {possession} in panic and {feeling2}", prev='b', next='c')
    line3 = Text(u"Death and {line3.harm2} ", prev='c')
    
    impressive_line=Text(u'Hear hear! to Heroes fallen and {verb1} ', next='last_message')
    
    last_message=Text("Hmmm... Interesting... now I gotta ... refit now.. Whatchaa!", )
    
    class Chapter(object):
        pass

class Template(object):
    pass
    
def check_Template(object):
    from pulo import Labeled
    
    text = Labeled("Captain, {type} vessels are {verb}", next = "b")
    text2 = Labeled("Should we {verb} our {hardware}", prev = "a")
    # TODO: Think clearly what is intended here
    # Basically this whole module is for dealing with texts aand templates
    #  Here I try to link together few pieces into a whole
    #  ...
    # I _need_ to Meditate over the purpose of this module
    # bhdz.out
    
if __name__ == "__main__":
    checks = [
              check_Text,
              ]
    for ch in checks:
        ch()    
