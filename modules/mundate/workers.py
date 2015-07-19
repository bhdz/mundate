'''
Created on Jul 15, 2015

@author: dakkar
'''
import threading
from Queue import Queue, Empty

import time

from borgs import Synched

#
#
# What+Who+Where+Something+Too+Busy+Now+Incepting+Ideas+Building+_ConceptS
#    ?https://duckduckgo.com/?q=stackoverflow+orevent+python&t=lm
# For a punishment of my Ego I choose Describing this Pattern Bellow.
#  Whoever finds my code will Know. Moar
#
def OrEvent(*events):
    """ Mutates *events chain?yes. to include several functoids?yes. such that 
    it would beep """
    # 1a. For starters, this function performs as a Method would.
    # Also, Notice how the User {!} of the Code has to Mutate the Self something
    # See? Get it? That was a wrong path for your Reading. He didakis something On Purpose
    #
    # 2d He called `_set! and `changed in a Sequence, put that into your Attention
    #
    def or_set(self):
        self._set()
        self.changed()
    
    #
    # Same as Forementioned method but now he calls `_clear! !and `changed!
    #&ps inline doc-ing lang fr quckr undrstndng nd unt 4ut0 d0c c0mp1l4t10n
    #&self.notice Gotta distract Mah'self into Exhaustion...
    #
    def or_clear(self):
        self._clear()
        self.changed()
    
    #
    # MUTATES what is Called by E and adds INTO A CHAIN of.. Stream of Bullshit addish10n not enough time today. I MUST RELEASE today
    #
    def orify(e, changed_callback):
        e._set = e.set
        e._clear = e.clear
        e.changed = changed_callback
        e.set = lambda: or_set(e)
        e.clear = lambda: or_clear(e)
        
    or_event = threading.Event()
    
    # This is a Bullsh1t function 'cus it doesn't have any Arguments t^h&ank you!UnanimousAnonTata!san
    def changed():
        bools = [e.is_set() for e in events]
        if any(bools):
            or_event.set()
        else:
            or_event.clear()
            
    #
    # For all the events we call that Mutator Ahem, function and change? 
    #  each of them `Eventsto! include [[\w; The Items of `_set! `_clear! `changed! `set! and `clear! ]]; MagicLang$$$
    #
    for e in events:
        orify(e, changed)
    #
    # What? The State of the Whole OrEvent, this is `Gold(Au)!!$$$ Don't Touch it Read()er
    #
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

#
# This Worker .has: Tasks 
#
class Worker(threading.Thread):
    """ This Worker .has. `Task!s
    Interface: {
    
        event_stop, 
        even..xxy.. *events -> *Needs moar re-writing (refactoring.todo)
        tasks_queue -> * Where the Tasks are comming From, LEAVE it Public REader
        ~.~ This Class Rightfully belongs to the {{by the Right of Task.???lets!BullshitString?HasTobeFyck1ng ReWritten. FunctionalApproachWatch
        List Family .of. ClassEs, M1ndstate?PureGold(Au)
        }} 
    }
    Interface::
        Event_stop,
        IOEvents,
        Task.queue
            ``Refactoring?Brl!?yep.no.not.ListeningPeerOpened!?Perhaps...Pyth0nRulz..Refactoring??Next?Whldyysntstpm1ndt3lks3lfchckrsz
    """
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

#
# This Worker .has: *Tasks! and *Events! and is a nice candidate for Multiple Inheritance with List, but NOOOOO
#   This class Will _behave_ like a list if I copy all the _Public_interface of the list() class 
#
class TaskedWorker(threading.Thread):
    """ This Worker .has. `Task!s
    Interface: {
    
        event_stop, 
        even..xxy.. *events -> *Needs moar re-writing (refactoring.todo)
        tasks_queue -> * Where the Tasks are comming From, LEAVE it Public REader
        ~.~ This Class Rightfully belongs to the {{by the Right of Task.???lets!BullshitString?HasTobeFyck1ng ReWritten. FunctionalApproachWatch
        List Family .of. ClassEs, M1ndstate?PureGold(Au)
        }} 
    }
    Interface::
        Event_stop,
        IOEvents,
        Task.queue
            ``Refactoring?Brl!?yep.no.not.ListeningPeerOpened!?Perhaps...Pyth0nRulz..Refactoring??Next?Whldyysntstpm1ndt3lks3lfchckrsz
        List!! # Mixin with List
            push, pop, insert, count, *so on
    """
    class State:
        WAITING = 1
        WORKING = 0
        SHUTTING_DOWN = -1
        
    class MixinList(list):
        def push(self):
            pass
        def pop(self):
            pass
        # ... todo ... When? * ~ next phase ~ ? must include the negative of types<(TaskedWorker, list)>
        pass
    
    def __init__(self, 
                 tasks_queue, 
                 name_ = None, 
                 target_ = None,
                 event_stop = threading.Event(),
                 *events,
                 **options):
        #:~Self.init!
        self.options = options.copy()
        self.events = events
        self.tasks_queue = tasks_queue
        
        self.target_do_task = self.do_task
        
        if target_:
            self.target_do_task = target_
            if 'target' in options or target_:
                self.options['target'] = options.pop('target')
                self.target_do_task = self.options['target']
            
        self.name = name_
        
        # Self.group S_elf.name, self.target
        
        # Self.Parent.init! target, name, options
        super(Worker, self).__init__(target=self.target, name=self.name, **options)
        self.event_stop = event_stop
        
        self.events = events
        
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
if __name__ == "__main__":
    #check_OrEvent()
    check_Worker()