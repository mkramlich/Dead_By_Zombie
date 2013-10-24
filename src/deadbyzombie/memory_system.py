'''
memory_system.py
by Mike Kramlich
'''

#from groglogic.mainapp.mind import HasMind
from has_mind import HasMind

class MemorySystem:
    #TODO method to make forget all memories with a certain 'when' value
    #TODO method to make forget all memories with 'when' older (or more recent) than a given time
    #TODO a memory may be tagged as secret or private or embarassing, etc.
    #TODO methods to return list of all a thing's secret (or non-secret) memories; same for private, embarassing, and any other meta-tags a memory can have
    def __init__(self):
        self.plugin = None
        
    def remember(self, thing, memory, when=None):
        if isinstance(thing,HasMind):
            if not hasattr(thing.mind,'memories'):
                thing.mind.memories = None
            mind = thing.mind
            if mind.memories == None:
                mind.memories = {}
            # when is the time/moment when memory formed or is about
            if when == None:
                tock = 'default-tock'
                if self.plugin != None:
                    tock = self.plugin.get_tock()
                when = tock
            #print 'when ' + str(when)
            #print 'mems ' + str(mind.memories)
            if when not in mind.memories:
                mind.memories[when] = None
            if mind.memories[when] == None:
                mind.memories[when] = []
            #print 'ADDED memory: ' + memory
            mind.memories[when].append(memory)
        else:
            print '\n'+str(thing) + ' remember call ignored because thing does not HasMemories; memory: ' + str(memory) + '\n'

    def forget(self, thing, memory, when=None):
        'giving when is useful to distinguish between otherwise identical memories formed at two or more moments in time; for example, you might have been attacked twice by a rat in your life, so there would be two distinct memories named "attacked by rat", but each with different "when" values'
        pass #TODO write me

    def clear_memories(self, thing):
        if isinstance(thing,HasMind):
            thing.mind.memories = None

    def memories_as_dict(self, thing):
        'returned dict entries format: when:[memory1,memory2,...]'
        if isinstance(thing,HasMind):
            return thing.mind.memories
        else: return None

    def list_memories(self, thing):
        allmems = []
        if isinstance(thing,HasMind):
            memdict = self.memories_as_dict(thing)
            if memdict is not None:
                for k in memdict:
                    mems4when = memdict[k]
                    allmems.extend(mems4when)
        return allmems

    def report_memories(self, thing, delim='\n'):
        s = ''
        memdict = self.memories_as_dict(thing)
        if memdict != None:
            for k in memdict:
                mems = memdict[k]
                t = ''
                for m in mems:
                    if len(t) > 0: t += '; '
                    t += str(m)
                s += t + ' (' + str(k) + ')' + delim
        return s

    def dev_report(self, thing, delim='\n', indent='  '):
        s = indent + self.report_memories(thing,delim) + delim
        return s

class MemorySystemPlugin:
    def __init__(self):
        pass

    def get_tock(self):
        pass

    def log(self, msg):
        pass

    def debug(self, msg):
        pass

class HasMemories:
    def __init__(self):
        if not hasattr(self,'memories'):
            self.memories = None
