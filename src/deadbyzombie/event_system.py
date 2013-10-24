'''
event_system.py
by Mike Kramlich
this module provides solely: class EventSystem
'''

import time

# My Libraries
from lib import StopWatch, assertNotNone, tostr, get_set_with_class_and_all_super_classes

from pprint import pformat

class EventSystem:
    def __init__(self):
        pass

    def log(self, msg):
        print msg

    def debug(self, msg):
        if self.debuglogging:
            self.log(msg)

    def reset(self):
        self.init()

    def init(self):
        self.init_clock()
        self.init_eventqueue()
        self.init_event_listeners()

    def init_clock(self):
        self.tock = 0

    def init_eventqueue(self):
        self.debuglogging = True
        self.eventqueue = []
        self.max_event_process_count_per_call = 1000

    def init_event_listeners(self):
        self.eventlistenersmap = {}

    def remove_listener(self, receipt_from_original_add):
        eventclass, listenerdef = receipt_from_original_add
        elmap = self.eventlistenersmap
        if eventclass in elmap:
            listenerdeflist = elmap[eventclass]
            if listenerdef in listenerdeflist:
                listenerdeflist.remove(listenerdef)
                self.debug('removed listener for event class '+str(eventclass)+'; listener was: '+str(listenerdef))
            else:
                self.log('tried to remove listener for event class '+str(eventclass)+' but was not found; listener was: '+str(listenerdef))
        else:
            self.log('tried to remove listener for event class '+str(eventclass)+' but no entry for that event name')

    def add_listener(self, eventspec, targetobj, targetmethodname, first=False):
        eventclass = eventspec[0]
        eventmatchparams = eventspec[1]
        s =  'ev.add_listener():\n'
        s += 'event class:'   + str(eventclass) + '\n'
        s += 'mparams:' + str(eventmatchparams) + '\n'
        s += 'tobj:'    + str(targetobj) + '\n'
        s += 'tmeth:'   + str(targetmethodname)
        self.debug(s)
        handleparams = {'first':first}
        newlistenerdef = (handleparams, eventmatchparams, targetobj, targetmethodname)
        elmap = self.eventlistenersmap
        listenerdeflist = None
        if eventclass in elmap: 
            listenerdeflist = elmap[eventclass]
        else:
            listenerdeflist = []
            elmap[eventclass] = listenerdeflist
        if first:
            listenerdeflist.insert(0,newlistenerdef)
        else:
            listenerdeflist.append(newlistenerdef)
        receipt = (eventclass, newlistenerdef)
        # we return a receipt (more like a coat claim tag) so if the caller wants he can hold onto it and use it later to ask us to deregister his listener
        return receipt

    def enqueue_event(self, event):
        self.debug('enqueue_event: %s' % event)
        #assert isinstance(event,Event) ?

        #TODO use self.now() instead of self.tock; let apps (or subclasses of ES) decide what now() returns (whether a tock int, or a timestamp, etc.)
        event._tock_enqueued = self.tock
        self.eventqueue.append(event)

    def event_queue_size(self):
        return len(self.eventqueue)

    def are_events(self):
        return self.event_queue_size() > 0

    def peek_event(self):
        if self.event_queue_size() > 0: 
            return self.eventqueue[0]
        else: return None

    def dequeue_event(self):
        if self.event_queue_size() > 0: 
            return self.eventqueue.pop(0)
        else: return None

    def tick_and_process_events(self, tickqty=1):
        msgpre = 'tick_and_process_events: total dur: '
        msgsuf =  ' for ' + str(tickqty) + ' ticks\n'
        watch = StopWatch(msgpre,msgsuf)
        s = '\ntick_and_process_events():'
        if tickqty > 1:
            s += ': tickqty=' + str(tickqty)
        self.debug(s)
        for i in xrange(tickqty):
            self.tick()
            self.process_events()
        self.log(watch.stop())

    def tick(self):
        self.log('tick()')
        self.tock += 1
        event = TickEvent(self.tock)
        self.enqueue_event(event)

    def process_events(self):
        self.debug('process_events()')
        count = 0
        while self.are_events() and self.is_event_process_count_under_max(count):
            event = self.dequeue_event()
            self.debug('processing event: '+str(event))
            count += 1
            self.handle_event(event)
        self.debug('\nevents processed count: ' + str(count) + '\n')
        if self.are_events():
            #we deduce the loop above exitted because event proc count hit max
            self.debug('events left in queue: '+str(self.event_queue_size()))

    def is_event_process_count_under_max(self, count):
        return count < self.max_event_process_count_per_call

    def handle_event(self, event):
        self.debug('handle_event(): event: '+str(event))
        #eventname = event['name']
        eventclass = event.__class__
        eventname = event.__class__.__name__

        eventclasses = get_set_with_class_and_all_super_classes(eventclass)
        lisdefs = []
        for cl in eventclasses:
            lds = self.get_listenerdefs_for_eventclass(cl)
            for ld in lds:
                if ld not in lisdefs:
                    lisdefs.append(ld)

        if len(lisdefs) == 0:
            self.log('no listeners for event class "%s" so returning early' % eventclass)
            return
        self.debug('eval '+str(len(lisdefs))+' listeners for event class: '+str(eventclass))
        for lisdef in lisdefs:
            handleparams = lisdef[0]
            evmatchparams = lisdef[1]
            targetobj = lisdef[2]
            targetmethodname = lisdef[3]
            self.debug('evmatchparams: '+str(evmatchparams))
            match = True
            for k in evmatchparams:
                if not hasattr(event,k):
                    self.debug('event %s did not have attribute %s, which listener %s specifies a value for, so listener does not match this event' % (event,k,lisdef))
                    match = False
                    break
                event_attr_val = getattr(event,k)
                if event_attr_val != evmatchparams[k]:
                    self.debug('evmatchparam "%s" value "%s" did not match event value "%s"' % (k,evmatchparams[k],event_attr_val))
                    match = False
                    break # was continue before, so this should be perf boost
            if match:
                self.debug('found matching listener, so firing it; lisdef= ' + str(lisdef))
                targetmethod = getattr(targetobj,targetmethodname)
                targetmethod(event)
            else:
                self.debug('the listener we checked didnt match for this events parameters so skipping')

    def get_listenerdefs_for_eventclass(self, eventclass):
        #TODO make answer reflect whether listeners of super/subclasses of given eventclass
        elmap = self.eventlistenersmap
        if eventclass in elmap:
            return elmap[eventclass]
        else:
            return []

    def meet_event_execute_reqs(self, event):
        #TODO optional param for app to tell it what exe handler fn to use
        elmap = self.eventlistenersmap
        #eventname = event['name']
        eventclass = event.__class__
        eventname = eventclass.__name__
        lisdeflist = elmap[eventclass]
        found_execute_handler = False
        executefn = None
        for lisdef in lisdeflist:
            #GUIDE: lisdef = (handleparams, eventmatchparams, tobj, tmethodname)
            tobj = lisdef[2]
            tmethname = lisdef[3]
            if tmethname.startswith('execute_'):
                found_execute_handler = True
                boundmeth = getattr(tobj,tmethname)
                executefn = boundmeth
                break

        meetsreqs = True

        if found_execute_handler:
            if not hasattr(executefn,'reqs'): return True
            reqs = getattr(executefn,'reqs')
            if isinstance(reqs,type([])):
                for req in reqs:
                    # we assume that every req fn uses the same 'self' obj as that used by the target execute handler fn, namely: tobj
                    if not req(tobj,event):
                        meetsreqs = False
                        break
            else:
                req = reqs
                # same comment as above about assuming tobj is the self
                meetsreqs = req(tobj,event)
        else:
            self.log('meet_event_execute_reqs(): could not find execute handler in reg listeners for event class '+str(eventclass)+' so will return False indicating the execute precondition reqs failed')
            meetsreqs = False
        return meetsreqs
