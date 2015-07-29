import threading
import time
import random
import copy

class Borg(object):
    __shared_state = {}
    def __init__(self, **kw):
        for k, v in kw.iteritems():
            if k not in Borg.__shared_state:
                Borg.__shared_state[k] = v
        self.__dict__ = Borg.__shared_state
        
class Synch(Borg):
    class FWrap(object):
        def __init__(self, func, lock):
            self.lock = lock
            self.func = func
            
        def __call__(self, *args, **kw):
            self.lock.acquire()
            ret = self.func(*args, **kw)
            self.lock.release()
            return ret
        
    def __init__(self, lock, **funcs):
        kwargs = {}
        kwargs['_lock'] = lock
        
        for key, func in funcs.iteritems():
            wrapped = Synch.FWrap(func, lock)
            kwargs[key] = wrapped
            
        super(Synch, self).__init__(**kwargs)
        


def check_Synch():
    def greet(name, item):
        print "Hello {name}, the {item} is yours!".format(name=name, item=item)
        return 13
        
    def ship_enter(ship, orbit):
        print "The ipss_{ship} is entering the orbit of {orbit}".format(
                    ship=ship, orbit=orbit)
        return 10
        
    synch = Synch(threading.Lock(), 
                    greet=greet, 
                    ship_enter=ship_enter)
    synch.ship_enter("Elysium", "Mars")
    synch.greet("Peterson", "phaser")
    
class Synched(Borg):
           
    def __init__(self, *locks, **kw):
        in_lock = threading.Lock()
        out_lock = threading.Lock()
        #wraps = [ Synched.FWrap(f, in_lock) for f in args ]
        
        super(Synched, self).__init__(
            output_lock = in_lock,
            input_lock = out_lock,**kw)
        
    @classmethod
    def out(cls, fmt = "", *args, **kwargs):
        s = Synched()
        
        text = fmt.format(*args, **kwargs)
        count = len(text)
        
        
        s.output_lock.acquire()
        print text
        s.output_lock.release()
        
        return count
    
def check_Synched():
    
    quit_evt = threading.Event()
   
    def greeter(name, age):
        thread_name = threading.current_thread().name
        while True:
            if False == quit_evt.is_set():
                Synched.out("{thread_name}:: Hello {name}, you are {age} years old", 
                    thread_name = thread_name, name = name, age = age)
                time.sleep(random.choice([1,2,3,4]))
            else:
                Synched.out("{thread_name}:: QuitEvent!", thread_name = thread_name)
                break
            
    threads = []
    for x in xrange(0, 10):
        name = "thread:%d" % x
        thread = threading.Thread(name = name, target = greeter, args = ("Joe", 27))
        threads.append(thread)

    for thread in threads:
        thread.start()
        
    input = raw_input()
    quit_evt.set()
    
    for thread in threads:
        thread.join()
    
if __name__ == "__main__":
    check_Synch()