'''
Created on Jul 15, 2015

@author: dakkar
'''
import threading
from Queue import Queue, Empty

import time

from borgs import Synched
from mundate.pulo import random_string
from gnomekeyring import BadArgumentsError


#
# From?
#    http://stackoverflow.com/questions/12317940/python-threading-can-i-sleep-on-two-threading-events-simultaneously
#
# search terms?
#    https://duckduckgo.com/?q=def+OrEvent
#
# Here is a non-polling non-excessive thread solution: modify the existing 
#  Events to fire a callback whenever they change, and handle setting a 
#  new event in that callback:
#      `Claudiu@stackoverflow.com/
#
# Oh and here is your wait_for_either function, though the way I wrote the code, 
# it's best to make and pass around an or_event. Note that the or_event 
#  shouldn't be set or cleared manually.
#    `Claudiu@http://stackoverflow.com/
#
# This is nice! However, I see one problem: if you orify the same event twice, 
#  you'll get a infinite loop whenever you set or clear it.
#      `Vincent@http://stackoverflow.com/
#
# Original? {{
# import threading
# 
# def or_set(self):
#     self._set()
#     self.changed()
# 
# def or_clear(self):
#     self._clear()
#     self.changed()
# 
# def orify(e, changed_callback):
#     e._set = e.set
#     e._clear = e.clear
#     e.changed = changed_callback
#     e.set = lambda: or_set(e)
#     e.clear = lambda: or_clear(e)
# 
# def OrEvent(*events):
#     or_event = threading.Event()
#     def changed():
#         bools = [e.is_set() for e in events]
#         if any(bools):
#             or_event.set()
#         else:
#             or_event.clear()
#     for e in events:
#         orify(e, changed)
#     changed()
#     return or_event
#}}
def OrEvent(*events):
    def or_set(self):
        self._set()
        self.changed()
    
    def or_clear(self):
        self._clear()
        self.changed()
    
    def _is_patched(e):
        if '_set' in e.__dict__:
            return True
        elif '_clear' in e.__dict__:
            return True
        return False
    
    def orify(e, changed_callback):
        if False == _is_patched(e):
            e._set = e.set
            e._clear = e.clear
            e.changed = changed_callback
            e.set = lambda: or_set(e)
            e.clear = lambda: or_clear(e)
    
    orevent = threading.Event()
    
    def changed():
        bools = [e.is_set() for e in events]
        if any(bools):
            orevent.set()
        else:
            orevent.clear()
            
    for e in events:
        orify(e, changed)
    
    def isSet(self):
        if self._isSet():
            return True
        truths = [e.is_set() for e in events]
        return any(truths)
    
    def gather_setted(self):
        return [e for e in events if e.isSet()]
        
    orevent._isSet = orevent.isSet
    orevent.isSet = isSet
    orevent.gather_setted = gather_setted
    
    changed()
    return orevent

def start_all(threads):
    for thread in threads:
        thread.start()
        
def join_all(threads):
    for thread in threads:
        thread.join()
        
def threads_do(threads, method, *args, **kwargs):
    for thread in threads:
        method(thread, *args, **kwargs)

def threads_start(threads):
    threads_do(threads, QueueWorker.start)
        
def threads_pause(threads):
    threads_do(threads, QueueWorker.pause)

def threads_resume(threads):
    threads_do(threads, QueueWorker.resume)
        
def threads_join(threads):
    threads_do(threads, QueueWorker.join)
        
# This is just for debugging purposes
def thread_say(fmt, *args, **keys):
    _name = threading.current_thread().name
    
    label_string = "Thread:{name}".format(name=_name)
    fmt_string = fmt.format(*args, **keys)
    full_string = "{label}:: {fmt}".format(label=label_string, fmt=fmt_string)
    return Synched.out(full_string)


class ActionedEvents(list):
    def __init__(self, iterable = []):
        self.names = {} # [index] name
        self.actions = {} # [index] action
        self._is_owned = {} 
        self.indices_names = {} # [name] index
        self.indices_actions = {} # [action] index
        self.indices_is_owned = {} # [is_owned:bool] index
        
        #self.or_event = OrEvent(*self)
        super(ActionedEvents, self).__init__(iterable)
        
    def remove(self, event):
        if event in list(self):
            index = self.index(event)
            name = self.names.pop(index)
            action = self.actions.pop(index)
            
            self.indices_names.pop(name)
            self.indices_actions.pop(action)
            return super(ActionedEvents, self).remove(event)
            
    def add(self, event, action, name, is_owned = True):
        if not event in list(self):
            self.append(event)
            index = self.index(event)
            
            self._is_owned[index] = is_owned
            
            self.actions[index] = action
            self.names[index] = name
            
            self.indices_names[name] = index
            self.indices_actions[action] = index
            
            # Update <or_event>
            #self.or_event = OrEvent(*self)
            return event    
        else:
            raise BadArgumentsError("<event> already in the event stack")
        
        
    def get(self, by_name = None, by_index = None):
        index = None
        if by_name:
            if not by_name in self.names.values():
                raise Exception("not (<nameid> in self.events_names)")
            index = self.indices_names[by_name]
        elif by_index:
            index = by_index
        thread_say("index = {index}", index=index)
        event = None
        if index is not None:
            event = self[index]
        return event
    
    def set(self, event, action, name, is_owned = True):
        if not event in list(self):
            raise Exception("Cannot set an unregistered Event")
        
        index = self.index(event)
        
        #event.is_owned = is_owned
        self._is_owned[index] = is_owned
        
        self.actions[index] = action
        self.indices_actions[action] = index
        
        self.names[index] = name
        self.indices_names[name] = index
        return event
    
    def action(self, event):
        return self.actions[self.index(event)]
    
    def action_set(self, event, action):
        index = self.index(event)
        self.actions[index] = action
        self.indices_actions[action] = index
    
    def name(self, event):
        return self.names[self.index(event)]
    
    def name_set(self, event, name):
        index = self.index(event)
        self.names[index] = name
        self.indices_names[name] = index
        
    def is_owned(self, event):
        index = self.index(event)
        return self._is_owned[index]
    
    def is_owned_set(self, event, is_owned):
        index = self.index(event)
        self._is_owned[index] = is_owned

