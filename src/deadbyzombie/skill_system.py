'''
skill_system.py
by Mike Kramlich
a generic skills system created for WebHack
'''

import random

from has_mind import HasMind
from misc_lib import rnd_using_rpg_die_notation

class SkillSystem:
    #TODO the skill value should not be a single int value, but a tuple: (level, xp); where level is how good you are at that skill, and XP is how much actual experience/exercise/practice you've had using that skill in the world. It's possible to have high level but little to no XP, which represents born talent.
    #TODO method to exercise a skill
    #TODO method to ask what a thing's skill is with highest level and/or xp
    #TODO a data structure which holds defintion of what abilities/perks/quirks/awards/effects/rights/privlidges a thing will acquire/gain/manifest at various skill levels. For example, at "swim 1" you get the "float" ability. At "skill 5" you gain the "breaststroke" ability. Abilities often correlate to user commands that become available for use by that player/thing, but, not always.
    #TODO the app can register a callback fn to be called whenever:
    #       a skill is exercised
    #       a skill increases in level
    #       a new ability/perk/whatever is unlocked due to a skill reaching a certain new level
    #TODO webhack should register callbacks for everything it what to know about, and in the method modies of those callbacks it should emit an event indicating what happened; I can then register listeners/triggers as needed.
    #TODO the player should be informed in feedback whenever he has a skill level increase, or new ability unlocked.
    #TODO un-exercised skills may slowly decay in level/xp over time, the longer they go un-exercised. The SS tracks this by recording the last time/tock that each skill was exercised. It gets the current time/tock value from the app, via a plugin that the app registers with it, that SS can call to get the current time value to use in it's record keeping.
    #TODO a reward may require 2+ skill+level combo's, not just one
    #TODO a method that takes a thing and turns a list of skillbundle names that that thing has skills equivalent to; in otherwords, even if a thing didn't start life with say the 'soldier' bundle, perhaps he's attained skill levels now such that he effectively has the 'soldier' bundle (or even exceeds it!)
    #TODO a method that takes a thing and returns a list of all rewards he's unlocked, based on his current skills/levels
    #TODO a method that returns report of all skills it's ever seen (through use of this SS instance by an application)
    #TODO the skillbundle system should have an xp portion too, and allow rnd ranges too, just like skill level already does; so a skillbundle can specify xp values (or ranges) to start with, for a particular skill
    #TODO talent: in next_xp_to_level (and elsewhere) subtract thing's base-talent-level from given level, before calculating xp to return; in other words, if given level 5, but his base-talent-level is 4, it means he's effectively level 1 in terms of how much XP he'll have to earn to reach the next level; in other words, if you have natural talent, you sorta learn that skill quicker, and can reach higher levels, more easily, than a less talented person, in that particular skill; this base-talent-level notion is always per-skill, not global across all skills
    #TODO method to get a thing's total overall level for a skill (level due to talent + level due to xp earned)
    #TODO app can specify (by configuring the SS instance) if there are level caps for a particular skill, or across all skills (a global level cap, like 100, for example)
    #TODO config option: SS can keep track of when was the last time/tock each skill was exercised (it gets the current time/tock from the app plugin); it then uses this information to 'decay' skill levels and/or xp, if/when app requests it to do so; this is the idea that unused skills will worsen or be lost; "Use it or lose it."
    #TODO some skills are secret; meaning, a thing has that skill (with some level, talent and/or xp in it) but he does not KNOW he has it; thus, if user issues a command to list his skills, that skill will not be listed; the API has methods both to list all skills (including secret ones) or to list only those skills that are not secret (to their owner anyway); this is useful for the situation where a skill represents knowledge gained of some subject that you don't quite yet know you're learning it, like, uh, cant think of example now but trust me it's probabl useful. yeah. right.

    # USAGE NOTES:
    # value entries in the skillbundle per-skill can be int, or, a string containing '1d3+1' notation or '2-4' notation
    # a reward can be anything, it's defined and interpreted by the app
    # a reward may be a number, string or object reference
    # examples of reward strings would include "ninja" or "marksman" (and those may or may not also be names of skillbundles, it's up to the app)
    # examples of reward object refs would include an object instance of a "Sword +2 of Giant Stabbing" (to clarify example: this would be a game in-world entity class instance, not a string)

    def __init__(self):
        self.skillbundles = None
        self.rewards = None
        self.level_up_listeners = []
        self.reward_unlocked_listeners = []
        self.plugin = None
        #TODO rewards is two-dim map of skill+level to a reward
        # a reward is app-defined; it could be a string, a number, a tuple, whatever, it only has meaning to the application, not to SkillSystem

    def set_skill_level(self, thing, skill, level):
        if not isinstance(thing,HasMind): return
        mind = thing.mind
        if not hasattr(mind,'skills'):
            mind.skills = {}
        newvalue = None
        if skill in mind.skills:
            (oldlevel, xp) = mind.skills[skill]
            newvalue = (level, xp)
        else:
            newvalue = (level, 0)
        mind.skills[skill] = newvalue

    def set_skill_xp(self, thing, skill, xp):
        if not isinstance(thing,HasMind): return
        mind = thing.mind
        if not hasattr(mind,'skills'):
            mind.skills = {}
        newvalue = None
        if skill in mind.skills:
            (level, oldxp) = mind.skills[skill]
            newvalue = (level, xp)
        else:
            newvalue = (0, xp)
        mind.skills[skill] = newvalue

    def set_skill(self, thing, skill, tuple_level_xp):
        if not isinstance(thing,HasMind): return
        mind = thing.mind
        if not hasattr(mind,'skills'):
            mind.skills = {}
        mind.skills[skill] = tuple_level_xp

    def define_skillbundle_skill(self, bundlename, skill, value):
        #TODO write fn to use that kind of notation ('3-8') to generate a rnd number with that range
        if not hasattr(self,'skillbundles'):
            self.skillbundles = None
        if self.skillbundles == None:
            self.skillbundles = {}
        sbs = self.skillbundles
        if bundlename not in sbs:
            sbs[bundlename] = {}
        sbs[bundlename][skill] = value

    def define_reward(self, skill, level, reward):
        # reward is assumed to be a tuple of individual rewards
        if self.rewards == None:
            self.rewards = {}
        if skill not in self.rewards:
            self.rewards[skill] = {}
        if not isinstance(reward,type( () )):
            reward = (reward,)
        self.rewards[skill][level] = reward

    def return_rewards():
        return self.rewards

    def generate_skills(self, bundlename):
        skillbundle = self.skillbundles[bundlename]
        skills = {}
        for skill in skillbundle:
            skdef = skillbundle[skill]
            val = None
            if isinstance(skdef,type(1)): # int
                val = skdef
            elif isinstance(skdef,type('')):
                skdef = skdef.lstrip().rstrip().lower()
                if skdef.count('d') > 0:
                    val = rnd_using_rpg_die_notation(skdef)
                elif skdef.count('-') > 0:
                    #TODO extract into gen fn in lib.py:
                    min,max = skdef.split('-')
                    min = int(min)
                    max = int(max)
                    maxrel = max - min
                    val = min + random.randrange(maxrel+1)
                else: val = int(skdef)
            level = val
            xp = 0
            skills[skill] = (level, xp)
        return skills

    def report_on_skills(self, thing, delim='\n'):
        if not isinstance(thing,HasMind): return ''
        #TODO optional param to indicate how to sort: alpha by skill name, or, by level descending
        s = ''
        mind = thing.mind
        skillnames = mind.skills.keys()
        skillnames = sorted(skillnames)
        for i,skill in enumerate(skillnames):
            s += skill + ' ' + str(mind.skills[skill]) + delim
        return s

    def list_skill_names_have(self, thing):
        return list(thing.mind.skills.keys())

    def dev_report(self, thing, delim='\n', indent='  '):
        return indent + self.report_on_skills(thing,delim=delim)

    def add_skills_from_bundle(self, thing, bundlename):
        if not isinstance(thing,HasMind): return
        mind = thing.mind
        skills = self.generate_skills(bundlename)
        if not hasattr(mind,'skills'):
            mind.skills = {}
        #TODO instead of overwriting existing skill values blindly, only alter the orig value if it would increase the skill's level and/or the skill's accumulated XP
        mind.skills.update(skills)

    def describe(self, thing):
        if self.plugin != None:
            return self.plugin.describe(thing)
        else: return str(thing)

    def debug(self, msg):
        if self.plugin != None:
            self.plugin.debug(msg)
        else: self.log(msg)

    def log(self, msg):
        if self.plugin != None:
            self.plugin.log(msg)
        else: print msg

    def exercise_skill(self, thing, skill, howmuch, reason=None):
        if not isinstance(thing,HasMind): return
        mind = thing.mind
        if howmuch == 0: return
        if not hasattr(mind,'skills'):
            mind.skills = {}
        level = 0
        xp = 0
        if skill in mind.skills:
            try:
                (level, xp) = mind.skills[skill]
            except: print '\n-->  "' + str(mind.skills[skill])+'"'
        else:
            (level, xp) = (0,0)
        xp += howmuch
        mind.skills[skill] = (level, xp)
        s = self.describe(thing) + ' gained ' + str(howmuch) + ' XP for ' + skill + ' skill'
        if reason != None:
            s += ' due to '+str(reason)
        self.log(s)
        self.notify_listeners_of_gained_xp(thing,skill,howmuch,reason)
        while xp >= self.next_xp_to_level(level):
            level += 1
            mind.skills[skill] = (level, xp)
            self.notify_listeners_of_level_up(thing,skill,level)
            if self.does_level_unlock_rewards(skill,level):
                rewards = self.what_rewards_unlocked_at_level(skill,level)
                for reward in rewards:
                    self.notify_listeners_of_reward_unlocked(thing,reward)

    def notify_listeners_of_gained_xp(self, thing, skill, howmuch, reason=None):
        if self.plugin != None:
            self.plugin.gained_xp(thing,skill,howmuch,reason)

    def next_xp_to_level(self, level):
        #TODO refactor to use better, more scalable system like equation
        if level == 0: return 1
        if level == 1: return 10
        if level == 2: return 100
        if level == 3: return 1000
        if level == 4: return 10000
        return 100000

    def what_rewards_unlocked_at_level(self, skill, level):
        reward = self.rewards[skill][level]
        if not instance(reward,type( () )):
            return (reward,)
        else: return reward

    def notify_listeners_of_level_up(self, thing, skill, level):
        if self.plugin != None:
            self.plugin.level_up(thing,skill,level)

        for lis in self.level_up_listeners:
            lis.level_up(thing,skill,level)

    def notify_listeners_of_reward_unlocked(self, thing, reward):
        if self.plugin != None:
            self.plugin.reward_unlocked(thing,reward)

        for lis in self.reward_unlocked_listeners:
            lis.reward_unlocked(thing,reward)

    def does_level_unlock_rewards(self, skill, level):
        return False

    def dump_skills(self, thing):
        skills = self.report_on_skills(thing)
        self.log(self.describe(thing) + ' has skills: ' + str(skills))

    def get_skillbundle(self, bundlename):
        if bundlename in self.skillbundles:
            return self.skillbundles[bundlename]
        else: return None

class HasSkills:
    def __init__(self):
        if not hasattr(self,'skills'):
            self.skills = {}

class SkillSystemPlugin:
    # USAGE NOTES: The application should instantiate and register with SkillSytem an instance of an app-specific subclass of this class. In their subclass, they provide method implementations appropriate for their application.
    def __init__(self):
        pass

    def gained_xp(self, thing, skill, howmuch, reason=None):
        pass

    def level_up(self, thing, skill, level):
        pass

    def reward_unlocked(self, thing, reward):
        pass

    def describe(self, thing):
        pass

    def log(self, msg):
        pass

    def debug(self, msg):
        pass

#EOF

