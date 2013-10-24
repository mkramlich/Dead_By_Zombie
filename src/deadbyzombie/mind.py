'''
mind.py
by Mike Kramlich
'''

from fact_system import HasFacts
from skill_system import HasSkills
from memory_system import HasMemories
from belief_system import HasBeliefs
from goal_system import HasGoals
from thought_system import HasThoughts

#TODO also have plans? conversations? social relationships? possession (sense of ownership over thing - or should that just be a fact or belief?)
#note: maybe if you "believe" you are "married" to someone, you are; I could emulate stalkers by making someone believe they're in a romantic relationship with another person, even if the target of their stalking does not believe that way!

class Mind(HasFacts,HasSkills,HasMemories,HasBeliefs,HasGoals,HasThoughts):
    def __init__(self):
        HasFacts.__init__(self)
        HasSkills.__init__(self)
        HasMemories.__init__(self)
        HasBeliefs.__init__(self)
        HasGoals.__init__(self)
        HasThoughts.__init__(self)

