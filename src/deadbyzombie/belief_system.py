'''
belief_system.py
by Mike Kramlich
'''

#from groglogic.mainapp.mind import HasMind
from has_mind import HasMind

class BeliefSystem:
    def __init__(self):
        pass

    def believe(self, thing, belief):
        if isinstance(thing,HasMind):
            thing.mind.beliefs.append(belief)

    def has_belief(self, thing, belief):
        if isinstance(thing,HasMind):
            if belief in thing.mind.beliefs: return True
            else: return False
        else: return False

    def clear_beliefs(self, thing):
        if isinstance(thing,HasMind):
            thing.mind.beliefs = []

    def list_beliefs(self, thing):
        if isinstance(thing,HasMind):
            return thing.mind.beliefs
        else: return []

    def report_beliefs(self, thing, delim='\n'):
        bl = self.list_beliefs(thing)
        bl = map(lambda b: '"'+b+'"',bl)
        return delim.join(bl)

    def dev_report(self, thing, delim='\n', indent='  '):
        s = indent + self.report_beliefs(thing,delim)
        return s

    def log(self, msg):
        print msg

    def debug(self, msg):
        print msg

class HasBeliefs:
    def __init__(self):
        if not hasattr(self,'beliefs'):
            self.beliefs = []

#EOF