# Worker class
# 
# Works on a queue which by default is polled for input tasks
#
class QueueWorker(threading.Thread):
    """ Worker: Basic thread that works with a <queue> and supports
    <pause>, 
    """ 

    class State:
        WORKING = 0
        SLEEPING = 1
        ERROR = -1
        
    class Policy:
        _INFO = {
                     'QUEUE_GET': ['polling', 'blocking'],
                     'QUEUE_GET_DEFAULT': 'polling',
                }
        QUEUE_GET = 'polling' # Default
        SLEEP_TIMEOUT = 0.5
 
    def __init__(self, queue, 
                 target = None,
                 args = (),
                 kwargs = {},
                 name = None,
                 e_quit=threading.Event(),  # Global QUIT
                 e_command=threading.Event(),
                 *events,
                 **options):
        self.queue = queue
        #self.e_quit = e_quit

        self.target = target
        self.args = args
        self.kwargs = kwargs
        
        super(QueueWorker, self).__init__(target=target, name=name, args=args, kwargs=kwargs)
        
        self._init()
        self._init_events(e_quit, e_command)

    def _init(self):
        #Reader(), make these configurable by <options>
        self.state = QueueWorker.State.WORKING
        self.state_prev = None
        self.policy = QueueWorker.Policy.QUEUE_GET
        self.quitting = False
        
    def _init_events(self, e_quit, e_command):
        self.events = ActionedEvents()
        self.events.add(threading.Event(), self.on_sleep, 'sleep', True)
        self.events.add(threading.Event(), self.on_wakeup, 'wakeup', True)
        self.events.add(e_quit, self.on_quit, 'quit', False)
        self.events.add(e_command, self.on_command, 'command', False)
        
    def check_events(self):
        """ Checks the thread for set events and returns them as a list
        """
        
        events_set = []
        for event in self.events:
            if event.is_set():
                events_set.append(event)
        return events_set
                
    def process_events(self, set_events = []):
        """ Processes a set of triggered events""" 
        for event in set_events:
            if event.is_set():
                
                action = self.events.action(event) # self.get_event_action(event)

                action(event)
                if self.events.is_owned(event):
                    event.clear()
    
    def change_policy(self, new_policy):
        self.policy_prev = self.policy
        self.policy = new_policy
        return self.policy_prev
    
    def change_state(self, new_state):
        """ Todo """
        self.state_prev = self.state
        self.state = new_state
        return self.state_prev
    
    #
    # Events/Action handlers
    #
    
    # These are actions to be called on each event <set>
    def on_command(self, event):
        pass
    
    def on_quit(self, event):
        self.quitting = True
     
    def on_sleep(self, event):
        #e_wakeup = self.events.get('wakeup')
        self.change_state(QueueWorker.State.SLEEPING)
        #e_wakeup.wait()
        
    
    def on_wakeup(self, event):
        #e_sleep = self.events.get('sleep')
        #e_sleep.clear()
        #event.clear()
        self.change_state(QueueWorker.State.WORKING)
    

                
    # Override this to modify the behavior of Worker while getting items from 
    #  the queue 
    def do_fetch(self):
        # This is by the DEFAULT POLICY (polling) 
        item = None
        try:
            item = self.queue.get_nowait()
        except Empty:
            item = None # Or sleep
        return item
        
    # Implement this if you want specific result 
    def do_result(self, result):
        """do_result: Handles the result of one work operation <do_work>. 
        Override this behavior in subclasses.
        """
        pass
    
    def do_nothing(self):
        pass
    
    # Overwrite this if you want something different than targeting <target>
    def do_work(self, item):
        """do_work: Handles A Unit of operation. 
        Override this behavior in subclasses.
        """
        result = None
        if self.target:
            result = self.target(item, *self.args, **self.kwargs)
        return result
    
    def run(self):
        while self.quitting == False:
            # check for events
            set_events = self.check_events()
           
            # respond to events
            self.process_events(set_events)

            # do work with the item, override this for Producers
            if self.state == QueueWorker.State.WORKING:
                # fetch from the queue, override this for Producers
                item = self.do_fetch()
                if item:
                    result = self.do_work(item)
                    
                    if result:
                        self.do_result(result)
                else:
                    self.do_nothing()
            elif self.state == QueueWorker.State.SLEEPING:
                #thread_say("Sleeping for {secs}", secs = Worker.Policy.SLEEP_TIMEOUT)
                time.sleep(QueueWorker.Policy.SLEEP_TIMEOUT)
    
    #
    # Interface
    #
    
    # pause
    def pause(self):
        """ This puts the Worker into <sleep> with <on_sleep> event action 
        method, see <on_sleep> for a complete view over the operation"""
        #thread_say("pause()!")
        #self.e_pause.set()
        e_sleep = self.events.get(by_name='sleep')
        if e_sleep:
            e_sleep.set()
        else:
            raise Exception("Cannot fetch 'sleep' event/action!")
        
    # resume    
    def resume(self):
        """ This resumes operations using <wakeup> event and 
        <on_wakeup> event action method"""
        #thread_say("resume()!")
        e_wakeup = self.events.get(by_name='wakeup')
        if e_wakeup:
            e_wakeup.set()
        else:
            raise Exception("Cannot fetch 'wakeup' event/action!")
        
    # stop
    def stop(self):
        e_quit = self.events.get(by_name='quit')
        if e_quit:
            e_quit.set()
        else:
            raise Exception("Cannot fetch 'quit' event/action!")
        
    # command
    def command(self, target):
        e_command = self.events.get(by_name='command')
    
