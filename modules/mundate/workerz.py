'''
Created on Jul 15, 2015

@author: dakkar
'''
import threading
from Queue import Queue, Empty

import time

from borgs import Synched


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

def or_event(event, *events):
    def or_set(self):
        self._set()
        self.changed()
    
    def or_clear(self):
        self._clear()
        self.changed()
    
    def orify(e, changed_callback):
        if False == _is_patched(e):
            e._set = e.set
            e._clear = e.clear
            e.changed = changed_callback
            e.set = lambda: or_set(e)
            e.clear = lambda: or_clear(e)
        
    def _is_patched(e):
        Synched.out("True? %s / _is_patched" % str(e))
        if '_set' in e.__dict__:
            return True
        elif '_clear' in e.__dict__:
            return True
        return False
    
    if event is None:
        event = threading.Event()
        
    def changed():
        bools = [e.is_set() for e in events]
        if any(bools):
            event.set()
        else:
            event.clear()
            
    for e in events:
        orify(e, changed)
            
    changed()
    return event

def check_OrEvent():
    return None
    import time
    
    def wait_on(name, e):
        print "Waiting on %s..." % (name,)
        e.wait()
        print "%s fired!" % (name,)
    e1 = threading.Event()
    e2 = threading.Event()

    or_e = OrEvent(e1, e2)
    or_e2 = OrEvent(e1, e2)

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
    
def start_all(threads):
    for thread in threads:
        thread.start()
        
def join_all(threads):
    for thread in threads:
        thread.join()

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
#
# Worker: This class serves as a base for all Tasked threads
#
class Worker(threading.Thread):
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
        super(Worker, self).__init__(name=name)
    
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
            task_results = task(*args, **keys)
            self.do_results(task, task_results)
        except Empty:
            pass
        
    def run(self):
        or_events = OrEvent(self.e_quit, self.e_pause, self.e_newtask)
        while True:
            if self.e_quit.is_set():
                break
            if or_events.wait():
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
        
def check_Worker():
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
            thread = Worker(queue, e_quit, name=name)
            threads.append(thread)
            
    create_threads('producers', q_tasks)
    
    start_all(threads)
    Synched.out("here")
    try:
        while True:
            inp = raw_input()
            if inp == "y":
                break
            elif inp == "a":
                pass
    except EOFError, err:
        pass
    e_quit.set()
    
    
    
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



def check_Worker2():
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
class TaskedWorker(threading.Thread):

    class State:
        WAITING = 2
        WORKING = 1
        SHUTTING_DOWN = 0
        ERROR = -1
    
    def __init__(self, 
                 tasks_queue,
                 event_stop = threading.Event(),
                 event_pause = threading.Event(),
                 **options):
        #:~Self.init!
        self.options = options.copy()
        self.tasks_queue = tasks_queue
        self.event_newtask = threading.Event()
        self.event_stop = event_stop
        self.event_pause = event_pause
        
        target = None
        if 'target' in options:
            self.target = options.pop('target')
            
        name = ""
        if 'name' in options:
            name = options.pop('name')
            
        if 'results_queue' in options:
            self.results_queue = options['results_queue']
        else:
            self.results_queue = None
        
        super(TaskedWorker, self).__init__(target=target, name=name, **options)
        
        self.event_stop = event_stop
        self.tasks_queue = tasks_queue
        self.event_or = OrEvent(self.event_stop, self.event_newtask, self.event_pause)
        self.state = Worker.State.WAITING
    
    def do_task(self):
        try:
            task = self.tasks_queue.get_nowait()
            self.state = Worker.State.WORKING
            
            if self.target:
                result = self.target(task)
            else:
                result = task()
                
            if self.results_queue:
                self.results_queue.put(result)
                
            self.tasks_queue.task_done()
            self.state = Worker.State.WAITING
            
        except Empty:
            self.event_newtask.clear()
            
    def run(self):
        while True:
            Synched.out("TaskedWorker:{name}:: time_tick", name=self.name)
            self.event_or.wait()

            if self.event_stop.is_set():
                self.state = Worker.State.SHUTTING_DOWN
                break
            elif self.event_newtask.is_set():
                self.do_task()
            #else:
            #    self.do_task()

                
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