# EventSystem class end

class Event:
    def __init__(self):
        self._tock_enqueued = None

    def assertValid(self):
        pass

    def __str__(self):
        return tostr(self)

class TickEvent(Event):
    def __init__(self, tock):
        Event.__init__(self)
        assertNotNone('tock',tock)
        self.tock = tock

'''
TODO

an app who registers a listener can indicate what his listener calling order inter-dependency needs are, for example, he can say that listener X must be called at some point after listener Y; and somebody can say that listener Y must be called at some point after listener Z; and the event system engine will analyze all the dependency needs for all the listeners for a particular event, and figure out exactly what order it should call them in, so as to best satisfy their depedency declarations. Kinda like Ant and it's target dependency declaration system. To make this hapen, would be conveneitn if app can give a string name for a particualr listener, that way he can declare his dependencies in terms of listener names rather than listener objects

firelimit and firecount: a listenerdef can specify the max times it should be fired before it's automatically deregistered by this code; this code increments a firecount attached to the listenerdef each time it is successfully fired; if no firelimit param in the listenerdef's spec hash, there is no limit; you can also specify that it only be called every Nth time it would normally have fire...you can also specify that one of the matching conditions is that the current self.tock must be T, in addition to the other matchparams (useful for non-tick event listeners as well as for tick listeners)...you can also specify value ranges like 'r':'>=5' and that value string '>=5' will get parsed and processed as you would expect, ensuring that the value of event param 'r' was >= 5
'''

#EOF 