def check_Worker_basic():
    from pulo import random_string
    
    def create_string(N):
        ret = "Hello world! [%d]" % N
        return ret
    
    def pretty_print(item, label):
        Synched.out("-=@ {label}: {item} @=-", label=label, item=item)    


    queue = Queue()
    e_quit = threading.Event()
    e_pause = threading.Event()
    e_wakeup = threading.Event()
    
    thread_say("Creating items...")
    # fill up the queue
    count = 1 
    for x in xrange(1, 25):
        queue.put(create_string(count))
        count += 1
    
    consumer = QueueWorker(queue, target=pretty_print, args=('PrettyPrint',),
                      name = "PrettyPrinter", 
                      e_quit=e_quit,
                      )
     
    thread_say("Starting thread for 3 secs...")

    consumer.start()
    time.sleep(1)
    
    for y in xrange(1,3):
        consumer.pause()
        
        for x in xrange(1, 5):
            queue.put(create_string(count))
            count += 1
            
        time.sleep(1)
        thread_say("Resuming thread")
        
        consumer.resume()


    time.sleep(3)
     
    thread_say("Set Quit...")
    e_quit.set()
    time.sleep(2)
    thread_say("Joining Threads...")
    consumer.join()
        
    def empty_queue():
        print ""
        print "Mainthread: queue::"
        while not queue.empty():
            item = queue.get()
            print "\titem: %s" % item
    
    empty_queue()

# 
# A producer Worker.
#  Each Producer treats the queue as something to be filled with data, rather 
#  than a source of data for the thread
#
class QueueProducer(QueueWorker):
    def __init__(self, queue, 
                 target = None,
                 args = (),
                 kwargs = {},
                 name = None,
                 e_quit=threading.Event(),  # Global QUIT
                 e_command=threading.Event(),
                 **options):
        
        super(QueueProducer, self).__init__(queue, 
                target=target, 
                args=args, 
                kwargs=kwargs,
                name=name,
                e_quit=e_quit,
                e_command=e_command)
    
    # Overwrite this if you want something different than targeting <target>
    def do_work(self, item):
        """do_work: Handles A Unit of operation. 
        Override this behavior in subclasses.
        """
        self.queue.put(item)
        return None
                
    # Override this to modify the behavior of Worker while getting items
    def do_fetch(self):
        """ Handles data to be fetched/generated"""
        return self.target(*self.args, **self.kwargs)
    
def check_Producer_Worker():
    from pulo import random_string
    
    queue = Queue()
    e_quit = threading.Event()
    
    threads = []
    producers = []
    consumers = []
        
    string_len = 15
    def genstring(N):
        string = random_string(N)
        #thread_say("Generated: {string}", string=string)
        return string
    
    def pretty_print(item, label):
        thread_say("-=@ {label}: {item} @=-", label=label, item=item)
        #Synched.out("-=@ {label}: {item} @=-", label=label, item=item)  
    
    # Producers
    for n in xrange(0,3):
        producer = QueueProducer(queue, 
                            target=genstring, args=(string_len,), 
                            name=("Producer[%d]" % n), 
                            e_quit=e_quit)
        producers.append(producer)
        threads.append(producer)
    
    # Consumers / Workers
    for n in xrange(0,5):
        consumer = QueueWorker(queue, 
                            target=pretty_print, args=("eating",), 
                            name=("Consumer[%d]" % n), 
                            e_quit=e_quit)
        consumers.append(consumer)
        threads.append(consumer)
    
    threads_start(producers)
    threads_start(consumers)
    time.sleep(5)
    
    threads_do(producers, QueueWorker.pause)
    time.sleep(5)
    
    # Quitting ALL
    #threads_do(producers, QueueWorker.resume)
    e_quit.set()
    threads_join(producers)
    threads_join(consumers)
    
    def empty_queue():
        Synched.out("")
        thread_say("queue::")
        while not queue.empty():
            item = queue.get()
            thread_say("\titem: {item}", item = item)
    
    empty_queue()

