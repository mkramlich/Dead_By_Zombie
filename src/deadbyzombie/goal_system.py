'''
goal_system.py
by Mike Kramlich
'''

#from groglogic.mainapp.mind import HasMind
from has_mind import HasMind

class GoalSystem:
    def __init__(self):
        pass

    def add_goal(self, thing, goal):
        if isinstance(thing,HasMind):
            thing.mind.goals.append(goal)

    def has_goal(self, thing, goal):
        if isinstance(thing,HasMind):
            if goal in thing.mind.goals: return True
            else: return False
        else: return False

    def list_goals(self, thing):
        if isinstance(thing,HasMind):
            return thing.mind.goals
        else: return []

    def report_goals(self, thing, delim='\n'):
        gl = self.list_goals(thing)
        gl = map(lambda g: '"'+g+'"',gl)
        return delim.join(gl)

    def dev_report(self, thing, delim='\n', indent='  '):
        return indent + self.report_goals(thing,delim)

    def log(self, msg):
        print msg

    def debug(self, msg):
        print msg

class HasGoals:
    def __init__(self):
        self.goals = []

#EOF
