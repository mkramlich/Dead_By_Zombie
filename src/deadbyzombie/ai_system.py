'''
ai_system.py
by Mike Kramlich
'''

import random

from fact_system import FactSystem
from skill_system import SkillSystem
from memory_system import MemorySystem
from belief_system import BeliefSystem
from thought_system import ThoughtSystem
from goal_system import GoalSystem

from lib import sentence

class AiSystem:
    def __init__(self, fa=None, sk=None, mem=None, be=None, go=None, th=None):
        if fa is None: self.fa = FactSystem()
        else: self.fa = fa

        if sk is None: self.sk = SkillSystem()
        else: self.sk = sk

        if mem is None: self.mem = MemorySystem()
        else: self.mem = mem

        if be is None: self.be = BeliefSystem()
        else: self.be = be

        if go is None: self.go = GoalSystem()
        else: self.go = go

        if th is None: self.th = ThoughtSystem()
        else: self.th = th

    def dev_report_thing_and_his_mind(self, thing, delim='\n', indent='  '):
        s = []
        mind = thing.mind

        def pretty(prefix,rep,delim):
            if len(rep) == 0: rep = ' none' + delim
            else: rep = delim + rep + delim
            return prefix + ':' + rep

        rep = self.fa.dev_report(thing,delim=delim,indent=indent).strip()
        s.append(pretty("thing's facts",rep,delim))

        rep = self.fa.dev_report(mind,delim=delim,indent=indent).strip()
        s.append(pretty("mind's facts",rep,delim))

        rep = self.sk.dev_report(thing,delim=delim,indent=indent).strip()
        s.append(pretty('skills',rep,delim))

        rep = self.mem.dev_report(thing,delim=delim,indent=indent).strip()
        s.append(pretty('memories',rep,delim))

        rep = self.be.dev_report(thing,delim=delim,indent=indent).strip()
        s.append(pretty('beliefs',rep,delim))

        rep = self.go.dev_report(thing,delim=delim,indent=indent).strip()
        s.append(pretty('goals',rep,delim))

        rep = self.th.dev_report(thing,delim=delim,indent=indent).strip()
        s.append(pretty('thoughts',rep,delim))

        return ''.join(s)

    def would_say_something_aloud_randomly_now(self, thing):
        return thing.is_capable_of_speech() and thing.is_capable_of_random_speech_by_ai() and thing.randomspeechset != None and len(thing.randomspeechset) > 0

    def give_something_to_say_aloud(self, thing):
        #TODO should be like "I believe <belief>", "My goal is <goal>", etc.
        #TODO also do Facts... like for fact 'wet', say "I am wet."
        # consider making the 'wet' fact a WetFact subclass of Fact, that has a __str__ of 'wet', and has helper methods so you can pass it the thing obj possessing the fact, and it will return a string rendered in the form "I am wet."
        def format(prefix, speechset):
            newlist = []
            for t in speechset:
                if t.startswith('The'): t = 't' + t[1:]
                if t.startswith('A '): t = 'a' + t[1:]
                if t[0:2] != 'I ':
                    t = t[0].lower() + t[1:]
                t = prefix + t
                t = sentence(t)
                newlist.append(t)
            return newlist
        speechset = list(thing.randomspeechset)
        speechset.extend( thing.get_dynamic_additions_to_rndspeechset())
        speechset.extend( self.th.list_thoughts(thing))
        speechset.extend( format('I believe ',self.be.list_beliefs(thing)))
        speechset.extend( format('I have a goal to ',self.go.list_goals(thing)))
        speechset.extend( format('I remember ',self.mem.list_memories(thing)))
        speechset.extend( format('I am skilled in ',self.sk.list_skill_names_have(thing)))
        i = random.randrange(len(speechset))
        return speechset[i]

#EOF