# This class acts on two queues and puts a transformed (through <target>) item
# into an <output queue|queue_output>
class QueuePipe(QueueWorker):
    def __init__(self, queue, queue_output,
                 target = None,
                 args = (),
                 kwargs = {},
                 name = None,
                 e_quit=threading.Event(),  # Global QUIT
                 e_command=threading.Event(),
                 **options):
        
        super(QueuePipe, self).__init__(queue, 
                target=target, 
                args=args, 
                kwargs=kwargs,
                name=name,
                e_quit=e_quit,
                e_command=e_command)
        self.queue_output = queue_output
   
    # Overwrite this if you want something different than targeting <target>
    def do_work(self, item):
        """do_work: Handles A Unit of operation. 
        Override this behavior in subclasses.
        """
        result = None
        if self.target:
            result = self.target(item, *self.args, **self.kwargs)
        return result
                
    # Override this to modify the behavior of Worker while getting items from 
    #  the queue 
    def do_fetch(self):
        # This is by the DEFAULT POLICY (polling) 
        item = None
        try:
            item = self.queue.get_nowait()
        except Empty:
            item = None # Or sleep
        return item
        
    # Implement this if you want specific result 
    def do_result(self, result):
        """do_result: Handles the result of one work operation <do_work>. 
        Override this behavior in subclasses.
        """
        self.queue_output.put(result)
    
    def run(self):
        while self.quitting == False:
            # check for events
            set_events = self.check_events()
           
            # respond to events
            self.process_events(set_events)

            # do work with the item, override this for Producers
            if self.state == QueueWorker.State.WORKING:
                # fetch from the queue, override this for Producers
                item = self.do_fetch()
                if item:
                    result = self.do_work(item)
                    
                    if result:
                        self.do_result(result)
                else:
                    self.do_nothing()
            elif self.state == QueueWorker.State.SLEEPING:
                #thread_say("Sleeping for {secs}", secs = Worker.Policy.SLEEP_TIMEOUT)
                time.sleep(QueueWorker.Policy.SLEEP_TIMEOUT)

def check_Pipe_Producer():
    from pulo import random_string
    
    queue = Queue()
    queue2 = Queue()
    e_quit = threading.Event()
    
    threads = []
    producers = []
    consumers = []
    pipes = []
        
    string_len = 15
    
    def genstring(N):
        string = random_string(N)
        #thread_say("Generated: {string}", string=string)
        return string
    
    def decorate_string(string):
        return "~==@ "+string+" @==~"
    
    def pretty_print(item, label):
        thread_say("<< {label}: {item} >>", label=label, item=item)
        #Synched.out("-=@ {label}: {item} @=-", label=label, item=item)  
    
    # Producers
    for n in xrange(0,3):
        producer = QueueWorker(queue, 
                            target=genstring, args=(string_len,), 
                            name=("Producer[%d]" % n), 
                            e_quit=e_quit)
        producers.append(producer)
        threads.append(producer)
        
    # Pipes
    for n in xrange(0,5):
        pipe = QueuePipe(queue, queue2,
                            target=decorate_string, args=(), 
                            name=("Pipe[%d]" % n), 
                            e_quit=e_quit)
        pipes.append(pipe)
        threads.append(pipe)
        
    # Consumers / Workers
    for n in xrange(0,5):
        consumer = QueueWorker(queue2, 
                            target=pretty_print, args=("eating",), 
                            name=("Consumer[%d]" % n), 
                            e_quit=e_quit)
        consumers.append(consumer)
        threads.append(consumer)
    
    
    thread_say("Starting all...")
    threads_start(producers)
    threads_start(consumers)
    threads_start(pipes)

    time.sleep(5)    
    # Quitting ALL
    #threads_do(producers, Worker.resume)
    e_quit.set()
    threads_join(producers)
    threads_join(consumers)
    
    def queue_empty(q, name):
        Synched.out("")
        thread_say("queue {name}::", name=name)
        while not q.empty():
            item = q.get()
            thread_say("\titem: {item}", item = item)
    
    queue_empty(queue, name="q1")
    
    queue_empty(queue2, name="q2")
    
    
class Tasklet(threading.Thread):
    
    class State:
        WAITING=0
        WORKING=1
        ERROR=-1
        
    def __init__(self, 
                 *args, **kw):
        self.event = threading.Event()
        self.state = Tasklet.State.WAITING
        
        self._quit = False 
        self._target = None
        self._args = ()
        self._kwargs = {}
        self._on_done = None
         
        super(Tasklet, self).__init__()
        
        self.start()
        
    def _is_quit(self):
        if self._quit:
            return True
        return False
    
    def _state_set(self, to_state):
        oldstate = self.state
        self.state = to_state
        return oldstate
    
    # Implement this
    def do_work(self):
        if not self._on_done:
            self._state_set(Tasklet.State.ERROR)
        else:
            self._state_set(Tasklet.State.WORKING)
            self._on_done( self._target(
                                    *self._args, 
                                    **self._kwargs
                                )
                          )
            # print self._args, self._kwargs
            self._state_set(Tasklet.State.WAITING)
        
    def run(self):
        self.event.clear()
        while True:
            # ------- event loop ---------------------------- 
            if self._is_quit(): 
                break
            # ----------------------------------------------
            # ------- to wait or not to wait before task ----

            self.event.wait() 
            # -----------------------------------------------
            if self._is_quit(): 
                break
            # ------- process target code ------- 
            self.do_work()
            # -----------------------------------
            if self._is_quit():
                break #exit loop
            
            self.event.clear() 
            #wait after loop
    # 
    # Interface
    #
    def quit(self):
        self._exit = True
        if not self._is_event():
            self.event.set()

    def is_working(self):
        return self.state == Tasklet.State.WORKING
  
    def task_set(self, on_done, task, args, kwargs):
        if self.is_working():
            return False
        
        if self._is_event():
            return False
        self._on_done = on_done
        self._target = task
        self._args = args
        self._kwargs = kwargs
        self.event.set() # resume
        return True
    
