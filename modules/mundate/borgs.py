import threading
import time
import random

class Borg(object):
    __shared_state = {}
    def __init__(self, **kw):
        for k, v in kw.iteritems():
            if k not in Borg.__shared_state:
                Borg.__shared_state[k] = v
        #Borg.__shared_state.update(kw)
        self.__dict__ = Borg.__shared_state
        
class Synched(Borg):
    def __init__(self):
        super(Synched, self).__init__(output_lock = threading.Lock())
        
    @classmethod
    def out(cls, fmt = "", *args, **kwargs):
        text = fmt.format(*args, **kwargs)
        count = len(text)
        
        s = Synched()
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
    check_Synched()