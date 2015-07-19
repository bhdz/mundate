'''
Created on Jul 15, 2015

@author: dakkar
'''
import threading
from Queue import Queue, Empty

import time

from borgs import Synched

def OrEvent(*events):
    def or_set(self):
        self._set()
        self.changed()
    
    def or_clear(self):
        self._clear()
        self.changed()
    
    def orify(e, changed_callback):
        e._set = e.set
        e._clear = e.clear
        e.changed = changed_callback
        e.set = lambda: or_set(e)
        e.clear = lambda: or_clear(e)
        
    or_event = threading.Event()
    
    def changed():
        bools = [e.is_set() for e in events]
        if any(bools):
            or_event.set()
        else:
            or_event.clear()
            
    for e in events:
        orify(e, changed)
        
    changed()
    or_event.events = events
    def fired(self):
        pass
    or_event.fired = fired
    return or_event

def check_OrEvent():
    import time
    
    def wait_on(name, e):
        print "Waiting on %s..." % (name,)
        e.wait()
        print "%s fired!" % (name,)
    e1 = threading.Event()
    e2 = threading.Event()

    or_e = OrEvent(e1, e2)

    threading.Thread(target=wait_on, args=('e1', e1)).start()
    time.sleep(0.05)
    threading.Thread(target=wait_on, args=('e2', e2)).start()
    time.sleep(0.05)
    threading.Thread(target=wait_on, args=('or_e', or_e)).start()
    time.sleep(0.05)

    print "Firing e1 in 2 seconds..."
    time.sleep(2)
    e1.set()
    time.sleep(0.05)

    print "Firing e2 in 2 seconds..."
    time.sleep(2)
    e2.set()
    time.sleep(0.05)

#check_OrEvent()

class Task(object):
    # general task
    def __init__(self, name, f, *a, **ka):
        self.name = name # name string tag
        self.f = f # fun
        self.a = a # args
        self.ka = ka # kwargs
        self.worker = None# caller ref
        self.is_attached = False #
        
'''        
    def attach(self,worker):
        """ when pushed to worker worker is attached and not None"""
        self.worker = worker
        if self.worker is not None:
            self.is_attached = True
        else:
            self.is_attached = False
        
    def is_attached(self):
        return self.is_attached
'''

class Worker(threading.Thread):
    class State:
        WAITING = 1
        WORKING = 0
        SHUTTING_DOWN = -1

    def __init__(self, name, 
                 event_stop = threading.Event(), 
                 event_newtask = threading.Event(),
                 event_pause = threading.Event(),
                 tasks_queue = Queue()):
        super(Worker, self).__init__()
        self.name = name
        self.event_stop = event_stop
        self.event_newtask = event_newtask
        self.event_pause = event_pause
        
        self.tasks_queue = tasks_queue
        
        self.event_or = OrEvent(self.event_stop, self.event_newtask, self.event_pause)
        
        self.state = Worker.State.WAITING
    
    def do_task(self):
        try:
            task = self.tasks_queue.get_nowait()
            self.state = Worker.State.WORKING
            
            result = task.f(*task.a, **task.ka)
            
            self.tasks_queue.task_done()
            self.state = Worker.State.WAITING
            
        except Empty:
            self.event_newtask.clear()
            
    def run(self):
        while True:
            self.event_or.wait()

            if self.event_stop.is_set():
                self.state = Worker.State.SHUTTING_DOWN
                break
            elif self.event_newtask.is_set():
                self.do_task()
            else:
                self.do_task()

                
    def push(self, task):
        self.tasks_queue.put(task)
        self.event_newtask.set()
        
    def pause(self, name = None, timeout = 0):
        """ eg. suspend thread tasks[name].event.wait() """
        self.event_or.clear()
        
    def resume(self):
        self.event_or.set()
    
    def quit(self):
        """ e.g stop everethyng and destroy thread process """
        self.event_stop.set()
        
    def state(self):
        """ return info about current state 
        is it working on task or paused waiting etc
        will be used from task.calller.state
        """
        return self.state 

def check_Worker():
    from pulo import random_string
    
    def print_random_string(n):
        str = random_string(n)
        Synched.out("print_random_string:: {rnd}", rnd = str)
    
    def print_string(fmt, *args, **kw):
        Synched.out(fmt, *args, **kw)
    
    
    def decorate_string(string):
        string = "<<" + string + ">>"
    producer = Worker("producer")
    
    try:
        while True:
            data = raw_input("Enter some data> ")
            Synched.out("value? {value}; type? {type}", data = data, type = type(data))
            
            producer.quit()
            producer.join()
            #t1 = Task("random_string", print_random_string, 17)
    except EOFError:
        print "Quitting"

    
if __name__ == "__main__":
    #check_OrEvent()
    check_Worker()