def check_Tasklet():
    pass

# 
# Task
#
class Task(object):
    def __init__(self, func, *args, **keys):
        self.func = func
        self.args = args
        self.keys = keys
        self.result = None
        self.links = [ ]
        self.links_results = {}
        
    def __call__(self, *args2, **keys2):
        keys = {}
        for k, v in self.keys.iteritems():
            result = v
            if isinstance(v, Task):
                result = v()
            keys[k] = result
            
        keys2.update(keys)
        self.result = self.func(*(self.args+args2), **keys2)
        
        for link in self.links:
            result2 = self.link_call(link)

        return self.result
    
    def link_call(self, link):
        
        task = link[0]
        args_keys = link[1]
        results = link[2]
        
        result = task(*args_keys[0], **args_keys[1])
        results.append(result)
        return results
    
    def link(self, task, *args, **keys):
        args_keys = (args, keys)
        results = []
        node = (task, args_keys, results)

        self.links.append( node )
        return task
    

    #Producer(qstrings, genstring)
################################################################################
################################################################################

def check_Threads():

    import time
    from pulo import random_string
    
    def decorate_str(str):
        return "-==@ " + str + " @==-"
    
    def pretty_print(str):
        Synched.out("[[ {str} ]]", str = str)
    
    threads = []
    producers = []
    counts = { 'producers': 2, 'consumers' : 2, 'transformers': 5}
    
    event_exit = threading.Event()
    event_pause = threading.Event()
    event_wake  = threading.Event()
    
    queue_input = Queue()
    queue_output = Queue()
    #queue_filtered = Queue()
    
    #
    # Producer target
    #
    def produce_str(e_exit, e_pause, e_wake, q_input, N):
        self = threading.current_thread()
        
        def produce():
            string = random_string(N)
            Synched.out("{name} produced << {prod} >>", name=str(self.name), prod=string)
            q_input.put(string)
            time.sleep(1)
            
        while True:
            if e_exit.is_set():
                break
            
            if e_pause.is_set():
                e_wake.wait()
                
            if e_wake.is_set():
                e_wake.clear()
                e_pause.clear()
                
            produce()
            
        Synched.out("{name} exiting", name = str(self.name))
        
    #
    # Producers
    #
    for k in xrange(0, counts['producers']):
        n = 10+k
         
        thread = threading.Thread(
                target=produce_str, 
                name = ("Producer[%d]" % k),           
                args=(event_exit, event_pause, event_wake, queue_input, n)
            )
        threads.append(thread)
    producers = threads
     
    #
    # Transformer target
    #
    def transform_str(e_exit, e_pause, e_wake, q_input, q_output, f_mapitem):
        self = threading.current_thread()
         
        e_any = OrEvent(e_exit, e_pause, e_wake)
         
        def transform():
            try:
                item = q_input.get_nowait()
                q_input.task_done()
                result = f_mapitem(item)
                q_output.put(result)
                Synched.out("{name} transformed << {prod} | {trans}>>", 
                        name=str(self.name), 
                        prod=str(item),trans = result)
                 
                return True
            except Empty:
                Synched.out("{name} queue empty, sleeping...", 
                            name=str(self.name))
                time.sleep(1)
                return False
             
        while True:
            if e_exit.is_set():
                break
            transform()
             
        Synched.out("{name} exiting", name = str(self.name))
         
    #
    # Transformers
    #
    for k in xrange(0, counts['transformers']):
        thread = threading.Thread(
                target=transform_str, 
                name = ("Transformer[%d]" % k),           
                args=(event_exit, event_pause, event_wake, queue_input, 
                      queue_output, decorate_str)
            )
        threads.append(thread)
         
    #
    # Consumer target
    #
    def consume_str(e_exit, e_pause, e_wake, q_output, f_consume):#, q_output):
        self = threading.current_thread()
         
        e_any = OrEvent(e_exit, e_pause, e_wake)
         
        def consume():
            try:
                item = q_output.get_nowait()
                Synched.out("{name} consumed >> {prod} <<", name=str(self.name), 
                        prod=str(item))
                q_output.task_done()
                #q_output.put(item)
                ret = f_consume(item)
                if False == ret:
                    return False
                else:
                    return True
            except Empty:
                Synched.out("{name} queue empty, sleeping...", 
                            name=str(self.name))
                time.sleep(1)
                return False
             
        while True:
            if e_exit.is_set():
                break
            consume()
             
        Synched.out("{name} exiting", name = str(self.name))
     
    #  
    # Consumers
    #
    for k in xrange(0, counts['consumers']):
        n = 10+k
 
        thread = threading.Thread(
                target=consume_str, 
                name = ("Consumer[%d]" % k),           
                args=(event_exit, event_pause, event_wake, queue_output, 
                      pretty_print)#, queue_output)
            )
        threads.append(thread)

    start_all(threads)
    
    data = None
    try:
        while True:
            data = raw_input("Quit? [y/n] ")
            if data == "y" or data == "Y":
                break
            elif data == "s" or data == "S":
                Synched.out("Putting them to sleep for 10 secs.")
                event_pause.set()
                time.sleep(10)
                event_wake.set()
    except EOFError:
        pass
    
    event_exit.set()
    
    join_all(threads)
    
    def empty_queue(q, name):
        print ""
        print "%s: [" % str(name)
        while False == q.empty():
            item = q.get()
            print "%s" % item
        print "]"
        
    empty_queue(queue_input, "queue_input")
    #empty_queue(queue_filtered, "queue_filtered")
    empty_queue(queue_output, "queue_output")
    


    
