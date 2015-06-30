
def yes(*values, **keywords):
    ret = True
    for value in values:
        if value is None or value == False:
            ret = False
            break
            
    for value in keywords.itervalues():
        if value is None or value == False:
            ret = False
            break
    return ret
    
def no(*values, **keywords):
    return yes(*values, **keywords) == False

# http://stackoverflow.com/questions/1952464/in-python-how-do-i-determine-if-an-object-is-iterable
def is_iterable(some_object):
    try:
        some_object_iterator = iter(some_object)
        return True
        next(some_object_iterator) # Shut up interpreter
        
    except TypeError:
        return False

class Labeled(dict):
    """ This labels a value"""
    def __init__(self, value_, *labels, **labels_context):
        self.value = value_
        d = {label: None for label in labels}
        self.labels = d
        self.update(**labels_context)
        
        
    def label_set(self, label, value):
        self[label] = value
    
    def label_get(self, label):
        return self[label]
    
    @property
    def labels(self):
        return self.copy()
    
    @labels.setter
    def labels(self, labels_ = {}):
        if isinstance(labels_, dict) or isinstance(labels_, Labeled):
            for key, value in labels_.iteritems():
                self[key] = value
    
    @property
    def value(self):
        return self._value
        
    @value.setter
    def value(self, value):
        self._value = value
        
    def __str__(self):
        ret = "{value}? [".format(value = self.value)
        first = True
        for label, label_value in self.iteritems():
            
            lv = ""
            if first:
                lv = "{label}? {label_value}".format(label = label, label_value = str(label_value))
                first = False
            else:
                lv = "; {label}? {label_value}".format(label = label, label_value = str(label_value))
            ret = "{old}{lv}".format(old = ret, lv = lv)

        ret = "{old}]".format(old = ret)
        return ret
        
    def __unicode__(self):
        ret = u"{value}?[[".format(value = self.value)
        first = True
        for label, label_value in self.iteritems():
            
            lv = u""
            if first:
                lv = u"{label}? {label_value}".format(label = label, label_value = str(label_value))
                first = False
            else:
                lv = u"; {label}? {label_value}".format(label = label, label_value = str(label_value))
            ret = u"{old}{lv}".format(old = ret, lv = lv)

        ret = u"{old}]]".format(old = ret)
        return ret
    
def check_Labeled():
    person = Labeled("Sam",first_name = "Samuel", last_name = "Jackson")
    person.diet = Labeled("no meat, no animal products, just plants", vegan = True)
    
    weight_loss = Labeled(30, units = 'pounds')
    person.diet.weight_loss = weight_loss
 
    print "person ::", person
    print "person.diet ::", person.diet
    print "person.diet.weight_loss ::", person.diet.weight_loss
    
    pulp_fiction = Labeled("Pulp Fiction", 
                        produced_in = "90s", 
                        directed_by = 
                            Labeled("Quentin", last_name = "Tarantino")
                   )
    print "pulp_fiction ::", pulp_fiction
    snakes_planes = Labeled("Snakes on the Plane",
                        produced_in = "90s",
                        directed_by = 
                            Labeled("David", middle_name="R.", last_name = "Ellis")
                    )
    print "snakes_planes ::", snakes_planes
    others = Labeled([], iterable = True, others = True)
    print "others::", others
    person.movies_played = [ pulp_fiction, snakes_planes, others ]
    
    print "person.movies_played ::", Labeled(person.movies_played)
      
    names = Labeled("Joe", "Random", "H.")
    print "names ::", names 
    
    print "person.labels ::", person.labels
    print "person.value ::", person.value
    person.label_set("last_name", "Jaxon")
    print "person.label_get ::", person.label_get("last_name")

class Node(object):
    pass

class Entry(dict):
    """It's for stacking values/names on top of attributes and a real handy way to keep an eye watch over elements thru' hierarchically structured Tree-like object. see """
    def __init__(self, value):
        self.__value = value
    
    @property
    def _mangled(self):
        return '_{}__'.format(self.__class__.__name__)
    
    @property
    def _value(self):
        return self.__value
    
    def __getattr__(self, name):
        value = None
        
        if name.startswith(self._mangled):
            value = super(Entry, self).__getitem__(name)
        else:
            value = super(Entry, self).__getattr__(name)
        return value
      
    def __setattr__(self, name, value):
        if name.startswith(self._mangled):
            super(Entry, self).__setitem__(name, value)
        else:
            val = Entry(value)
            super(Entry, self).__setattr__(name, val)

    def __str__(self):
        pass
        
def check_Entry():
    e = Entry("root")
    
    print e._mangled
    
    e.joe = "Joe Random"
    e.joe.age = 23
    e.joe.name = "Joe"
    e.joe.name.last = "Random"
    e.joe.name.last.ego = "Super Random"
    
    print "e.person:", e.joe._value, ", type?", type(e.joe)
    print "e.person.age:", e.joe.age._value, ", type?", type(e.joe.age)
    print "e.person"
        
class Eye(object):
    __sections = { '_gaze': Entry("root") }
    
    def __init__(self, *a, **kw):
        self.__dict__ = Eye.__sections
        
def check_Eye():
    Eye()._gaze.john = "John Lennon"
    Eye()._gaze.john.name = "John"
    Eye()._gaze.john.name.last = "Lennon"
    Eye()._gaze.john.trabacho = "Guitar Player"
    Eye()._gaze.john.guitarra = "Less Paul Gibson"
    e = Eye("career")
    e.john.occupation = "Musician"
    e.john.age = 35
    

if __name__ == "__main__":
    check_Entry()
    check_Eye()
    