class Producer(threading.Thread):
    class State:
        PRODUCING = 1
        SLEEPING = 2
        SHUTTING_DOWN = 0
        ERROR = -1
        
    def __init__(self, 
                 output_queue,
                 target,
                 args = [],
                 event_stop = threading.Event(),
                 event_pause = threading.Event(),
                 event_wakeup = threading.Event(),
                 **options):
        #:~Self.init!
        self.output_queue = output_queue
        self.event_stop = event_stop
        #self.event_pause = event_pause
        #self.event_wakeup = event_wakeup
        self.target = target
        
        name = ""
        if 'name' in options:
            name = options.pop('name')
            
        super(Producer, self).__init__(name=name, **options)

        self.args = args
       
        self.event_stop = event_stop
        self.output_queue = output_queue
        #self.event_or = OrEvent(self.event_stop, self.event_pause, self.event_wakeup)

        self.state = Producer.State.PRODUCING
        
    def do_task(self):
        self.output_queue.put(self.target(*self.args))
    
    def run(self):
        while True:
            #if self.event_or.is_set():
            if self.event_stop.is_set():
                self.state = Producer.State.SHUTTING_DOWN
                break
            '''
            elif self.event_pause.is_set():
                self.state = Producer.State.SLEEPING
                self.event_pause.clear()
            elif self.event_wakeup.is_set():
                self.state = Producer.State.PRODUCING
                self.event_wakeup.clear()
            '''
            self.do_task()

class Consumer(threading.Thread):
    def __init__(self,
                 input_queue,
                 output_queue,
                 target = None,
                 args = (),
                 stop_event = threading.Event(),
                 newitems_event = threading.Event(),
                 **options):
        self.target = target
        
        name = ""
        if 'name' in options:
            name = options.pop('name')
            
        super(Consumer, self).__init__(name=name, **options)
        
        self.newitems_event = newitems_event
        self.stop_event = stop_event
        self.event_or = OrEvent(self.stop_event, self.newitems_event)

        self.input_queue = input_queue
        self.output_queue = output_queue

    '''
    def do_task(self):
        try:
            task = self.tasks_queue.get_nowait()
            self.state = Worker.State.WORKING
            
            result = task.f(*task.a, **task.ka)
            
            self.tasks_queue.task_done()
            self.state = Worker.State.WAITING
            
        except Empty:
            self.event_newtask.clear()
    '''
    def do_task(self):
        try:
            item = self.input_queue.get_nowait()
            if self.args:
                result = self.target(item, *self.args)
            else:
                result = self.target(item)
                
            self.output_queue.put(result)
            self.input_queue.task_done()
        except Empty:
            self.newitems_event.clear()
            '''
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
                '''
    def run(self):
        while True:
            self.event_or.wait()
            
            if self.stop_event.is_set():
                break
            elif self.newitems_event.is_set():
                self.do_task()
            else:
                self.do_task()
                    
                    
def check_ProducerConsumer():
    from pulo import random_string
    quit_event = threading.Event()
    
    randomstring_q = Queue()
    decorated_q = Queue()
    
    def random_string_producer(name, n):
        ret = random_string(n)
        Synched.out("%s Generating >> %s <<" %(name,ret))
        time.sleep(1)
        return ret
    
    def decorate_string(string, name):
        Synched.out("%s Decorating << %s >>" %(name, string))
        string = "http://somehost.com/%s" % (string)
        return string
    
    def print_string(name, string):
        Synched.out("%s Printing << %s >>" %(name, string))
    
    threads = []
    
    for x in xrange(0,5):
        n = 10 + x
        name = "RandomStringProducer<n=%d>" % (n)
        producer_thread = Producer(
                 randomstring_q,
                 random_string_producer,
                 (name, n,), 
                 event_stop = quit_event,
                 name=name,
                 )
        
        threads.append(producer_thread)
         
    #first_producer = threads[0]
    #last_producer = threads[-1]
    
    for x in xrange(0,10):
        n = x
        name = "ConsumerDecorator<n=%d>" % (n)
        consumer = Consumer(randomstring_q, decorated_q, 
                            decorate_string, (name,), 
                            stop_event = quit_event, name = name)
        threads.append(consumer)
    
    start_all(threads)
    try:
        while True:
            data = raw_input("Quit? [yY]> ")
            if data == "y" or data == "Y":
                break
    except EOFError:
        pass
    
    print "Quitting"
    quit_event.set()
    join_all(threads)
        
    print "checking producer_queue:"
    
    while not randomstring_q.empty():
        item = randomstring_q.get()
        print "item:", str(item)
        
    print ""
    print "decorated:"
    while not decorated_q.empty():
        item = decorated_q.get()
        print "decorated(item):", str(item)
        
if __name__ == "__main__":
    #check_OrEvent()
    #check_Threads()
    check_Worker()
    #check_ProducerConsumer()