class Task2(object):
    # general task
    def __init__(self, name, f, *a, **ka):
        self.name = name # name string tag
        self.f = f # fun
        self.a = a # args
        self.ka = ka # kwargs
        self.worker = None# caller ref
        self.is_attached = False #
        
    def __call__(self, *args, **keys):
        args.prepend(self.a)
        keys.update(self.ka)
        return self.f(*args, **keys)


#
# Worker: This class serves as a base for all Tasked threads
#
class TaskedWorker(threading.Thread):
    class State:
        WORKING = 1
        SLEEPING = 2
        ERROR = -1
    
    def __init__(self, tasks_queue, 
                 e_quit = threading.Event(),
                 e_pause = threading.Event(),
                 **opts):
        self.q_tasks = tasks_queue
        self.e_quit = e_quit
        self.e_pause   = e_pause
        self.e_newtask = threading.Event()
        name = ""
        if 'name' in opts:
            name = opts['name']
        super(TaskedWorker, self).__init__(name=name)
    
    def fetch_args(self, task):
        return ((), {})
    
    def fetch_taskitem(self):
        try:
            task = self.q_tasks.get_nowait()
        except Empty:
            task = None
        return task
    
    # Do something with the results
    def do_results(self, task, result):
        """Do something with the results. Implement this in your subclass."""
        pass
    
    def do_task(self):
        try:
            task = self.fetch_taskitem()
            args, keys = self.fetch_args(task)
            if task:
                task_results = task(*args, **keys)
                self.do_results(task, task_results)
        except Empty:
            pass
        
    def run(self):
        or_events = OrEvent(self.e_quit, self.e_pause, self.e_newtask)
        while True:
            if self.e_quit.is_set():
                break
            if self.e_pause.is_set():
                pass
            self.do_task()

    def pause(self):
        pass
    
    def resume(self):
        pass
    
    def push(self, task):
        self.q_tasks.put(task)
        self.e_newtask.set()
        
def check_Worker2():
    from pulo import random_string
    import random
    
    counts = {'producers': 5, 'consumers': 10}
    indices = {'producers': 0, 'consumers': 1}
    names =  ["Producer[%d]", "Consumer[%d]"]
    
    def print_thread(fmt, *args, **kw):
        name = threading.current_thread().name
        fmt = name + ": " + fmt
        return Synched.out(fmt, *args, **kw)
        
    def produce_number(min_, max_):
        n = random.randint(min_, max_)
        print_thread("produce_number: {min_} < {n} < {max_}", min_ = min_, n = n, 
                     max_ = max_)
        return n
    
    def produce_str(N):
        s = random_string(N)
        print_thread("produce_str: <{s}>; N = {N}", s = s, N = N)
        return s 
    
    def decorate_str(str):
        ret = "-==@ " + str + " @==-"
        print_thread("decorate_str: <{ret}>", ret = ret)
        return ret
    
    def pretty_print(str):
        print_thread("{{ {str} }}", str = str)
    
    def delay(seconds):
        print_thread("delaying for {sec}s", sec=seconds)
        time.sleep(seconds)
        
    task_num = Task(produce_number, 5, 25)
    task_str = Task(produce_str, N = task_num)
    task_str.link(Task(delay), 2)# .link(Task(delay), 2)
    #print "task_num():", task_num()
    #print "task_str():", task_str()
    
    e_quit = threading.Event()
    q_tasks = Queue()
    threads = []
    
    def create_threads(which, queue):
        for x in xrange(1, counts[which]):
            name = names[indices[which]] % x
            thread = QueueWorker(queue, e_quit, name=name)
            threads.append(thread)
            
    create_threads('producers', q_tasks)
    
    start_all(threads)
    
    Synched.out("started")
    try:
        while True:
            inp = raw_input("> ")
            if inp == "y":
                break
            elif inp == "a":
                for x in xrange(''):
                    pass
                q_tasks.put(task_str)
    except EOFError, err:
        pass
    
    e_quit.set()
    join_all(threads)
    
    def empty_queue(q, name):
        print ""
        print "%s: [" % str(name)
        while False == q.empty():
            item = q.get()
            print "%s" % item
        print "]"
        
    empty_queue(q_tasks, "queue_input")
    
    
