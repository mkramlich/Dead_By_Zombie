'''
factsystem.py
by Mike Kramlich
created for WebHack 8/13/2007
'''

# a fact may be a string, or instance of Fact (or subclass), or instance of any arbitrary class (though in the last class it's up to the app to handle it correctly); all facts should str() into something meaningful and representitive of the fact 

# USAGE: Unlike in the rest of WebHack, when we refer to "thing" in this module we're not necessarily referring to Thing instances. Instead, we're referring to the thing which has the facts attached to it. In the case of WebHack, to be even more clear, not only can a Thing instance directly have facts, it's mind can also have facts. So when you see "thing" below it could be referring to a Thing instance or to a Thing instance's mind, etc. Or a world, a region, a level, a cell, etc. The only thing you can assume is that we assume that 'thing' implements HasFacts.

class FactSystem:
    def __init__(self):
        pass

    def add_fact(self, thing, fact):
        if isinstance(thing,HasFacts):
            if not hasattr(thing,'facts') or thing.facts is None:
                HasFacts.__init__(self)
            thing.facts.append(fact)

    def get_facts(self, thing):
        if isinstance(thing,HasFacts):
            return thing.facts
        else: return []

    def has_fact(self, thing, fact):
        if isinstance(thing,HasFacts):
            if fact in thing.facts: return True
            else: return False
        else: return False

    def report_facts(self, thing, delim='\n'):
        s = []
        if isinstance(thing,HasFacts):
            for f in thing.facts:
                if len(s) > 0:
                    s.append(delim)
                s.append(str(f))
        return ''.join(s)

    def dev_report(self, thing, delim='\n', indent='  '):
        return indent + self.report_facts(thing,delim=delim) + delim

class HasFacts:
    def __init__(self):
        if not hasattr(self,'facts'):
            self.facts = []

