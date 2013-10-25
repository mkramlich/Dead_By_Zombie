'''
thought_system.py
by Mike Kramlich
'''

from has_mind import HasMind

class ThoughtSystem:
    def __init__(self):
        self.plugin = None

    def think(self, thing, thought):
        if isinstance(thing,HasMind):
            mind = thing.mind
            if mind.thoughts == None:
                mind.thoughts = []
            mind.thoughts.append(thought)

    def unthink(self, thing, thought):
        if isinstance(thing,HasMind):
            mind = thing.mind
            if mind.thoughts != None and thought in mind.thoughts:
                mind.thoughts.remove(thought)

    def clear_thoughts(self, thing):
        if isinstance(thing,HasMind):
            thing.mind.thoughts = []

    def has_thought(self, thing, thought):
        if isinstance(thing,HasMind):
            if thought in thing.mind.thoughts: return True
            else: return False
        else: return False

    def list_thoughts(self, thing):
        if isinstance(thing,HasMind):
            return thing.mind.thoughts
        else: return None

    def report_thoughts(self, thing, delim='\n'):
        thl = self.list_thoughts(thing)
        thl = map(lambda th: '"'+th+'"',thl)
        return delim.join(thl)

    def dev_report(self, thing, delim='\n', indent='  '):
        return indent + self.report_thoughts(thing,delim)

class ThoughtSystemPlugin:
    def __init__(self):
        pass

    def get_tock(self):
        pass

    def log(self, msg):
        pass

    def debug(self, msg):
        pass

class HasThoughts:
    def __init__(self):
        if not hasattr(self,'thoughts'):
            self.thoughts = []