#     q_tasks = Queue()
#     
#     
#     t1 = Worker()
#     t1.start()
#     t1.push(task)
#
# This Worker .has: Tasks 
#
class Worker2(threading.Thread):
    class State:
        WAITING = 1
        WORKING = 0
        SHUTTING_DOWN = -1

    def __init__(self, name, 
                 event_stop = threading.Event(), 
                 event_newtask = threading.Event(),
                 event_pause = threading.Event(),
                 tasks_queue = Queue()):
        super(QueueWorker, self).__init__()
        self.name = name
        self.event_stop = event_stop
        self.event_newtask = event_newtask
        self.event_pause = event_pause
        
        self.tasks_queue = tasks_queue
        
        self.event_or = OrEvent(self.event_stop, self.event_newtask, self.event_pause)
        
        self.state = QueueWorker.State.WAITING
    
    def do_task(self):
        try:
            task = self.tasks_queue.get_nowait()
            self.state = QueueWorker.State.WORKING
            
            result = task.f(*task.a, **task.ka)
            
            self.tasks_queue.task_done()
            self.state = QueueWorker.State.WAITING
            
        except Empty:
            self.event_newtask.clear()
            
    def run(self):
        while True:
            self.event_or.wait()

            if self.event_stop.is_set():
                self.state = QueueWorker.State.SHUTTING_DOWN
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



def check_Worker3():
    from pulo import random_string
    
    def print_random_string(n):
        str = random_string(n)
        Synched.out("print_random_string:: {rnd}", rnd = str)
    
    def print_string(fmt, *args, **kw):
        Synched.out(fmt, *args, **kw)
    
    
    def decorate_string(string):
        string = "<<" + string + ">>"
    producer = QueueWorker("producer")
    
    try:
        while True:
            data = raw_input("Enter some data> ")
            Synched.out("value? {value}; type? {type}", value = data, type = type(data))
            
            producer.quit()
            producer.join()
            #t1 = Task("random_string", print_random_string, 17)
    except EOFError:
        print "Quitting"
        


        
#
# This Worker .has: *Tasks! and *Events! and is a nice candidate for Multiple Inheritance with List, but NOOOOO
#   This class Will _behave_ like a list if I copy all the _Public_interface of the list() class 
#
# class TaskedWorker(threading.Thread):
# 
#     class State:
#         WAITING = 2
#         WORKING = 1
#         SHUTTING_DOWN = 0
#         ERROR = -1
#     
#     def __init__(self, 
#                  tasks_queue,
#                  event_stop = threading.Event(),
#                  event_pause = threading.Event(),
#                  **options):
#         #:~Self.init!
#         self.options = options.copy()
#         self.tasks_queue = tasks_queue
#         self.event_newtask = threading.Event()
#         self.event_stop = event_stop
#         self.event_pause = event_pause
#         
#         target = None
#         if 'target' in options:
#             self.target = options.pop('target')
#             
#         name = ""
#         if 'name' in options:
#             name = options.pop('name')
#             
#         if 'results_queue' in options:
#             self.results_queue = options['results_queue']
#         else:
#             self.results_queue = None
#         
#         super(TaskedWorker, self).__init__(target=target, name=name, **options)
#         
#         self.event_stop = event_stop
#         self.tasks_queue = tasks_queue
#         self.event_or = OrEvent(self.event_stop, self.event_newtask, self.event_pause)
#         self.state = Worker.State.WAITING
#     
#     def do_task(self):
#         try:
#             task = self.tasks_queue.get_nowait()
#             self.state = Worker.State.WORKING
#             
#             if self.target:
#                 result = self.target(task)
#             else:
#                 result = task()
#                 
#             if self.results_queue:
#                 self.results_queue.put(result)
#                 
#             self.tasks_queue.task_done()
#             self.state = Worker.State.WAITING
#             
#         except Empty:
#             self.event_newtask.clear()
#             
#     def run(self):
#         while True:
#             Synched.out("TaskedWorker:{name}:: time_tick", name=self.name)
#             self.event_or.wait()
# 
#             if self.event_stop.is_set():
#                 self.state = Worker.State.SHUTTING_DOWN
#                 break
#             elif self.event_newtask.is_set():
#                 self.do_task()
#             #else:
#             #    self.do_task()
# 
#                 
#     def push(self, task):
#         self.tasks_queue.put(task)
#         self.event_newtask.set()
#         
#     def pause(self, name = None, timeout = 0):
#         """ eg. suspend thread tasks[name].event.wait() """
#         self.event_or.clear()
#         
#     def resume(self):
#         self.event_or.set()
#     
#     def quit(self):
#         """ e.g stop everethyng and destroy thread process """
#         self.event_stop.set()
#         
#     def state(self):
#         """ return info about current state 
#         is it working on task or paused waiting etc
#         will be used from task.calller.state
#         """
#         return self.state

# class Producer(threading.Thread):
#     class State:
#         PRODUCING = 1
#         SLEEPING = 2
#         SHUTTING_DOWN = 0
#         ERROR = -1
#         
#     def __init__(self, 
#                  output_queue,
#                  target,
#                  args = [],
#                  event_stop = threading.Event(),
#                  event_pause = threading.Event(),
#                  event_wakeup = threading.Event(),
#                  **options):
#         :~Self.init!
#         self.output_queue = output_queue
#         self.event_stop = event_stop
#         self.event_pause = event_pause
#         self.event_wakeup = event_wakeup
#         self.target = target
#         
#         name = ""
#         if 'name' in options:
#             name = options.pop('name')
#             
#         super(Producer, self).__init__(name=name, **options)
# 
#         self.args = args
#        
#         self.event_stop = event_stop
#         self.output_queue = output_queue
#         self.event_or = OrEvent(self.event_stop, self.event_pause, self.event_wakeup)
# 
#         self.state = Producer.State.PRODUCING
#         
#     def do_task(self):
#         self.output_queue.put(self.target(*self.args))
#     
#     def run(self):
#         while True:
#             if self.event_or.is_set():
#             if self.event_stop.is_set():
#                 self.state = Producer.State.SHUTTING_DOWN
#                 break
#             '''
#             elif self.event_pause.is_set():
#                 self.state = Producer.State.SLEEPING
#                 self.event_pause.clear()
#             elif self.event_wakeup.is_set():
#                 self.state = Producer.State.PRODUCING
#                 self.event_wakeup.clear()
#             '''
#             self.do_task()

# class Consumer(threading.Thread):
#     def __init__(self,
#                  input_queue,
#                  output_queue,
#                  target = None,
#                  args = (),
#                  stop_event = threading.Event(),
#                  newitems_event = threading.Event(),
#                  **options):
#         self.target = target
#         
#         name = ""
#         if 'name' in options:
#             name = options.pop('name')
#             
#         super(Consumer, self).__init__(name=name, **options)
#         
#         self.newitems_event = newitems_event
#         self.stop_event = stop_event
#         self.event_or = OrEvent(self.stop_event, self.newitems_event)
# 
#         self.input_queue = input_queue
#         self.output_queue = output_queue
# 
#     '''
#     def do_task(self):
#         try:
#             task = self.tasks_queue.get_nowait()
#             self.state = Worker.State.WORKING
#             
#             result = task.f(*task.a, **task.ka)
#             
#             self.tasks_queue.task_done()
#             self.state = Worker.State.WAITING
#             
#         except Empty:
#             self.event_newtask.clear()
#     '''
#     def do_task(self):
#         try:
#             item = self.input_queue.get_nowait()
#             if self.args:
#                 result = self.target(item, *self.args)
#             else:
#                 result = self.target(item)
#                 
#             self.output_queue.put(result)
#             self.input_queue.task_done()
#         except Empty:
#             self.newitems_event.clear()
#             '''
#     def run(self):
#         while True:
#             self.event_or.wait()
# 
#             if self.event_stop.is_set():
#                 self.state = Worker.State.SHUTTING_DOWN
#                 break
#             elif self.event_newtask.is_set():
#                 self.do_task()
#             else:
#                 self.do_task()
#                 '''
#     def run(self):
#         while True:
#             self.event_or.wait()
#             
#             if self.stop_event.is_set():
#                 break
#             elif self.newitems_event.is_set():
#                 self.do_task()
#             else:
#                 self.do_task()
#                     
#                     
# def check_ProducerConsumer():
#     from pulo import random_string
#     quit_event = threading.Event()
#     
#     randomstring_q = Queue()
#     decorated_q = Queue()
#     
#     def random_string_producer(name, n):
#         ret = random_string(n)
#         Synched.out("%s Generating >> %s <<" %(name,ret))
#         time.sleep(1)
#         return ret
#     
#     def decorate_string(string, name):
#         Synched.out("%s Decorating << %s >>" %(name, string))
#         string = "http://somehost.com/%s" % (string)
#         return string
#     
#     def print_string(name, string):
#         Synched.out("%s Printing << %s >>" %(name, string))
#     
#     threads = []
#     
#     for x in xrange(0,5):
#         n = 10 + x
#         name = "RandomStringProducer<n=%d>" % (n)
#         producer_thread = Producer(
#                  randomstring_q,
#                  random_string_producer,
#                  (name, n,), 
#                  event_stop = quit_event,
#                  name=name,
#                  )
#         
#         threads.append(producer_thread)
#          
#     #first_producer = threads[0]
#     #last_producer = threads[-1]
#     
#     for x in xrange(0,10):
#         n = x
#         name = "ConsumerDecorator<n=%d>" % (n)
#         consumer = Consumer(randomstring_q, decorated_q, 
#                             decorate_string, (name,), 
#                             stop_event = quit_event, name = name)
#         threads.append(consumer)
#     
#     start_all(threads)
#     try:
#         while True:
#             data = raw_input("Quit? [yY]> ")
#             if data == "y" or data == "Y":
#                 break
#     except EOFError:
#         pass
#     
#     print "Quitting"
#     quit_event.set()
#     join_all(threads)
#         
#     print "checking producer_queue:"
#     
#     while not randomstring_q.empty():
#         item = randomstring_q.get()
#         print "item:", str(item)
#         
#     print ""
#     print "decorated:"
#     while not decorated_q.empty():
#         item = decorated_q.get()
#         print "decorated(item):", str(item)
        
if __name__ == "__main__":
    checks = [
              #check_Worker_basic,
              #check_Producer_Worker,
              check_Pipe_Producer
              ]
    for check in checks:
        check()