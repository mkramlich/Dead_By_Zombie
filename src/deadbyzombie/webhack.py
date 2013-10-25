'''
webhack.py

WebHack: A Python Framework for Rogue-like Games
by Mike Kramlich

ps. the name is a play on NetHack (net -> web... get it?)
'''

import copy
import datetime
import gc
import logging
import os
import pickle
import pprint
import random
import sys
import textwrap

from misc_lib import dist, chance, Groups, read_file_lines, StopWatch,\
    getattr_withlazyinit, sentence, sentence_capitalize,\
    encode_whitespace_inside_quotes, awordify, rnd_in_range, TextPools,\
    assertNotNone, stradd, isinstance_any, randrangewith, gender2heshe,\
    gender2himher, gender2hishers, app, assertNotDirectInstantiate,\
    secs_float_diff_to_summary_str, table, and_many, isclass, in_range,\
    get_object, cycle_increment, get_next_with_cycle, fontcolorize, get_doc,\
    bare_class_name, split_width #TODO alpha sort these
from misc_lib import HtmlColors as LibHtmlColors
import filecache
from rectarea import RectArea


def path_for_file_in_data(filename):
    return envcfg('DBZ') + '/data/' + filename

def read_data_file(filename, linedelim='\n', lineprefix=None):
    lines = filecache.read_file_as_lines(path_for_file_in_data(filename))
    lines2 = []
    for ln in lines:
        lines2.append(ln.rstrip('\n'))
    lines = lines2

    if lineprefix is not None:
        linedelim = linedelim + lineprefix
    s = linedelim.join(lines)
    if lineprefix is not None and len(lines) > 0:
        s = lineprefix + s
    return s

def envcfg(key):
    d = {}
    d['WHLOGDIR'] = 'logs/'
    d['WHLOGFILE'] = 'log'
    d['SITELOGFORMAT'] = '%(asctime)s|%(levelname)8s| %(message)s'
    d['WHLOGFORMAT'] = d['SITELOGFORMAT']
    d['WHLOGFILEMODE'] = 'a'
    d['WHLOGLEVEL'] = 'DEBUG'
    if key in d:
        return d[key]
    else:
        return os.environ[key]

def makehtmlsafe(txt): return txt


# WebHack Game Subsystems
from ai_system import AiSystem
from belief_system import BeliefSystem, HasBeliefs
from event_system import EventSystem, Event, TickEvent
from fact_system import FactSystem, HasFacts
from geo_system import GeoSystem, GeoSystemPlugin, Location, HasLocation, FuzzyLocation, Level, Zone, Water, StringLevelRenderer
from goal_system import GoalSystem
from has_mind import HasMind
from id_system import IdSystem, HasID
from language_helper import LanguageHelper
from memory_system import MemorySystem, MemorySystemPlugin
from mind import Mind
from skill_system import SkillSystem, SkillSystemPlugin 
from thought_system import ThoughtSystem, ThoughtSystemPlugin

# Logging
logdir = envcfg('WHLOGDIR')
fnameparams = {'pid' : os.getpid()}
logfilename = envcfg('WHLOGFILE') % fnameparams
logfilepath = '%s%s' % (logdir, logfilename)
logformat = envcfg('WHLOGFORMAT')
logger = logging.Logger('webhack.py')
handler = logging.FileHandler(logfilepath,mode=envcfg('WHLOGFILEMODE'))
fmt = logging.Formatter(fmt=logformat)
handler.setFormatter(fmt)
#TODO maybe first removeHandler any pre-existing one(s):
logger.addHandler(handler)
loglevel = getattr(logging,envcfg('WHLOGLEVEL'))
logger.setLevel(loglevel)

def trace(msg):
    pass
    #if debugvar:
    #    logger.debug(msg)

def debug(msg, *args, **kwargs):
    #pass
    logger.debug(msg,*args,**kwargs)

def log(msg, *args, **kwargs):
    pass
    #logger.info(msg,*args,**kwargs)

def error(msg):
    pass
    #logger.error(msg)

DBZ = '.' #TODO hack!
DATADIR = DBZ + '/data/webhack/'

# Constants
#TODO refactor to: class MetaKey: AUTOUI = 'autoui'; DEVONLY = 'devonly', etc.
AUTOUI_METAKEY = 'autoui'
DEVONLY_METAKEY = 'devonly'
DIRECTIONAL_METAKEY = 'directional'
MOVECMD_METAKEY = 'movecmd'
INVENTORYTHINGUSERCMD_METAKEY = 'inventorythingusercmd'

USERCMD_PREFIX = 'usercmd_'

SUBMIT_STYLE_PARAMS_PREFIX = 'params|'

YES = True

TICKS_PER_DAY_DEFAULT = 48

def extract_info_from_filename(filename): # TODO delete me; vestigial from the orig web app version
    #filename pattern: 'gamestate-g%s-u%s-t%s-%s-%s.dat' % (gameid, userid, tock, date, time)
    pieces = filename.split('-')
    gameid = int( pieces[1][1:] )
    userid = int( pieces[2][1:] )
    tock   = int( pieces[3][1:] )
    date   =      pieces[4] # NOTE just a string
    time   =      pieces[5].split('.')[0] # NOTE just a string
    return gameid, userid, tock, date, time


class HtmlColors(LibHtmlColors):
    FG         = LibHtmlColors.BLACK
    BG         = LibHtmlColors.WHITE
    YOU        = LibHtmlColors.BLUE
    FRIEND     = '#00BB00'
    DEVONLY    = LibHtmlColors.BLUE
    USDOLLAR   = LibHtmlColors.DARKGREEN
    MONEY      = USDOLLAR
    GOLDCOIN   = LibHtmlColors.DARKYELLOW

class Colors(LibHtmlColors):
    BLACK = LibHtmlColors.WHITE
    WHITE = LibHtmlColors.BLACK
    FG = WHITE
    BG = BLACK

# Thoughts
THINK_SHOULD_FOLLOW_YOU = 'I should follow You.'
THINK_SHOULD_NOT_MOVE = 'I should not move.'

class Skills: # enumeration, not really a class
    HAND_TO_HAND = 'hand-to-hand'

# Infrastructure Data
thing_classes = set()
thing_class_groups = {}
master_layoutmap = {}

# Global Variables
debugvar = False
force_reset = False

EOL = '<br/>\n'

###################
# WebHack - begin #
###################

##################################
# Website View Functions - begin #
##################################

class Plot:
    def __init__(self, wh):
        self.wh = wh

    def report_status(self):
        pass

class CureZombiePlot(Plot):
    def __init__(self, wh):
        Plot.__init__(self,wh)
        self.steps = {}
        # more step ideas:
        #   id. the mechanism of infection
        #   inhibit, clone
        self.steps[1] = ('identify the active agent',        False)
        self.steps[2] = ('isolate the gene',                 False)
        self.steps[3] = ('index the nucleotides',            False)
        self.steps[4] = ('map the phenome',                  False)
        self.steps[4] = ('trigger a reaction disabler',      False)
        self.steps[5] = ('design the manufacturing process', False)
        self.steps[6] = ('setup the manufacturing facility', False)
        self.steps[7] = ('arrange a distribution method',    False)

    def common_event_handle_tasks(self, event, step):
        txt, oldstatus = self.steps[step]
        newstatus = True
        self.steps[step] = (txt, newstatus)
        s = '%s handler: changed step %s status from %s to %s' % (event.__class__,step,oldstatus,newstatus)
        self.wh.feedback(s)

    def handle_IdentifyActiveAgentEvent(self, event):
        self.common_event_handle_tasks(event,1)

    def handle_IsolateTheGeneEvent(self, event):
        self.common_event_handle_tasks(event,2)

    def handle_MapTheThingEvent(self, event):
        self.common_event_handle_tasks(event,3)

    def handle_IndexTheThingEvent(self, event):
        self.common_event_handle_tasks(event,4)

    def handle_DesignManufactureProcessEvent(self, event):
        self.common_event_handle_tasks(event,5)

    def handle_SetupFactoryEvent(self, event):
        self.common_event_handle_tasks(event,6)

    def handle_ArrangeDistroMethodEvent(self, event):
        self.common_event_handle_tasks(event,7)

    def report_status(self):
        s = 'Zombie Cure Development\n'
        for i in self.steps:
            txt, status = self.steps[i]
            done = status and 'YES' or 'NO'
            row = (txt, done)
            s += ' \n    %s\n        done: %s\n' % (txt.capitalize(), done)
        return s

class GameMode:
    def __init__(self, wh):
        #TODO: the hasattr() guard clause below is to prevent the guts of this method from executing twice for an object. This is needed because subclass initialization is currently causing GameMode.init to be called twice. It feels non-ideal but this little hack will compensate.
        if not hasattr(self,'wh'):
            self.wh = wh

    def __str__(self):
        return 'GameMode class %s name %s' % (self.__class__.__name__,self.mode_name())

    #TODO other stuff I may disallow in demo mode: building things; picking locks
    #TODO: disallowed_user_commands(); returns tuple of usercmd name strings; example: in demo mode, "save" is not allowed, and possibly other usercmd's as well
    def mode_name(self): pass
    def is_demo_mode(self): pass
    def is_full_mode(self): pass
    def init_game(self): pass
    #NOTE: the rate values are measured per-user, for a particular user
    #TODO: world size, extends
    def is_tock_limit(self): pass
    def get_tock_limit(self): pass
    def save_allowed(self): pass
    def may_watch_time_pass_after_death(self): pass
    def is_restart_limit(self): pass #TODO max num of restarts allowed per user/visitor
    def get_restart_limit(self): pass #TODO
    def restart_throttle_rate(self): pass #TODO
    def request_throttle_rate(self): pass #TODO
    def again_command_allowed(self): pass
    def console_input_allowed(self): pass
    #TODO: victory conditons
    def advertising_enabled(self): pass #TODO
    def scoreboard_recording(self): pass #TODO
    #TODO: in-game gameplay perks, differences, bonuses, content
    def ui_change_allowed(self): pass
    def use_homebrew_content(self): pass #TODO
    def submit_homebrew_content(self): pass #TODO
    def bg_sound_allowed(self): pass 
    def subscription_required(self): pass #TODO

class DemoGameMode(GameMode):
    init_state_file_indicator = 'demo'

    def mode_name(self): return 'Demo'
    def is_demo_mode(self): return True
    def is_full_mode(self): return False
    def is_tock_limit(self): return True
    def get_tock_limit(self): return 500
    def save_allowed(self): return False
    def may_watch_time_pass_after_death(self): return False
    def is_restart_limit(self): return True
    def get_restart_limit(self): return 10
    def restart_throttle_rate(self): return 60 # no more than once per 60 min
    def request_throttle_rate(self): return 30 # no more than 30 requests per minute
    def again_command_allowed(self): return False
    def console_input_allowed(self): return False
    def advertising_enabled(self): return True
    def scoreboard_recording(self): return False
    def ui_change_allowed(self): return False
    def use_homebrew_content(self): return False
    def submit_homebrew_content(self): return False
    def bg_sound_allowed(self): return False 
    def subscription_required(self): return False

class FullGameMode(GameMode):
    init_state_file_indicator = 'full'

    def mode_name(self): return 'Full'
    def is_demo_mode(self): return False
    def is_full_mode(self): return True
    def is_tock_limit(self): return False
    def get_tock_limit(self): return None #TODO raise ex?
    def save_allowed(self): return True
    def may_watch_time_pass_after_death(self): return True
    def is_restart_limit(self): return False
    def get_restart_limit(self): return None #TODO raise ex?
    def restart_throttle_rate(self): return 10 # no more than once per 10 min
    def request_throttle_rate(self): return 120 # no more than 120 requests per minute
    def again_command_allowed(self): return True
    def console_input_allowed(self): return True
    def advertising_enabled(self): return False
    def scoreboard_recording(self): return True
    def ui_change_allowed(self): return True
    def use_homebrew_content(self): return True
    def submit_homebrew_content(self): return True
    def bg_sound_allowed(self): return True 
    def subscription_required(self): return True

class ZombieHackDemoGameMode(DemoGameMode):
    def __init__(self, wh):
        DemoGameMode.__init__(self,wh)

    def init_game(self): # ZombieHack
        self.init_game_first_part()
        self.init_game_last_part()

    def init_game_first_part(self):
        wh = self.wh
        cfg = wh.cfg
        log = wh.log

        wh.changed_since_last_render = True
        watch = StopWatch('%s.init_game_first_part(): ' % self.__class__.__name__)
        wh.gamedatasubdir = 'zombiehack/'
        wh.reset_config()
        wh.init_idsys()
        wh.init_misc()
        wh.init_gameend_flags()
        wh.init_eventsystem()
        wh.init_textpools()
        wh.init_ai()
        wh.init_feedback()

        # convenience aliases:
        ai = wh.ai
        th = ai.th

        # convenience fn's:
        def loc(r, c):
            return stdloc.clone(r=r,c=c)

        def floc(r=None, c=None, br=None, bc=None, w=None, h=None):
            return stdfloc.clone(r,c,br,bc,w,h)

        # Geography & Things section BEGIN 

        w = 30
        h = 10
        wh.init_geo(w,h)
        geo = wh.geo
        wh.layoutmap['Z'] = zh_Zombie
        #wh.layoutmap['B'] = Barricade
        region = geo.initial_region
        region.name = 'Dayton, Ohio'

        # convenience aliases:
        pm = geo.put_on_map
        pm2 = geo.put_on_map2
        maketerr = geo.make_terrainclass_at
        fillterr = geo.make_terrainclass_fill

        # Create the Levels
        level1 = geo.initial_level
        level1.name = 'Underground Level'
        level1.environment = Level.INSIDE
        level2, lk2 = geo.make_new_level_above('Street Level', level1)
        level2.environment = Level.OUTSIDE
        wh.init_sandbox_level(region)


        # Populate the Levels

        # Level 1 - The Underground

        stdloc = Location(0,0,level1,region)
        stdfloc = FuzzyLocation(r=None,c=None,br=None,bc=None,w=None,h=None,level=level1,region=region)

        # convenience fn's:
        def loc(r, c):
            return stdloc.clone(r=r,c=c)

        def floc(r=None, c=None, br=None, bc=None, w=None, h=None):
            return stdfloc.clone(r,c,br,bc,w,h)

        # Sewer's Outer Boundary Walls
        boundarylayout = wh.gen_thing_rectangle_layout(Wall, w, h)
        wh.place_using_layout(Location(0,0,level1,region), boundarylayout)

        #TODO have interior walls & water in patterns looking like a sewer
        # there are tons of zombies down there:
        sewerzoms = pm2(zh_Zombie, fuzloc=floc(br=0,bc=0), minqty=10, maxqty=10)

        # Stairway on (and leading between) Level 1 and 2
        stairs_loc = Location(8,14,level1,region)
        dest_loc =   stairs_loc.clone(level=level2)
        wh.stair_pair(stairs_loc, dest_loc)

        # Level 2 - Street Level (where You start)

        stdloc = Location(0,0,level2,region)
        stdfloc = FuzzyLocation(r=None,c=None,br=None,bc=None,w=None,h=None,level=level2,region=region)

        # convenience fn's:
        def loc(r, c):
            return stdloc.clone(r=r,c=c)

        def floc(r=None, c=None, br=None, bc=None, w=None, h=None):
            return stdfloc.clone(r,c,br,bc,w,h)

        # Lake Dayton
        lake = Zone(stdloc.level, w-3, 0, 3, 3, name='Lake Dayton')
        geo.add_zone(stdloc.level, lake)
        fillterr(Water, loc(lake.area.by,lake.area.bx), lake.area.w, lake.area.h)

        # Houses:
        #TODO multiple; terrain inside house is diff terrain than normal ground
        #TODO have 'wood floor' terrain inside house, light brown '.'
        #TODO have some grass (terrain, green "." (period))
        #TODO have some dirt (terrain, dark brown ".")
        #TODO pavement terrain (black ".")

        # Your House
        wh.building_random(loc(1,1),      5, 5, door_qty_range=(1,1), rnd_stuff={'min_qty':2, 'max_qty':6}, name='your house')
        pm(Chainsaw(wh), loc(2, 2))
        pm(FirstAidKit(wh), loc(3, 2))
        pm(USDollar(wh,amount=20), loc(3,3))
        pm(Milk(wh), loc(4, 4))
        pm(Bread(wh),  loc(4, 4))
        pm(Cheese(wh), loc(4, 4))
        pm(Cheese(wh), loc(4, 4))
        pm(Fruit(wh), loc(4, 4))
        pm(Fruit(wh), loc(4, 4))
        pm(Cookie(wh), loc(4, 4))

        wh.building_random(loc(1,9),      8, 3, door_qty_range=(1,2), rnd_stuff={'min_qty':3, 'max_qty':8}, name="somebody's house")

        # Costume Shop, Barricaded Up w/Zombie Costume Inside
        wh.building_random(loc(h-3-1,7),  5, 3, door_qty_range=(0,0), barricade_qty_range=(1,1), rnd_stuff=None, name="Crazy Bob's Costume Shop")
        pm(ZombieCostume(wh), loc(h-3, 9))

        wh.building_random(loc(h-5-1,20), 9, 5, door_qty_range=(2,2), rnd_stuff={'min_qty':6, 'max_qty':12}, name='store')


        # Teleporter in top-right corner of map
        #tporter_loc = loc(0, w-1)
        #tp_dest_loc = loc(h-3, 0)
        #tporter = Teleporter(wh, tporter_loc, tp_dest_loc)
        #tporter.devmode_only_tp = True
        #tporter.devmode_only_vis = True
        #pm(tporter, tporter_loc)

        # invuln zombie (during dev only)
        z = zh_Zombie(wh)
        if cfg('devmode'):
            z.invuln = True
        pm(z, loc(h-1, 4))

        # ensures there is at least 1 female human
        hum = Human(wh,gender='female')
        pm(hum, loc(h-1, 12))

        # DEVTEST: Barricade to your west
        #barr_layout = wh.gen_thing_rectangle_layout(Barricade, 3, 3)
        #wh.place_using_layout(Location(1,19,stdloc.level,stdloc.region), barr_layout)

        wh.you = You(wh)
        you = wh.you
        goal = you.goals.append
        goal(("Don't become a zombie.",'is_goal_satisfied_you_not_zombie',True))
        goal(('Destroy all zombies.','is_goal_satisfied_destroy_all_zombies',False))
        goal(('Escape to a place of permanent personal safety from zombies.','is_goal_satisfied_escape_to_personal_perm_safety',True))
        goal(('Ensure at least one non-zombie human breeding pair survives, to help save humanity from extinction.','is_goal_satisfied_keep_others_alive',True))
        goal(('Develop a cure.','is_goal_satisfied_develop_a_cure',False))
        mem = ai.mem.remember
        mem(you,'My house is on the north-west side of this area.','for a while now')
        mem(you,'I woke up on the wrong side of the bed','this morning')
        mem(you,"I heard a strange blood-curdling scream coming from the street in front of my house, but didn't go outside to investigate further",'this afternoon')
        mem(you,'I saw the tail end of a TV news report today talking about a mysterious rise in emergency hospital admissions','an hour ago')
        mem(you,"There's food in your house",'last time you were there')
        mem(you,"There's a first-aid kit in your house",'last time you were there')
        mem(you,"There's a chainsaw in your house",'last time you were there')
        you.myenemyclasses.extend([zh_Zombie,WarriorDoll])
        #wielded = (BaseballBat(wh),)
        #you.carry_and_wield(wielded,feedback=False)
        worn = (
            Coat(wh),
            LeatherJacket(wh),
            Shirt(wh),
            Belt(wh),
            Jeans(wh),
            #Underwear(wh),
            Socks(wh),
            Shoes(wh),
            #ZombieCostume(wh),
            )
        you.carry_and_wear(worn,feedback=False)
        note = Note(wh,bodytext='TODO: buy more cheese')
        flyer = Flyer(wh,bodytext='Zion Research: call for volunteers for exciting experiments on the frontiers of biological science')
        letter_txt = "March 17, 19--.\nDear ---,\n  We are writing to you in response to your inquiry as to the result of last year's voyage, the one you read about in all the papers. The one with the strange circumstances. The official story was that our ship ran aground in a terrible storm, and that explained our disappearance from the charts and the loss of crew. But that was not the truth. Not the whole truth anyway.\nOur expedition had discovered an uncharted island and landed upon it. A week later, we fled back to the ship and sailed away with the survivors. Most of the crew had been murdered in horrible ways by an unseen demon on that cursed island. We pray that noone else ever sets foot there. What we encountered must never reach civilization."
        letter = Letter(wh,bodytext=letter_txt)
        carried = (note, flyer, letter, Book(wh), Bread(wh), Cheese(wh), Knife(wh))
        you.carry(carried)
        more_food = []
        for i in range(3):
            more_food.append(CandyBar(wh))
        you.carry(more_food)
        youloc = loc(1, w-5)
        pm(you, youloc)
        wh.ev.add_listener((ThingEntersCellEvent,{'thing':you}),wh,'make_you_level_active_and_focus_ui')
        geo.add_to_cell_desc('This is where you started.',youloc.level,youloc.r,youloc.c)
        geo.activelevel = youloc.level

        pm(Dog(wh), youloc.clone(r='-1', c='-1'))
        pm(Fruit(wh), youloc.clone(c='-1'))
        pm(FruitTree(wh), youloc.clone(r='+1'))

        flyer2 = Flyer(wh,bodytext='The League of Mad Scientists For a Better Tomorrow - next meeting to be held at the mansion of V. Venturius')
        pm(flyer2, youloc.clone(r='+1', c='-2'))

        pm(Flare(wh,lit=True), youloc.clone(r=3,c=19))


        # a zombie! (ensures there is at least one at game start)
        z = zh_Zombie(wh)
        z.always_hits = True
        pm(z, loc(7,3))

        # a corpse! (ensures at least one, and suggests danger and unusualness)
        pm(HumanCorpse(wh), loc(7,4))

        # Human NPC's
        humsmade = pm2(American, fuzloc=floc(br=0,bc=0), minqty=10, maxqty=10)
        humspeechset = wh.get_data_lines('zombiehack/Human_speech')
        for hum in humsmade:
            hum.myenemyclasses.append(zh_Zombie)
            hum.add_to_rnd_speech(humspeechset)

        # Fruit Tree Grove
        pm2(FruitTree, fuzloc=floc(br=h-3,bc=0,w=4,h=3), minqty=7, maxqty=9)

        # Geography & Things section END 
        wh.introblurb = read_data_file('webhack/zombiehack/introblurb')
        wh.introadvice = read_data_file('webhack/zombiehack/introadvice')


        log(watch.stop())

    def init_game_last_part(self):
        watch = StopWatch('%s.init_game_last_part(): ' % self.__class__.__name__)
        wh = self.wh
        wh.update_seen_cells()
        wh.feedback(wh.introblurb)
        wh.feedback(wh.introadvice)
        wh.usercmd_look_here()
        wh.init_ui()
        log(watch.stop())

class ZombieHackFullGameMode(FullGameMode, ZombieHackDemoGameMode):
    init_state_file_indicator = FullGameMode.init_state_file_indicator

    def __init__(self, wh):
        FullGameMode.__init__(self,wh)
        ZombieHackDemoGameMode.__init__(self,wh)

    def is_demo_mode(self): return False
    def is_full_mode(self): return True

    def init_game(self):
        ZombieHackDemoGameMode.init_game_first_part(self)

        wh = self.wh
        you = wh.you
        log = wh.log
        cfg = wh.cfg
        ai = wh.ai
        th = ai.th
        geo = wh.geo
        pm = geo.put_on_map
        start_level = you.loc.level
        geo.activelevel = start_level

        self.make_Eastside()
        self.make_Library()
        self.make_Prison()
        self.make_PoliceStation()
        self.make_University()
        self.make_Cemetary()
        self.make_Bank()
        self.make_Church()
        self.make_SuperStore()
        self.make_MegaMall()
        zion = self.make_ZionResearch()
        self.make_Hospital()
        zoo_level       = self.make_Zoo()
        venturius_level = self.make_VenturiusEstate()
        hexenhammer = self.make_HexenhammerCastle()
        wendigo_level   = self.make_WendigoForest()
        milbase_level   = self.make_MilitaryBase()

        wh.route_pair(wendigo_level,milbase_level,edge_pref1='top',edge_pref2='bottom')
        wh.route_pair(zoo_level,venturius_level,edge_pref1='right',edge_pref2='left')
        wh.route_pair(zion,hexenhammer,edge_pref1='right',edge_pref2='left')

        # Make More Regions - Randomly
        rnd_regs = wh.make_rnd_regions(0) # <-- may raise StairwayPlacementFail
        lr,lc = 1,18
        ar,ac = 2,18
        for rr in rnd_regs:
            reg, rk, baselev, baselk = rr
            #wh.make_teleporter_pair_between_two_levels(start_level, baselev, (lr,lc), (ar,ac))
            wh.route_pair(start_level, baselev) # NOTE: may raise RoutePlacementFail
            lc += 1
            ac += 1

        ZombieHackDemoGameMode.init_game_last_part(self)

    def region_setup(self, regname, w, h, lev_name='Street Level', route_from_start=True, edge_pref1=None, edge_pref2=None):
        print 'region_setup: %s %ix%i' % (regname, w, h)
        wh = self.wh
        log = wh.log
        cfg = wh.cfg
        ai = wh.ai
        th = ai.th
        geo = wh.geo
        world = geo.world
        you = wh.you
        start_level = you.loc.level
        pm = geo.put_on_map
        pm2 = geo.put_on_map2

        reg, rk = geo.new_region(regname,w=w,h=h)
        lev, lk = geo.new_level(lev_name, reg, levelkey=0)
        if route_from_start:
            wh.route_pair(start_level, lev, edge_pref1=edge_pref1, edge_pref2=edge_pref2) # NOTE: may raise RoutePlacementFail
        stdloc = Location(0,0,lev,reg)
        stdfloc = FuzzyLocation(r=None,c=None,br=None,bc=None,w=None,h=None,level=lev,region=reg)
        loc = stdloc.clone
        floc = stdfloc.clone

        return regname, w, h, reg, lev, stdloc, stdfloc, loc, floc, pm, pm2, wh

    def make_Eastside(self):
        log('make Eastside')
        regname, w, h, reg, lev, stdloc, stdfloc, loc, floc, pm, pm2, wh =\
            self.region_setup('Eastside',30,20)
        fl = floc(br=6,bc=8,w=12,h=8)
        wh.building_random(loc(fl.br,fl.bc), fl.w, fl.h, door_qty_range=(1,2), rnd_stuff={'min_qty':3, 'max_qty':8}, name="The Jameson's")
        humsmade = pm2(American, fuzloc=fl, minqty=10, maxqty=10)
        humspeechset = wh.get_data_lines('zombiehack/Human_speech')
        for hum in humsmade:
            hum.myenemyclasses.append(zh_Zombie)
            hum.add_to_rnd_speech(humspeechset)
        buildings = lev.get_zones_of_class(Building)
        zombies = pm2(zh_Zombie, fuzloc=floc(br=0,bc=0), minqty=5, maxqty=10, zones_disallowed=buildings)
        pm(WarriorDoll(wh), loc(7,9))

    def make_Library(self):
        log('make Library')
        regname, w, h, reg, lev, stdloc, stdfloc, loc, floc, pm, pm2, wh =\
            self.region_setup('Library',30,20)
        fl = floc(br=6,bc=8,w=12,h=8)
        wh.building_random(loc(fl.br,fl.bc), fl.w, fl.h, door_qty_range=(1,2), rnd_stuff={'min_qty':20, 'max_qty':30, 'group_name':'library_material'}, name="Library")
        humsmade = pm2(American, fuzloc=fl, minqty=10, maxqty=10)
        humspeechset = wh.get_data_lines('zombiehack/Human_speech')
        for hum in humsmade:
            hum.myenemyclasses.append(zh_Zombie)
            hum.add_to_rnd_speech(humspeechset)
        buildings = lev.get_zones_of_class(Building)
        zombies = pm2(zh_Zombie, fuzloc=floc(br=0,bc=0), minqty=5, maxqty=10, zones_disallowed=buildings)

    def make_Prison(self):
        log('make Prison')
        regname, w, h, reg, lev, stdloc, stdfloc, loc, floc, pm, pm2, wh =\
            self.region_setup('Prison',30,20)
        fl = floc(br=6,bc=8,w=12,h=8)
        wh.building_random(loc(fl.br,fl.bc), fl.w, fl.h, door_qty_range=(1,2), rnd_stuff={'min_qty':3, 'max_qty':8}, name="Prison")
        humsmade = pm2(American, fuzloc=fl, minqty=10, maxqty=10)
        humspeechset = wh.get_data_lines('zombiehack/Human_speech')
        for hum in humsmade:
            hum.myenemyclasses.append(zh_Zombie)
            hum.add_to_rnd_speech(humspeechset)
        buildings = lev.get_zones_of_class(Building)
        zombies = pm2(zh_Zombie, fuzloc=floc(br=0,bc=0), minqty=5, maxqty=10, zones_disallowed=buildings)

    def make_Zoo(self):
        log('make Zoo')
        regname, w, h, reg, lev, stdloc, stdfloc, loc, floc, pm, pm2, wh =\
            self.region_setup('Zoo',30,20,edge_pref1='right', edge_pref2='left')
        fl = floc(br=6,bc=8,w=12,h=8)
        wh.building_random(loc(fl.br,fl.bc), fl.w, fl.h, door_qty_range=(1,2), rnd_stuff={'min_qty':3, 'max_qty':8}, name="Zoo")
        humsmade = pm2(American, fuzloc=fl, minqty=10, maxqty=10)
        humspeechset = wh.get_data_lines('zombiehack/Human_speech')
        for hum in humsmade:
            hum.myenemyclasses.append(zh_Zombie)
            hum.add_to_rnd_speech(humspeechset)
        buildings = lev.get_zones_of_class(Building)
        zombies = pm2(zh_Zombie, fuzloc=floc(br=0,bc=0), minqty=5, maxqty=10, zones_disallowed=buildings)
        return lev

    def make_PoliceStation(self):
        log('make PoliceStation')
        regname, w, h, reg, lev, stdloc, stdfloc, loc, floc, pm, pm2, wh =\
            self.region_setup('Police Station',30,20)
        fl = floc(br=6,bc=8,w=12,h=8)
        wh.building_random(loc(fl.br,fl.bc), fl.w, fl.h, door_qty_range=(1,2), rnd_stuff={'min_qty':3, 'max_qty':8}, name="Police Station")
        humsmade = pm2(American, fuzloc=fl, minqty=10, maxqty=10)
        humspeechset = wh.get_data_lines('zombiehack/Human_speech')
        for hum in humsmade:
            hum.myenemyclasses.append(zh_Zombie)
            hum.add_to_rnd_speech(humspeechset)
        buildings = lev.get_zones_of_class(Building)
        zombies = pm2(zh_Zombie, fuzloc=floc(br=0,bc=0), minqty=5, maxqty=10, zones_disallowed=buildings)

    def make_University(self):
        log('make University')
        regname, w, h, reg, lev, stdloc, stdfloc, loc, floc, pm, pm2, wh =\
            self.region_setup('University',30,20)
        fl = floc(br=6,bc=8,w=12,h=8)
        wh.building_random(loc(fl.br,fl.bc), fl.w, fl.h, door_qty_range=(1,2), rnd_stuff={'min_qty':3, 'max_qty':8}, name="University")
        humsmade = pm2(American, fuzloc=fl, minqty=10, maxqty=10)
        humspeechset = wh.get_data_lines('zombiehack/Human_speech')
        for hum in humsmade:
            hum.myenemyclasses.append(zh_Zombie)
            hum.add_to_rnd_speech(humspeechset)
        buildings = lev.get_zones_of_class(Building)
        zombies = pm2(zh_Zombie, fuzloc=floc(br=0,bc=0), minqty=5, maxqty=10, zones_disallowed=buildings)

    def make_Cemetary(self):
        log('make Cemetary')
        regname, w, h, reg, lev, stdloc, stdfloc, loc, floc, pm, pm2, wh =\
            self.region_setup('Cemetary',30,20)
        fl = floc(br=6,bc=8,w=12,h=8)
        wh.building_random(loc(fl.br,fl.bc), fl.w, fl.h, door_qty_range=(1,2), rnd_stuff={'min_qty':3, 'max_qty':8}, name="Cemetary")
        humsmade = pm2(American, fuzloc=fl, minqty=10, maxqty=10)
        humspeechset = wh.get_data_lines('zombiehack/Human_speech')
        for hum in humsmade:
            hum.myenemyclasses.append(zh_Zombie)
            hum.add_to_rnd_speech(humspeechset)
        buildings = lev.get_zones_of_class(Building)
        zombies = pm2(zh_Zombie, fuzloc=floc(br=0,bc=0), minqty=5, maxqty=10, zones_disallowed=buildings)

    def make_Bank(self):
        log('make Bank')
        regname, w, h, reg, lev, stdloc, stdfloc, loc, floc, pm, pm2, wh =\
            self.region_setup('Bank',30,20)
        fl = floc(br=6,bc=8,w=12,h=8)
        wh.building_random(loc(fl.br,fl.bc), fl.w, fl.h, door_qty_range=(1,2), rnd_stuff={'min_qty':3, 'max_qty':8}, name="Bank")
        pm2(USDollar, fuzloc=fl.clone(br=7,bc=9,w=10,h=6), minqty=20, maxqty=25, ctor_extra_args={'rnd_amount':{'min':100,'max':1000}})
        #humsmade = pm2(American, fuzloc=fl, minqty=10, maxqty=10)
        humspeechset = wh.get_data_lines('zombiehack/Human_speech')
        #for hum in humsmade:
        #    hum.myenemyclasses.append(zh_Zombie)
        #    hum.add_to_rnd_speech(humspeechset)
        buildings = lev.get_zones_of_class(Building)
        zombies = pm2(zh_Zombie, fuzloc=floc(br=0,bc=0), minqty=5, maxqty=10, zones_disallowed=buildings)

    def make_Church(self):
        log('make Church')
        regname, w, h, reg, lev, stdloc, stdfloc, loc, floc, pm, pm2, wh =\
            self.region_setup('Church',30,20)
        fl = floc(br=6,bc=8,w=12,h=8)
        wh.building_random(loc(fl.br,fl.bc), fl.w, fl.h, door_qty_range=(1,2), rnd_stuff={'min_qty':3, 'max_qty':8}, name="Church")
        humsmade = pm2(American, fuzloc=fl, minqty=10, maxqty=10)
        humspeechset = wh.get_data_lines('zombiehack/Human_speech')
        for hum in humsmade:
            hum.myenemyclasses.append(zh_Zombie)
            hum.add_to_rnd_speech(humspeechset)
        buildings = lev.get_zones_of_class(Building)
        zombies = pm2(zh_Zombie, fuzloc=floc(br=0,bc=0), minqty=5, maxqty=10, zones_disallowed=buildings)

    def make_SuperStore(self):
        log('make SuperStore')
        regname, w, h, reg, lev, stdloc, stdfloc, loc, floc, pm, pm2, wh =\
            self.region_setup('SuperStore',30,20)
        fl = floc(br=6,bc=8,w=12,h=8)
        wh.building_random(loc(fl.br,fl.bc), fl.w, fl.h, door_qty_range=(1,2), rnd_stuff={'min_qty':30, 'max_qty':40}, name="SuperStore")
        wh.make_and_put_rnd_stuff(20,30,7,9,10,6,lev,reg,thing_classes=thing_class_groups['store_food'])
        humsmade = pm2(American, fuzloc=fl, minqty=10, maxqty=10)
        humspeechset = wh.get_data_lines('zombiehack/Human_speech')
        for hum in humsmade:
            hum.myenemyclasses.append(zh_Zombie)
            hum.add_to_rnd_speech(humspeechset)
        buildings = lev.get_zones_of_class(Building)
        zombies = pm2(zh_Zombie, fuzloc=floc(br=0,bc=0), minqty=5, maxqty=10, zones_disallowed=buildings)

    def make_VenturiusEstate(self):
        log('make VenturiusEstate')
        regname, w, h, reg, lev, stdloc, stdfloc, loc, floc, pm, pm2, wh =\
            self.region_setup('The Estate of V. Venturius',30,20,route_from_start=False)
        fl = floc(br=6,bc=8,w=12,h=8)
        wh.building_random(loc(fl.br,fl.bc), fl.w, fl.h, door_qty_range=(1,2), rnd_stuff={'min_qty':3, 'max_qty':8}, name="Venturius Mansion")
        victor = VictorVenturius(wh)
        pm(victor, loc(r=8,c=10))

        def assistant(name):
            p = Human(wh, gender='female')
            p.name = name
            pm(p, loc(h-1, 12))
            #pm2(USDollar, fuzloc=fl.clone(br=7,bc=9,w=10,h=6), minqty=20, maxqty=25, ctor_extra_args={'rnd_amount':{'min':100,'max':1000}})
            ps = pm2(Human, fuzloc=fl.clone(br=6,bc=8,w=12,h=8), minqty=1, maxqty=1, ctor_extra_args={'gender':'female'})
            ps[0].name = name
            #humsmade = pm2(American, fuzloc=fl, minqty=10, maxqty=10)

        assistant('Syndi')
        assistant('Synthia')
        assistant('Bambi')
        assistant('Barbara')
        assistant('Lisa')
        assistant('Wendi')

        return lev

    def make_HexenhammerCastle(self):
        log('make HexenhammerCastle')
        regname, w, h, reg, lev, stdloc, stdfloc, loc, floc, pm, pm2, wh =\
            self.region_setup('Hexylvannia, Ohio',60,40,route_from_start=False)
        fl = floc(br=10,bc=10,w=20,h=20)
        wh.building_random(loc(fl.br,fl.bc), fl.w, fl.h, door_qty_range=(1,2), rnd_stuff={'min_qty':3, 'max_qty':8}, name="Hexenhammer Castle")
        hex = HeinrichHexenhammer(wh)
        pm(hex, loc(r=20,c=20))
        return lev

    def make_MegaMall(self):
        log('make MegaMall')
        regname, w, h, reg, lev, stdloc, stdfloc, loc, floc, pm, pm2, wh =\
            self.region_setup('The MegaMall',45,25)
        jfloc = floc(br=0,bc=0,w=40,h=20)
        wh.building_random(loc(jfloc.br,jfloc.bc), jfloc.w, jfloc.h, name='Silverthorn Mall', layout_name='mall', rnd_stuff={'min_qty':3, 'max_qty':8})
        humsmade = pm2(American, fuzloc=jfloc, minqty=25, maxqty=30)
        humspeechset = wh.get_data_lines('zombiehack/Human_speech')
        for hum in humsmade:
            hum.myenemyclasses.append(zh_Zombie)
            hum.add_to_rnd_speech(humspeechset)
        buildings = lev.get_zones_of_class(Building)
        zombies = pm2(zh_Zombie, fuzloc=floc(br=0,bc=0), minqty=5, maxqty=10, zones_disallowed=buildings)

    def make_ZionResearch(self):
        log('make ZionResearch')
        regname, w, h, reg, lev, stdloc, stdfloc, loc, floc, pm, pm2, wh =\
            self.region_setup('Zion Research Campus',43,18)
        jfloc = floc(br=0,bc=0,w=43,h=18)
        wh.building_random(loc(jfloc.br,jfloc.bc), jfloc.w, jfloc.h, name='Zion Research', layout_name='research_facility', rnd_stuff={'min_qty':3, 'max_qty':8})
        humsmade = pm2(Scientist, fuzloc=jfloc, minqty=15, maxqty=15)
        humspeechset = wh.get_data_lines('zombiehack/Human_speech')
        for hum in humsmade:
            hum.myenemyclasses.append(zh_Zombie)
            hum.add_to_rnd_speech(humspeechset)
        buildings = lev.get_zones_of_class(Building)
        zombies = pm2(zh_Zombie, fuzloc=floc(br=0,bc=0), minqty=5, maxqty=10, zones_disallowed=buildings)
        return lev

    def make_WendigoForest(self):
        log('make WendigoForest')
        regname, w, h, reg, lev, stdloc, stdfloc, loc, floc, pm, pm2, wh =\
            self.region_setup('Wendigo Forest',60,30,lev_name='ground level',edge_pref1='top', edge_pref2='bottom')
        shack = wh.building_random(loc(h/2,2), 3, 3, door_qty_range=(1,1), rnd_stuff={'min_qty':10, 'max_qty':15}, name='a shack')

        jfloc = floc(br=0,bc=0,w=60,h=30)
        trees = pm2(Tree, fuzloc=jfloc, minqty=300, maxqty=310, zones_disallowed=[shack,])
        trees = pm2(FruitTree, fuzloc=jfloc, minqty=10, maxqty=15, zones_disallowed=[shack,])
        return lev

    def make_MilitaryBase(self):
        log('make MilitaryBase')
        regname, w, h, reg, lev, stdloc, stdfloc, loc, floc, pm, pm2, wh =\
            self.region_setup('Fort Myers',50,32,route_from_start=False)
        jfloc = floc(br=3,bc=5,w=w-10,h=h-6)
        wh.building_random(loc(jfloc.br,jfloc.bc), jfloc.w, jfloc.h, name='Fort Myers', layout_name='military_base', rnd_stuff={'min_qty':3, 'max_qty':8})
        insidefloc = floc(br=5,bc=7,w=36,h=18)
        def equip(soldier):
            worn = (Helmet(wh,color='green'), Coat(wh,color='green'), Pants(wh,color='green'), Socks(wh), Boots(wh,color='black'))
            soldier.carry_and_wear(worn)
            wielded = (Gun(wh),)
            soldier.carry_and_wield(wielded)
        humsmade = pm2(Soldier, fuzloc=insidefloc, minqty=50, maxqty=75, preparefn=equip)
        humspeechset = wh.get_data_lines('zombiehack/Human_speech')
        for hum in humsmade:
            hum.myenemyclasses.append(zh_Zombie)
            hum.add_to_rnd_speech(humspeechset)
        buildings = lev.get_zones_of_class(Building)
        zombies = pm2(zh_Zombie, fuzloc=floc(br=0,bc=0), minqty=5, maxqty=10, zones_disallowed=buildings)
        return lev

    def make_Hospital(self):
        log('make Hospital')
        regname, w, h, reg, lev, stdloc, stdfloc, loc, floc, pm, pm2, wh =\
            self.region_setup('Dayton General Hospital',30,20)
        bfloc = floc(br=3,bc=3,w=22,h=8)
        wh.building_random(loc(bfloc.br,bfloc.bc), bfloc.w, bfloc.h, door_qty_range=(1,2), rnd_stuff={'min_qty':3, 'max_qty':8}, name="Gen. Hospital")
        wh.make_and_put_rnd_stuff(20, 30, bfloc.br, bfloc.bc, bfloc.w, bfloc.h, lev, reg, thing_classes=thing_class_groups['healing_items'])
        doctors = pm2(Doctor, fuzloc=bfloc, minqty=5, maxqty=8)
        patients = pm2(American, fuzloc=bfloc, minqty=20, maxqty=25)
        people = []
        people.extend(doctors)
        people.extend(patients)
        humspeechset = wh.get_data_lines('zombiehack/Human_speech')
        for hum in people:
            hum.myenemyclasses.append(zh_Zombie)
            hum.add_to_rnd_speech(humspeechset)
        buildings = lev.get_zones_of_class(Building)
        zombies = pm2(zh_Zombie, fuzloc=floc(br=0,bc=0), minqty=5, maxqty=10, zones_disallowed=buildings)

def is_devmode_allowed(request):
    return is_staff(request.user)

def is_devmode_allowed(request):
    return False

def wh_cacheper_content_report():
    items = wh_cacheper_content_list()
    s = 'size %s' % len(items)
    if len(items) > 0:
        s += EOL * 2
        s += EOL.join(items)
        s += EOL
    return s

def wh_cacheper_content_list():
    items = []
    for key in cache_per.cache:
        wh = cache_per.cache[key]
        modename = wh.gamemode.mode_name()
        tock = wh.ev.tock
        item = '%s: %s tock %s' % (key, modename, tock)
        items.append(item)
    return items

def wh_saveallgames_viewfn(request):
    #TODO consider moving most guts of this into a new method of CachePlusPersistStrategy (impl method) and PersistStrategy (interface meth/stub)
    saved_keys = []
    keys = cache_per.cache.keys()
    for key in keys:
        state = cache_per.cache[key]
        if state.gamemode.is_demo_mode(): # we don't save demomode game states
            continue
        if is_saved_on_disk_already(key):
            continue
        tock = state.ev.tock
        if tock == 0: # we don't save tock=0 game states
            continue
        fname, pstate_size = save_cache_entry_to_disk(key)
        entry = '%s|%s|%s' % (key, fname, pstate_size)
        saved_keys.append(entry)
    return saved_keys

def is_loggedin_perceived_by_admin_job(userid):
    last_login_later_than_logout = True
    has_session = True
    return last_login_later_than_logout and has_session

def wh_purge_inactive_games_from_cache(request):
    purged = []
    keys = cache_per.cache.keys()
    for key in keys:
        state = cache_per.cache[key]
        user_id, game_id = cache_per.extract_userid_gameid_from_cache_key(key)
        user = User.objects.get(id=user_id)
        now = time.time()
        if not is_loggedin_perceived_by_admin_job(user_id) or is_too_long_since_last_request(user_id):
            if not is_saved_on_disk_already(key):
                fname, pstate_size = save_cache_entry_to_disk(key)
            log('purging %s from mem cache' % key)
            del cache_per.cache[key]
            purged.append(key)
    return purged

def save_cache_entry_to_disk(wh_cache_key):
    state = cache_per.cache[wh_cache_key]
    user_id, game_id = cache_per.extract_userid_gameid_from_cache_key(wh_cache_key)
    tock = state.ev.tock
    dtime = datetime.datetime.now()
    fname = file_per.form_filename(user_id,game_id,tock,dtime)
    gs = Game.objects.filter(id=game_id)
    if len(gs) < 1:
        return #TODO log error because row should've existed or id wrong
    game = gs[0]
    savedir = file_per.get_savedirectory_for_game(game)
    fpath = savedir + '/' + fname
    pstate_size = file_per.persist_state_with_filename(state,fpath)
    return fname, pstate_size

def is_saved_on_disk_already(wh_cache_key):
    return False #TODO finish me, possibly check a tuple item in the cache entry's value; example: key -> (state, lastsavefilename, lastsavetimestamp)

def is_too_long_since_last_request(user_id):
    td = how_long_since_last_request(user_id)
    # watchout: code assumes limit is always less than 1 day
    #TODO get value from config:
    limit_secs = 60 * 10 # 10 min
    return td.days > 0 or td.seconds >= limit_secs

def how_long_since_last_request(user_id):
    ''' returns instance of datetime.timedelta class '''
    lrts = LastRequestTime.objects.filter(user=user_id)
    if len(lrts) > 0:
        lastreq = lrts[0]
        then = lastreq.when
        now = datetime.datetime.now()
        diff = now - then
        return diff
    else:
        return datetime.timedelta() # 0 diff, which is nonsense but safe

def wh_play_viewfn_helper(request, game, whsesskey, whsubclass, whhelp_viewfn, whusercmd_viewfn):
    trace('wh_play_viewfn_helper()')
    watch = StopWatch('wh_play_viewfn_helper(): ')
    wh = None
    s = None
    try:
        #TODO: WARNING: BE VERY CAREFUL WITH DISABLING GC!!!
        if gc.isenabled(): gc.disable()
        wh = None
        devmode_allowed = is_devmode_allowed(request)
        gameclass, modeclass = determine_gameclass_modeclass(request,game)
        if not force_reset and does_persisted_state_exist(request,game,whsesskey):
            wh = fetch_state(request,game,whsesskey)
            set_devmode(wh,devmode_allowed)
            set_gameclass_modeclass_for_reset(wh,gameclass,modeclass)
        else:
            debug('no persisted state found for game %s, user %s, so will load canned initstate', game.id, request.user.id)
            wh = return_new_wh_from_canned_initstates_chosen_randomly(gameclass,modeclass)
            wh.changed_since_last_render = True
            set_devmode(wh,devmode_allowed)
            set_gameclass_modeclass_for_reset(wh,gameclass,modeclass)
            persist_state(request, game, whsesskey, wh, disk_persist=False)
        wh.help_viewfn = whhelp_viewfn
        wh.usercmd_viewfn = whusercmd_viewfn
        s = wh.render_ui(game)
    finally:
        if not gc.isenabled(): gc.enable()
    log(watch.stop())
    return wh, s

def set_gameclass_modeclass_for_reset(wh, gameclass, modeclass):
    wh.set_cfg('reset_gameclass', gameclass)
    wh.set_cfg('reset_modeclass', modeclass)

def determine_gameclass_modeclass(request, game):
    user = request.user
    #TODO HACK - BEGIN
    gameclass = None
    modeclass = None
    premium = is_loggedin(user) and (has_premium_access(user) or has_full_sub_benefits(user) or is_beta_tester(user))
    if game.name == 'Dead By Zombie': #TODO bad way to do this
        gameclass = ZombieHack
        modeclass = (premium and ZombieHackFullGameMode) or ZombieHackDemoGameMode
    elif game.name == 'WolfenHack':
        gameclass = WolfenHack
        modeclass = (premium and WolfenHackFullGameMode) or WolfenHackDemoGameMode
    #TODO HACK - END
    return gameclass, modeclass

def determine_gameclass_modeclass(request, game):
    return ZombieHack, ZombieHackFullGameMode

def set_devmode(wh, devmode_allowed):
    #TODO the above log msgs should be done automaticaly inside body of the set_cfg() method:
    log('setting devmode_allowed to %s' % devmode_allowed)
    wh.set_cfg('devmode_allowed', devmode_allowed)

class Persister:
    def persist_state(self, wh, user, game, request=None, whsesskey=None):
        pass

    def fetch_state(self, user, game, request=None, whsesskey=None):
        pass

    def has_state(self, user, game, request=None, whsesskey=None):
        pass

class SessionPersister(Persister):
    def persist_state(self, wh, user, game, request, whsesskey):
        putintogamesess(request, game.id, whsesskey, wh)

    def fetch_state(self, user, game, request, whsesskey):
        return getfromgamesess(request, game.id, whsesskey)

    def has_state(self, user, game, request, whsesskey):
        return isingamesess(request, game.id, whsesskey)

class CachePersister(Persister):
    STATE_CACHE_KEY = 'webhack'

    def __init__(self):
        self.cache = {}

    def persist_state(self, wh, user, game, request=None, whsesskey=None):
        debug('PERSIST TO CACHE')
        cachekey = self._form_state_cache_key(user,game)
        self.cache[cachekey] = wh

    def fetch_state(self, user, game, request=None, whsesskey=None):
        debug('FETCH FROM CACHE')
        cachekey = self._form_state_cache_key(user,game)
        return self.cache[cachekey]

    def has_state(self, user, game, request=None, whsesskey=None):
        debug('CHECK CACHE')
        cachekey = self._form_state_cache_key(user,game)
        return cachekey in self.cache

    def _form_state_cache_key(self, user, game):
        return '%s-%s-%s' % (self.STATE_CACHE_KEY, user.id, game.id)

    def extract_userid_gameid_from_cache_key(self, cachekey):
        toks = cachekey.split('-')
        userid = int(toks[1])
        gameid = int(toks[2])
        return userid, gameid
# CachePersister - end

class DatabasePersister(Persister):
    def __init__(self, pickle_protocol=0):
        self.pickle_protocol = pickle_protocol

    def persist_state(self, wh, user, game, request=None, whsesskey=None):
        debug('PERSIST TO DATABASE')
        gs = self.fetch_state(user, game)
        if not gs:
            gs = GameState()
            gs.user = user
            gs.game = game
        wh_pickled = serialize(wh,'wh',protocol=self.pickle_protocol)
        gs.data = wh_pickled
        size = len(wh_pickled)
        gs.datasize = size
        watch = StopWatch('gs.save() to database with gs.datasize %s: ' % size)
        gs.save()
        debug(watch.stop())
        return size

    def has_state(self, user, game, request=None, whsesskey=None):
        gss = GameState.objects.filter(user=user, game=game)
        return len(gss) > 0

    def fetch_gs(self, user, game):
        gs = None
        watch = StopWatch('fetch_state_from_database(): user=%s, game=%s: ' % (user.id, game.id))
        gss = GameState.objects.filter(user=user, game=game)
        found_gs = len(gss) > 0
        if found_gs:
            gs = gss[0]
        debug(watch.stop())
        return gs

    def fetch_state(self, user, game, request=None, whsesskey=None):
        debug('FETCH FROM DATABASE')
        wh = None
        gs = self.fetch_gs(user,game)
        if gs:
            wh = deserialize(gs.data,'wh',protocol=self.pickle_protocol)
            wh.size = gs.datasize
            gc_enabled_before = gc.isenabled()
            gc.enable()
            #ogr = ObjGraphReporter(10)
            #wh.objreport = ogr.report(wh)
            if not gc_enabled_before: gc.disable()
        return wh
# DatabasePersister - end

class FilePersister(Persister):
    def __init__(self, pickle_protocol=2):
        self.pickle_protocol = pickle_protocol

    def persist_state(self, wh, user, game, request=None, whsesskey=None):
        tock = wh.ev.tock
        dtime = datetime.datetime.now()
        filename = self.get_filepathname(user,game,tock,dtime)
        self.persist_state_with_filename(wh,filename)

    def persist_state_with_filename(self, wh, filename):
        debug('PERSIST TO FILE')
        f = file(filename, mode='wb')
        wh_pickled = serialize(wh,'wh',protocol=self.pickle_protocol)
        size = len(wh_pickled)
        watch = StopWatch('file_per: write()/close() of data to file with datasize %s: ' % size)
        f.write(wh_pickled)
        f.close()
        debug(watch.stop())
        return size

    def fetch_state(self, user, game, request=None, whsesskey=None):
        filename = self.determine_best_saved_file_to_fetch(user,game)
        savedir = self.get_savedirectory_for_game(game)
        filepath = savedir + '/' + filename
        return self.fetch_state_with_filename(filepath)

    def determine_best_saved_file_to_fetch(self, user, game):
        best = None
        savedir = self.get_savedirectory_for_game(game)
        fnames = os.listdir(savedir) #TODO replace with cache-based equiv
        for fname in fnames:
            gameid, userid, tock, date, time = extract_info_from_filename(fname)
            #we can assume gameid will match game.id so don't check...
            if userid != user.id:
                continue
            # the best is the one most recently saved to disk
            if best is None:
                # first found, so make it the initial best
                best = (fname, date, time)
            else:
                if date >= best[1] and time >= best[2]:
                    # this is the new best, because more recent
                    best = (fname, date, time)
        return best[0] # fname

    def fetch_state_with_filename(self, filename):
        filename = 'data/webhack/initstates/default.zh.full.gamestate'
        #print 'fetch_state_with_filename: %s' % filename
        #raise filename
        
        debug('FETCH FROM FILE')
        wh = None
        f = file(filename,mode='rb')
        data = f.read()
        f.close()
        if len(data) > 0:
            wh = deserialize(data,'wh',protocol=self.pickle_protocol)
            wh.size = len(data)
            gc_enabled_before = gc.isenabled()
            gc.enable()
            #ogr = ObjGraphReporter(10)
            #wh.objreport = ogr.report(wh)
            if not gc_enabled_before: gc.disable()
        return wh

    def has_state(self, user, game, request=None, whsesskey=None):
        debug('CHECK IN FILE')

        savedir = self.get_savedirectory_for_game(game)
        fnames = os.listdir(savedir) #TODO replace with cache-based equiv
        for fname in fnames:
            gameid, userid, tock, date, time = extract_info_from_filename(fname)
            #we can assume gameid will match game.id so don't check...
            if userid == user.id:
                return True
        return False

    #TODO delete this fn if not used anymore
    def does_file_exist(self, fpath):
        #TODO rewrite below to use python std fn, like maybe os.path.exists()
        f = None
        try:
            f = file(fpath,mode='r')
            f.close()
        except:
            if f is not None:
                f.close()
            return False
        return True

    def get_filepathname(self, user, game, tock, dtime):
        savedir = self.get_savedirectory_for_game(game)
        return savedir + '/' + self.get_filename(user,game,tock,dtime)

    def get_savedirectory_for_game(self, game):
        #TODO game.mediasubdir unnec hits db each request, better to draw from a cache that persists in memory until server bounces, since this value (the subdir) won't change normally during server running lifetime
        gamesubdir = game.mediasubdir
        return self.get_savedirectory() + gamesubdir

    def get_savedirectory(self):
        return DBZ + '/saves/webhack/'

    def get_filename(self, user, game, tock, dtime):
        return self.form_filename(user.id,game.id,tock,dtime)

    def form_filename(self, userid, gameid, tock, dtime):
        def fo(num):
            width = 2
            return str(num).rjust(width,'0')

        date = '%s%s%s' % (dtime.year, fo(dtime.month), fo(dtime.day))
        time = '%s%s%s' % (fo(dtime.hour), fo(dtime.minute), fo(dtime.second))
        return 'gamestate-g%s-u%s-t%s-%s-%s.dat' % (gameid, userid, tock, date, time)
# FilePersister - end

class PersistStrategy:
    def does_persisted_state_exist(self, user, game, request, whsesskey):
        pass

    def fetch_state(self, user, game, request, whsesskey):
        pass

    def persist_state(self, user, game, request, whsesskey, wh, disk_persist=True):
        pass

class SessPersistStrategy(PersistStrategy):
    def does_persisted_state_exist(self, user, game, request, whsesskey):
        return sess_per.has_state(user,game,request,whsesskey)

    def fetch_state(self, user, game, request, whsesskey):
        return sess_per.fetch_state(user,game,request,whsesskey)

    def persist_state(self, user, game, request, whsesskey, wh, disk_persist=True):
        sess_per.persist_state(wh,user,game,request,whsesskey)

class CachePlusPersistStrategy(PersistStrategy):
    def __init__(self, main_per, cache_per):
        self.main_per = main_per
        self.cache_per = cache_per

    def does_persisted_state_exist(self, request, game, whsesskey):
        user = request.user
        if self.cache_per.has_state(user,game): return True
        return self.main_per.has_state(user,game)

    def fetch_state(self, request, game, whsesskey):
        wh = None
        user = request.user
        if self.cache_per.has_state(user,game):
            wh = self.cache_per.fetch_state(user,game)
        else: # state not in cache, so fetch from database, and cache it:
            wh = self.main_per.fetch_state(user,game)
            self.cache_per.persist_state(wh,user,game)
        return wh

    def persist_state(self, request, game, whsesskey, wh, disk_persist=True):
        record_session_size(request,wh)
        user = request.user
        should_main_persist = disk_persist
        if should_main_persist:
            wh.size = self.main_per.persist_state(wh,user,game)
            #ogr = ObjGraphReporter(10)
            #wh.objreport = ogr.report(wh)
        self.cache_per.persist_state(wh,user,game)
# CachePlusPersistStrategy - end

# called by bin/makeinitstate.py:
def gen_new_gamestate_and_save_to_file(webhacksubclass, gamemodeclass, filename, devmode_allowed):
    wh = webhacksubclass()
    wh.reset(gamemodeclass)
    wh.set_cfg('devmode', False)
    wh.set_cfg('devmode_allowed', devmode_allowed)
    per = FilePersister()
    wh.size = per.persist_state_with_filename(wh,filename)

def strip_non_gamestate_filenames(fnames):
    return [f for f in fnames if f.endswith('.gamestate')]

def strip_all_filenames_but_for_game_and_mode(fnames, game_indic, mode_indic):
    frag = '.%s.%s.' % (game_indic, mode_indic)
    return [f for f in fnames if frag in f]

def return_new_wh_from_canned_initstates_chosen_randomly(gameclass, modeclass):
    game_indic = gameclass.init_state_file_indicator
    mode_indic = modeclass.init_state_file_indicator
    path = DATADIR + 'initstates'
    fnames = os.listdir(path)
    fnames = strip_non_gamestate_filenames(fnames)
    fnames = strip_all_filenames_but_for_game_and_mode(fnames,game_indic,mode_indic)
    debug('canned initstate filenames found at %s: %s', path, fnames)
    fname = random.choice(fnames)
    debug('randomly chose: %s', fname)
    filepath = '%s/%s' % (path,fname)
    debug('loading: %s', filepath)
    per = FilePersister()
    wh = per.fetch_state_with_filename(filepath)
    debug('load success. wh.size: %s', wh.size)
    return wh

sess_per = SessionPersister()
cache_per = CachePersister()
db_per = DatabasePersister()
file_per = FilePersister()
sess_stgy = SessPersistStrategy()
dbcache_stgy = CachePlusPersistStrategy(db_per,cache_per)
filecache_stgy = CachePlusPersistStrategy(file_per,cache_per)

per_stgy = filecache_stgy


def does_persisted_state_exist(request, game, whsesskey):
    debug('does_persisted_state_exist()')
    debug('persist strategy: %s' % per_stgy.__class__.__name__)
    return per_stgy.does_persisted_state_exist(request,game,whsesskey)

def fetch_state(request, game, whsesskey):
    trace('fetch_state()')
    debug('persist strategy: %s' % per_stgy.__class__.__name__)
    wh = per_stgy.fetch_state(request,game,whsesskey)
    if not hasattr(wh,'sess_size'): #TODO TMP HACK to workaround bug, should eventually be removed
        wh.sess_size = 1
    return wh

def persist_state(request, game, whsesskey, wh, disk_persist=True):
    trace('persist_state()')
    debug('persist strategy: %s' % per_stgy.__class__.__name__)
    per_stgy.persist_state(request,game,whsesskey,wh,disk_persist)

def record_session_size(request, wh):
    sess_pickled = serialize(request.session,'session')
    wh.sess_size = len(sess_pickled)

default_pickle_protocol = 0

def serialize(obj, objname, protocol=None):
    if protocol is None:
        protocol = default_pickle_protocol
    watch = StopWatch('serialize(%s) with pickle protocol %s: ' % (objname,protocol))
    obj_ser = pickle.dumps(obj, protocol=protocol)
    debug(watch.stop())
    debug('serialized %s len: %s bytes (protocol %s)' % (objname, len(obj_ser), protocol))
    return obj_ser

def deserialize(obj_ser, objname, protocol=None):
    if protocol is None:
        protocol = default_pickle_protocol
    watch = StopWatch('deserialize(%s) with pickle protocol %s: ' % (objname,protocol))
    obj = pickle.loads(obj_ser)
    debug(watch.stop())
    debug('serialized %s len: %s bytes (protocol %s)' % (objname, len(obj_ser), protocol))
    return obj

def wh_usercmd_viewfn_helper(request, whsesskey):
    trace('wh_usercmd_viewfn_helper()')
    response = None
    watchmsgpre = 'wh_usercmd_viewfn_helper(): '
    watch_total = StopWatch(watchmsgpre)
    try:
        #TODO: WARNING: BE VERY CAREFUL WITH DISABLING GC!!!
        if gc.isenabled(): gc.disable()
        response, watchmsgsuf = subfn_wh_usercmd_viewfn_helper(request,whsesskey,watchmsgpre)
    finally:
        if not gc.isenabled(): gc.enable()
    log(watch_total.stop(watchmsgpre,watchmsgsuf))
    return response

def subfn_wh_usercmd_viewfn_helper(request, whsesskey, watchmsgpre):
    devmode_allowed = is_devmode_allowed(request)

    if not is_loggedin(request.user):
        s = 'you are not logged in. you must be logged in to play.' 
        response = HttpResponse(s)
        watchmsgsuf = ' BUT IN CASE where returned early without doing anything due to user not logged in'
        return response, watchmsgsuf
    #TODO also check in GET, decide which is used then only use the params in that one ignoring the other

    watch = StopWatch('get cmd and gameid from req POST: ')
    paramsrc = None
    if 'gameid' in request.POST:
        paramsrc = request.POST
    else:
        paramsrc = request.GET
    gameid = int(paramsrc['gameid'])
    cmd = paramsrc['cmd']
    log(watch.stop())

    watch = StopWatch('fetch Game row from db: ')
    game = Game.objects.get(id=gameid) #doing early so can puke early
    xxx = game.id
    log(watch.stop())

    wh = None
    if does_persisted_state_exist(request,game,whsesskey):
        wh = fetch_state(request,game,whsesskey)
    else:
        s = no_persisted_state_found_msg(request.user,game)
        return HttpResponse(s), ''

    # Signal to the UI that it should re-render the page on next page request
    wh.changed_since_last_render = True

    set_devmode(wh,devmode_allowed)

    watch = StopWatch('building cmd params from req POST params: ')
    params = {}
    was_rel_dir_cmd_submit = False
    for k in request.POST:
        if k == 'gameid' or k == 'cmd':
            continue
        pre = SUBMIT_STYLE_PARAMS_PREFIX
        if k.startswith(pre):
            was_rel_dir_cmd_submit = True
            log('found POST param starting with "%s": %s' % (pre,k))
            paramspart = k[len(pre):]
            prms = eval(paramspart)
            log('we parsed it into: %s  type %s' % (prms,type(prms)))
            params.update(prms)
        else:
            params[k] = request.POST[k]
    if was_rel_dir_cmd_submit:
        command = params['command']
        setname = None
        if command in wh.get_directional_move_usercmds_bare():
            setname = 'move'
        elif command in wh.get_directional_nonmove_usercmds_bare():
            setname = 'nonmove'
        wh.rel_dir_cmd_last_submitted[setname] = params['command']
    log(watch.stop())

    log('params: %s' % params)

    watch = StopWatch('dispatch_usercmd(\''+str(cmd)+'\',...): ')
    success, reason, should_persist_to_disk, replace_wh_with = wh.dispatch_usercmd(cmd,params)
    log(watch.stop())

    new_wh_desc = None 
    if replace_wh_with is None:
        new_wh_desc = 'None'
    else:
        new_wh_desc = 'id(): ' + str(id(replace_wh_with)) + ' wh.size: %s' % replace_wh_with.size
    log('success returned: %s',success)
    log('replace_wh_with returned: %s', new_wh_desc)

    response = None
    watchmsgsuf = None
    if success:
        if replace_wh_with is not None:
            log('replacing wh with new instance, before persisting; wh.size: %s',wh.size)
            wh = replace_wh_with
            should_persist_to_disk = False
    
        persist_state(request, game, whsesskey, wh, disk_persist=should_persist_to_disk)
        watch = StopWatch('build redirect to play view: ')
        response = redirect(views.playwebgame.makeviewurlfn(game))
        log(watch.stop())
    else:
        watchmsgsuf = ' BUT IN CASE where dispatch returned failure'
        response = HttpResponse(reason)

    return response, watchmsgsuf

def no_persisted_state_found_msg(user, game):
    s = 'no persisted state found for this combination of user and game (user: %s (%s) game: %s (%s))' % (user.username, user.id, game.name, game.id)
    return s

def wh_help_viewfn_helper(request, whsesskey):
    trace('wh_help_viewfn_helper()')
    #views = groglogic.mainapp.views
    try:
        #TODO: WARNING: BE VERY CAREFUL WITH DISABLING GC!!!
        if gc.isenabled(): gc.disable()
        gameid = int(request.GET['gameid'])
        game = Game.objects.get(id=gameid)
        s = header(request, views.playwebgame, title=game.name) + EOL
        if does_persisted_state_exist(request,game,whsesskey):
            wh = fetch_state(request,game,whsesskey)
            s += wh.get_help_blurb() + EOL + EOL
            s += link(site_url(views.playwebgame.makeviewurlfn(game)),'back') + EOL
        else:
            s = no_persisted_state_found_msg(request.user,game)
    finally:
        if not gc.isenabled(): gc.enable()
    return HttpResponse(s)

################################
# Website View Functions - end #
################################


# Global Functions


########################################
# Thing Type Marker Interfaces - begin #
########################################

class RndStuff: pass

######################################
# Thing Type Marker Interfaces - end #
######################################

#TODO deprecated function; can't delete it until I get all callers of it switched to new system
def class_prep(klass, ch=None, color=None):
    if ch is not None:
        klass.char = ch
    if color is not None:
        klass.charcolor = color

def get_instantiable_thing_classes(namespace, alsoklass=None):
    classes = set()
    keys = namespace.keys()
    for k in keys:
        v = namespace[k]
        if isclass(v):
            if issubclass(v,Thing) and 'abstract' not in vars(v):
                match = True
                if alsoklass is not None:
                    match = v is alsoklass or issubclass(v,alsoklass)
                if not match:
                    continue
                if v not in classes:
                    classes.add(v)
    return classes

def is_devonly(obj):
    return has_meta_with_value(obj,DEVONLY_METAKEY,True)

def has_meta_with_value(obj, metakey, value):
    if hasattr(obj,'meta') and obj.meta is not None:
        if metakey in obj.meta:
            return obj.meta[metakey] == value
    return False


##################
# Mixins - begin #
##################

class IsOpenCloseable:
    abstract = True

    def __init__(self):
        self.opened = False

    def open(self):
        self.opened = True

    def close(self):
        self.opened = False

    def toggle_openclose_state(self):
        self.opened = not self.opened

class HasHP:
    abstract = True

    def __init__(self):
        self.init_hp(1)

    def init_hp(self, max, cur=None):
        if isinstance(max,tuple):
            max1 = max[0]
            max2 = max[1]
            max = rnd_in_range(max1,max2)
        self.hp_max = max
        if cur is None:
            cur = max
        self.hp = cur

    def reset_hp(self):
        self.hp = self.hp_max

    def is_destroyed(self):
        return not self.has_hp()

    def has_hp(self):
        return self.hp > 0

    def has_max_hp(self):
        return self.hp == self.hp_max

    def describe_damageness(self):
        return '%s hp' % self.hp

    def hp_str(self):
        return 'hp %s/%s' % (self.hp, self.hp_max)

class AppHasID(HasID):
    abstract = True

    def __init__(self, webhack):
        HasID.__init__(self, webhack.idsys)

#TODO rename to HasSpeech, move out of this file. Create a SpeechSystem, and move most of the logic method below out of HasSpeech into SpeechSystem, keeping pretty much only the self.randomspeechset and it's init in HasSpeech
class RndTalker: # a mixin
    abstract = True

    def __init__(self):
        self.randomspeechset = None

    def clear_speech(self):
        self.randomspeechset = None

    def add_to_rnd_speech(self, what):
        if self.randomspeechset == None:
            self.randomspeechset = []
        if isinstance(what,type([])):
            self.randomspeechset.extend(what)
        else:
            self.randomspeechset.append(what)

    def set_rnd_speech_set(self, newset):
        self.randomspeechset = newset

    def would_say_something_aloud_randomly_now(self):
        return self.randomspeechset != None and len(self.randomspeechset) > 0

    def give_something_to_say_aloud(self):
        if self.randomspeechset is not None:
            return random.choice(self.randomspeechset)
        else: return None

class HasColor:
    abstract = True

    def __init__(self, webhack, color=None):
        if color is not None:
            self.color = color
        else:
            self.color = webhack.textpools.get_random_entry('colors')

    def get_color(self):
        return self.color

class HasInventory:
    abstract = True

    def __init__(self):
        self.inventory = []
        self.worn = set()
        self.wielded = set()

    def inventory_add(self, thing):
        self.inventory.append(thing)

    def inventory_remove(self, thing):
        if thing in self.wielded:
            self.wielded.remove(thing)
        if thing in self.worn:
            self.worn.remove(thing)
        if thing in self.inventory:
            self.inventory.remove(thing)

    def carry(self, thing):
        things = None
        if not isinstance(thing,type([])) and not isinstance(thing,type(set())) and not isinstance(thing,type(tuple())):
            things = (thing,)
        else:
            things = thing
        for thing in things:
            self.inventory_add(thing)

    def find_thing_in_inventory_with_id(self, thingid):
        for thing in self.inventory:
            if thing.id_thing() == thingid:
                return thing
        else: return None

    def describe_worn(self):
        s = ''
        for th in self.worn:
            if len(s) > 0: s += ', '
            s += th.describe()
        return s

    def describe_wielded(self):
        s = ''
        for th in self.wielded:
            if len(s) > 0: s += ', '
            s += th.describe()
        return s

    def in_inventory(self, what):
        return what in self.inventory

    def list_inventory(self):
        return list(self.inventory)

    def list_inventory_of_class(self, klass):
        return [x for x in self.inventory if isinstance(x,klass)]

    def wielded_set(self):
        return set(self.wielded)

    def wielded_list(self):
        return list(self.wielded)

    def worn_set(self):
        return set(self.worn)

    def worn_list(self):
        return list(self.worn)

    def nonwielded_nonworn_list(self):
        return [th for th in self.inventory if not self.does_wear(th) and not self.does_wield(th)]

    def nonwielded_nonworn_set(self):
        return set(self.nonwielded_nonworn_list())

    def has_inventory(self):
        return len(self.inventory) > 0

    def has_unworn_unwielded_inventory(self):
        things = self.nonwielded_nonworn_list()
        return len(things) > 0

    def report_inventory(self, delim='\n', withid=False):
        return self.report_inventory_from(self.inventory, delim, withid=withid)

    def report_unworn_unwielded_inventory(self, delim='\n', withid=False):
        things = self.nonwielded_nonworn_list()
        return self.report_inventory_from(things, delim, withid=withid)

    def report_inventory_from(self, invlist, delim, withid=False):
        described_inventory = map(lambda thing: thing.describe(withid=withid), invlist)
        return delim.join(described_inventory)

    def has_worn(self):
        return len(self.worn) > 0

    def has_wielded(self):
        return len(self.wielded) > 0

    def does_wear(self, thing):
        return thing in self.worn

    def does_wield(self, thing):
        return thing in self.wielded

    def does_wear_class(self, thingclass):
        for th in self.worn:
            if isinstance(th,thingclass):
                return True
        else: return False

    def does_wield_class(self, thingclass):
        for th in self.wielded:
            if isinstance(th,thingclass):
                return True
        else: return False

    def get_worn_of_class(self, thingclass):
        ths = []
        for th in self.worn:
            if isinstance(th,thingclass):
                ths.append(th)
        return ths

    def get_wielded_of_class(self, thingclass):
        ths = []
        for th in self.wielded:
            if isinstance(th,thingclass):
                ths.append(th)
        return ths

    def wearing_count(self):
        return len(self.worn)

    def wielded_count(self):
        return len(self.wielded)

    def can_wear(self, thing):
        return thing.is_wearable()

    def can_unwear(self, thing):
        return thing.is_unwearable()

    def can_wield(self, thing):
        return thing.is_wieldable()

    def can_unwield(self, thing):
        return thing.is_unwieldable()

    def carry_and_wear(self, thing, feedback=True):
        self.carry(thing)
        self.wear(thing,feedback)

    def carry_and_wield(self, thing, feedback=True):
        self.carry(thing)
        self.wield(thing,feedback)

    def wear(self, thing, feedback=True):
        things = None
        if not isinstance(thing,type([])) and not isinstance(thing,type(set())) and not isinstance(thing,type(tuple())):
            things = (thing,)
        else:
            things = thing
        for thing in things:
            if not self.does_wear(thing):
                if self.can_wear(thing):
                    if self.does_wield(thing):
                        if self.can_unwield(thing):
                            self.unwield(thing)
                        else:
                            s = '%s could not wear %s because was wielded and could not unwield' % (self.describe(), thing.describe())
                            self.wh.feedback_ifyou(self,s)
                            continue
                    self.worn.add(thing)
                    s = '%s wear %s' % (self.describe(), thing.describe())
                    self.wh.feedback_ifyou(self,sentence(s),feedback)

    def unwear(self, thing):
        if self.does_wear(thing):
            if self.can_unwear(thing):
                self.worn.remove(thing)
                s = '%s take off %s' % (self.describe(), thing.describe())
                self.wh.feedback_ifyou(self,sentence(s))

    def wield(self, thing, feedback=True):
        things = None
        if not isinstance(thing,type([])) and not isinstance(thing,type(set())) and not isinstance(thing,type(tuple())):
            things = (thing,)
        else:
            things = thing
        for thing in things:
            if not self.does_wield(thing):
                if self.can_wield(thing):
                    if self.does_wear(thing):
                        if self.can_unwear(thing):
                            self.unwear(thing)
                        else:
                            s = '%s could not wield %s because was worn and could not unwear' % (self.describe(), thing.describe())
                            self.wh.feedback_ifyou(self,s)
                            continue
                    self.wielded.add(thing)
                    s = '%s wield %s' % (self.describe(), thing.describe())
                    self.wh.feedback_ifyou(self,sentence(s),feedback)

    def unwield(self, thing):
        if self.does_wield(thing):
            if self.can_unwield(thing):
                self.wielded.remove(thing)
                s = '%s unwield %s' % (self.describe(), thing.describe())
                self.wh.feedback_ifyou(self,sentence(s))
#class HasInventory - end

class Useable:
    abstract = True
    def __init__(self):
        assertNotDirectInstantiate(self,Useable)
    def use_by(self, user):
        return ''

class Edible:
    abstract = True
    foodvalue_min = 0
    foodvalue_max = 0
    foodvalue = foodvalue_min

    def __init__(self):
        assertNotDirectInstantiate(self, Edible)
        self.foodvalue = rnd_in_range(self.foodvalue_min, self.foodvalue_max)

    def consume(self, amount=1):
        return self.extract_foodvalue(amount)

    def get_foodvalue(self):
        return self.foodvalue

    def extract_foodvalue(self, amount=1):
        if self.foodvalue < 1:
            return 0
        else:
            if amount > self.foodvalue:
                amount = self.foodvalue
            self.foodvalue -= amount
            return amount

    def describe_foodvalue(self):
        return '%s calories' % self.foodvalue

class Eater:
    abstract = True
    stomach_size = TICKS_PER_DAY_DEFAULT
    stomach = stomach_size
    bitesize_max = 1
    digest_rate = 1 # per tick
    digests = True
    starves = True

    def __init__(self):
        pass

    def can_self_eat_this(self, what):
        v = isinstance(what,Edible)
        reason = ''
        if not v:
            reason = 'It is not edible.'
        self.wh.log('for %s we return %s %s' % (what.describe(), v, reason))
        return v, reason

    def eat(self, what):
        bitesize = self.bitesize_max
        stomach_space = self.stomach_size - self.stomach
        if stomach_space < bitesize:
            bitesize = stomach_space
        amount_ate = what.consume(bitesize)
        self.stomach += amount_ate
        return amount_ate

    def digest(self):
        if not self.has_empty_stomach():
            digest_amount = self.get_digest_rate()
            if digest_amount > self.stomach:
                digest_amount = self.stomach
            self.stomach -= digest_amount
            if self.stomach < 0:
                self.stomach = 0
            return digest_amount
        else: return 0

    def has_full_stomach(self):
        return self.stomach >= self.stomach_size

    def has_empty_stomach(self):
        return self.stomach <= 0

    def get_stomach(self):
        return self.stomach

    def get_stomach_size(self):
        return self.stomach_size

    def get_digest_rate(self):
        return self.digest_rate

    def does_digest(self):
        return self.digests

    def may_starve(self):
        return self.starves
# Eater - end

################
# Mixins - end #
################

#########################
# Thing Classes - begin #
#########################

class Thing(HasLocation,HasFacts,HasHP,AppHasID):
    abstract = True
    char = ','
    dmg_absorption = 0
    invuln = False
    basebasedesc = 'nondescript thing'
    render_importance = 1
    invis = False

    def __init__(self, webhack):
        assert self.__class__ is not Thing, 'Thing cannot be instantiated directly, only a subclass'
        HasLocation.__init__(self)
        HasFacts.__init__(self)
        HasHP.__init__(self)
        AppHasID.__init__(self, webhack)
        self.wh = webhack
        self.tock_created = self.wh.ev.tock

    def damage_absorbs(self):
        return self.dmg_absorption

    def is_wearable(self):
        return False

    def is_unwearable(self):
        return True

    def is_wieldable(self):
        return False

    def is_unwieldable(self):
        return True

    def is_invisible(self):
        return self.invis

    def get_basedesc(self):
        return awordify(self.basebasedesc)

    def statedump(self):
        return ''

    def get_render_importance(self):
        return self.render_importance

    def understands_speech(self):
        return False

    def does_self_block_adding_thing_to_self_cell(self):
        return False

    def he(self):
        #for use in user-facing sentences where a 'he' would go if self were male
        # for example, "He ate the food."
        # in the case of a generic thing, we would say "It ate the food."
        # related methods are 'him()' and 'his()
        return 'it'

    def him(self):
        return 'it'

    def his(self):
        return "it's"

    def handle_event_tick(self, event):
        pass

    def render_char(self):
        char = None
        color = None

        if hasattr(self, 'char'):
            char = self.char
        elif hasattr(self.__class__, 'char'):
            char = self.__class__.char

        if hasattr(self, 'charcolor'):
            color = self.charcolor
        elif hasattr(self.__class__, 'charcolor'):
            color = self.__class__.charcolor

        return char, color

    def would_you_find_interesting(self):
        return True

    def sound_reaches_self(self, sound_event):
        pass

    def can_be_picked_up(self):
        return True

    def is_invuln(self):
        return self.invuln

    def describe(self, withid=False):
        idstr = self.withid_helper(withid)
        return '%s%s' % (self.get_basedesc(), idstr)

    def full_describe(self, withid=False):
        return self.describe(withid)

    def describe_damageness(self):
        return None

class Lifeform(Thing,HasMind,HasInventory,RndTalker,Eater):
    char = 'l'
    atkhitchance = (1,2) # num,denom; 1,2 = 1 out of 2 = 50% chance
    atkdmg = 1
    always_hits = False
    always_do_kill_dmg = False
    digests = False
    starves = False
    basebasedesc = 'lifeform'
    render_importance = 7

    def __init__(self, wh, mind2use=None):
        assert self.__class__ is not Lifeform, 'Lifeform cannot be instantiated directly, only a subclass'
        Thing.__init__(self,wh)
        HasInventory.__init__(self)
        mymind = None
        if mind2use is not None:
            if isinstance(mind2use,LifeformMind):
                mymind = mind2use
            else: raise 'mind2use must be LifeformMind or subclass; you gave me: ' + str(mind2use)
        else:
            mymind = LifeformMind(self)
        HasMind.__init__(self, mymind)
        RndTalker.__init__(self)
        Eater.__init__(self)
        self.myfriendclasses = []
        self.myenemyclasses = []
        self.myfriends = []
        self.myenemies = []
        self.min_sound_volume_heard = 4

    def render_char(self):
        char, color = Thing.render_char(self)
        if self.does_wear_class(Costume):
            costume = self.get_worn_of_class(Costume)[0]
            char = costume.get_symbol_shown_on_map_when_worn()
        return char, color

    def does_always_hit(self):
        return self.always_hits

    def does_always_do_kill_dmg(self):
        return self.always_do_kill_dmg

    def use(self, what):
        return what.use_by(self)

    def mind_content_load(self, thingclassname, subdir=''):
        cln = thingclassname

        try:
            self.wh.think_all_in(self, '%s%s %s' % (subdir,cln,'thoughts'))
        except IOError, e:
            self.wh.log(str(e))

        try:
            self.wh.believe_all_in(self, '%s%s %s' % (subdir,cln,'beliefs'))
        except IOError, e:
            self.wh.log(str(e))

        try:
            self.add_to_rnd_speech(self.wh.get_data_lines('%s%s %s' % (subdir,cln,'speech')))
        except IOError, e:
            self.wh.log(str(e))

    def statedump(self):
        return Thing.statedump(self) #TODO

    def handle_event_tick(self, event):
        Thing.handle_event_tick(self, event)
        self.body_tick(event)
        if self.should_ai_control_actions():
            if self.is_alive():
                self.mind.tick() # this line assumes mind is LifeformMind

    def body_tick(self, event):
        #TODO food digestion, disease, poison, fatigue
        pass

    def should_ai_control_actions(self):
        return True

    def sound_reaches_self(self, sound_event):
        Thing.sound_reaches_self(self, sound_event)

        #TODO make it matter if he hears it - sparks his interest? if he's a Guard on alert for enemy intruders, he may choose to go investigate this sound (move towards sound origin loc, etc.)
        can_hear, failreason = self.can_hear_this_sound_right_now(sound_event)
        if can_hear:
            self.mind.sound_reaches_me(sound_event)

    def can_hear_this_sound_right_now(self, sound_event):
        if not self.is_alive(): return False, ('because dead')
        event = sound_event
        where = event.where
        volume = event.volume
        soundloc = where
        if soundloc is None or self.loc is None:
            self.wh.log('\n\n\n\nBAD SOUND DATA REACHED Lifeform.can_hear_this_sound_right_now:')
            self.wh.log('soundloc %s' % soundloc)
            self.wh.log('self.loc %s' % self.loc)
            self.wh.log('event: %s' % event)
            self.wh.log('self: %s' % self.describe())
            self.wh.log('\n\n\n\n')
        #TODO whether hears (and what effects of are) should also depend on: is deaf? asleep? unconscious?
        distance = int(dist(soundloc.r, soundloc.c, self.loc.r, self.loc.c))
        adj_volume = volume - distance
        if adj_volume < 0: adj_volume = 0
        # lower hear_strength is stronger hearing, because it means what is the lowest/faintest sound you can hear, as that volume is when received by your ear (after orig volume level adjusted downward with increasing distance from it's source)
        #TODO this should be done for ALL hearers of the sound, not just YOU!
        whether_you_hear_it = adj_volume >= self.min_sound_volume_heard
        answer = None
        if whether_you_hear_it:
            answer = (True, tuple())
        else:
            answer = (False, ('too faint to be heard',))
        return answer

    def can_you_pickup_this(self, thing):
        return True

    def pickup_many(self, things):
        #TODO refactor so i match against any seq not just lists and tuples:
        things = None
        if isinstance(what,type(list())) or isinstance(what,type(tuple(()))):
            things = what
        else:
            things = [what]
        results = []
        for thing in things:
            success, reason = self.pickup(thing)
            result = (success, reason)
            results.append(result)
        return results

    def pickup(self, thing):
        #TODO since removing from map should make sure that thing is still reachable by the geosystem -- it should still know that it EXISTS in the world, and, WHERE in the world, even if it is inside some thing's inventory
        #TODO any thing in an inventory due to this code will not receive ticks and probably not most other events either
        origloc = thing.loc
        self.wh.geo.remove_from_map(thing)
        self.inventory_add(thing)
        event = PickedUpEvent(what=thing, bywho=self, thingwaswhere=origloc)
        self.wh.emit_event(event)
        return True, ''

    def drop(self, thing, where=None):
        self.wh.log('drop() got where: %s' % where)
        if self.does_wield(thing):
            if self.can_unwield(thing):
                self.unwield(thing)
            else:
                raise DropFailDueToNotUnwieldable(thing)

        if self.does_wear(thing):
            if self.can_unwear(thing):
                self.unwear(thing)
            else:
                raise DropFailDueToNotUnwearable(thing)

        if where is None:
            where = self.loc
        self.inventory_remove(thing)
        success, reason = self.wh.geo.put_on_map(thing,where)
        if success:
            verb = self.wh.lh.itverbify(self, 'to drop', tense='past')
            s = '%s %s' % (verb, thing.describe())
            self.wh.feedback_ifyou(self,sentence(s))
            #TODO define DROPPED_EVENT; add listener for it that itself emits a SOUND_EVENT representing the sound of the thing hitting the ground
            event = DroppedEvent(what=thing,bywho=self,where=where)
            self.wh.emit_event(event)
        else:
            self.inventory.append(thing) # so it's not lost into thin air!
            s = 'failed to drop %s due to %s' % (thing.describe(), reason)
            if self is self.wh.you:
                self.wh.feedback(sentence('you '+s))
            else:
                self.wh.error(sentence(thing.describe()+s))

    def dropall(self, where=None):
        self.wh.log('dropall() got where: %s' % where)
        if where is None:
            where = self.loc
        carried = list(self.inventory)
        for thing in carried:
            try: self.drop(thing,where)
            except DropFail, ex: self.wh.log('dropall() caught DropFail: ' + str(ex))

    def is_capable_of_speech(self):
        return False

    def is_capable_of_random_speech_by_ai(self):
        return True

    def get_odds_of_rnd_move(self):
        return 1,2 # 50% chance is default

    def get_corpse_class(self):
        #TODO also climb up self's superclass tree, trying to use any of those parent class's corpseclass attrib, if any exist, and only if all of that fails would you resort to returning hardcoded default of Lifeform.corpseclass
        if hasattr(self.__class__, 'corpseclass'):
            return self.__class__.corpseclass
        else: return Lifeform.corpseclass

    def get_dynamic_additions_to_rndspeechset(self):
        addl_speech = []
        if hasattr(self,'name'):
            if self.name != None:
                addl_speech.append("I'm " + self.name + '.')
        return addl_speech

    def is_alive(self):
        return not self.is_destroyed()

    def is_something_there_you_would_attack(self, loc):
        r = loc.r
        c = loc.c
        cell = loc.level.grid[r][c]
        for th in cell.things:
            if self.would_self_attack_this_thing(th):
                return True
        return False

    def identify_best_attack_target_there(self, loc):
        best = None 
        cell = self.wh.geo.get_cell(loc.level,loc.r,loc.c)
        for thing in cell.things:
            if self.would_self_attack_this_thing(thing):
                howgood = self.how_good_of_attack_target_is_this(thing)
                if best is None:
                    best = (howgood, thing)
                else:
                    if howgood > best[0]:
                        best = (howgood, thing)
        if best is not None:
            return best[1]
        else: return None
    identify_best_attack_target_there.assumes = 'self.loc != None and self.loc.level != None'

    def how_good_of_attack_target_is_this(self, thing):
        #TODO HACK needs refactor, not right way to implement this method!
        if thing == self: return 0
        if isinstance(thing,Corpse): return 5
        if isinstance(thing,zh_Zombie): return 40
        if isinstance(thing,Human) and thing.is_alive(): return 10
        if isinstance(thing,Door) and not thing.opened: return 4
        if isinstance(thing,Window) and not thing.broken: return 3
        if isinstance(thing,Barricade): return 3
        if isinstance(thing,Wall): return 2
        if isinstance(thing,Stairway): return 1
        return 0

    def identify_good_attack_target(self):
        target = None
        if self.loc is None:
            self.wh.log('IGAT WILL PUKE BECAUSE SELF.LOC is NONE; self: ' % self.describe())
        myr = self.loc.r
        myc = self.loc.c
        myrc = (myc, myr)
        mylevel = self.loc.level
        adjlocs = mylevel.area.adj_cells(myc, myr)
        locs = []
        locs.append(myrc)
        locs.extend(adjlocs)
        for loc in locs:
            c,r = loc
            cell = mylevel.grid[r][c]
            for thing in cell.things:
                if self.would_self_attack_this_thing(thing):
                    target = thing
                    return target
        return target
    identify_good_attack_target.assumes = 'self.loc != None and self.loc.level != None'

    def would_self_attack_this_thing(self, thing):
        if self == thing:
            return False
        if isinstance(thing,self.__class__):
            return False
        for enemyclass in self.myenemyclasses:
            if isinstance(thing,enemyclass) and thing.is_alive():
                costumes = thing.get_worn_of_class(Costume)
                if len(costumes) == 1:
                    costume = costumes[0]
                    costume_is_enemy = False
                    for enemyclass in self.myenemyclasses:
                        if isinstance(costume.looks_like_class, enemyclass):
                            costume_is_enemy = True
                    if not costume.is_effective() or costume_is_enemy:
                        return True
                else:
                    return True
        for friendclass in self.myfriendclasses:
            if isinstance(thing,friendclass):
                return False
        for enemy in self.myenemies:
            if thing == enemy:
                return True
        for friend in self.myfriends:
            if thing == friend:
                return False
            
        return False

    def would_you_find_interesting(self):
        return True


class Tree(Lifeform):
    char = 'T'
    charcolor = HtmlColors.DARKGREEN
    basebasedesc = 'tree'
    digests = False
    starves = False

    def __init__(self, wh, mind2use=None):
        Lifeform.__init__(self,wh,mind2use=mind2use)
        self.init_hp((10,20))

    def can_be_picked_up(self):
        return False

    def can_you_pickup_this(self, thing):
        return False

    def should_ai_control_actions(self):
        return False

    def is_capable_of_speech(self):
        return False

    def get_odds_of_rnd_move(self):
        return 0,2

    def would_self_attack_this_thing(self, thing):
        return False

    def is_something_there_you_would_attack(self, loc):
        return False

class GrowingTree(Tree):
    abstract = True
    charcolor = HtmlColors.GREEN
    grow_period = 4
    grow_period_index = 0
    growtype = None
    max_fruit_here_allowed = 8

    def __init__(self, wh):
        Tree.__init__(self,wh)
        self.grow_period_index = rnd_in_range(0, self.grow_period-1)

    def body_tick(self, tick_event):
        if self.loc is None: return
        tock = tick_event.tock
        if tock % self.grow_period == self.grow_period_index:
            qty_already_here = self.wh.geo.count_thingclass_instances_here(self.growtype, self.loc)
            if qty_already_here >= self.max_fruit_here_allowed: return
            f = self.growtype(self.wh)
            self.wh.geo.put_on_map(f, self.loc)
            if self.wh.geo.is_on_same_level_and_within_range(self,self.wh.you,1):
                self.wh.feedback('tree grew %s (%s)' % (f.describe(), self.loc))

class Corpse(Lifeform,Edible):
    char = '%'
    digests = False
    starves = False
    foodvalue_min = 3
    foodvalue_max = 8
    basebasedesc = 'corpse'
    render_importance = 2

    def __init__(self, webhack, origlifeform=None):
        Lifeform.__init__(self,webhack)
        Edible.__init__(self)
        self.init_hp(2)
        self.origlifeform = origlifeform

    def can_be_picked_up(self):
        return True

    def is_alive(self):
        return False

    def full_describe(self, withid=False):
        if self.origlifeform:
            return 'the corpse of %s' % self.origlifeform.describe(withid=withid)
        else: return awordify(self.basebasedesc)
Lifeform.corpseclass = Corpse

###################
# Animals - begin #
###################

class Animal(Lifeform):
    abstract = True
    char = 'a'
    charcolor = HtmlColors.DARKYELLOW
    atkdmg = 1
    basebasedesc = 'animal'

    def __init__(self, webhack):
        Lifeform.__init__(self,webhack,mind2use=AnimalMind(self))
        self.coredesc = self.basebasedesc
        self.init_hp(2)

    def is_capable_of_speech(self):
        return False

    def can_be_picked_up(self):
        return False

    def does_self_block_adding_thing_to_self_cell(self):
        return False

class Dog(Animal):
    char = 'd'
    charcolor = HtmlColors.DARKYELLOW
    basebasedesc = 'dog'

    def __init__(self, webhack):
        Animal.__init__(self,webhack)
        self.coredesc = self.basebasedesc
        self.init_hp((2,5))

#################
# Animals - end #
#################

#######################
# Human Types - begin #
#######################

class Human(Lifeform):
    char = 'P'
    bitesize_max = 5
    basebasedesc = 'person'
    render_importance = 10

    def __init__(self, webhack, gender=None, use_rnd_name=True, mind2use=None):
        if mind2use is None:
            mind2use = HumanMind(self)
        Lifeform.__init__(self,webhack,mind2use=mind2use)
        self.init_hp((3,7))
        if gender is None:
            gender = self.wh.textpools.get_random_entry('genders')
        self.gender = gender
        if use_rnd_name:
            self.name = self.wh.get_rnd_person_name(gender=self.gender)
        self.nationality = self.wh.textpools.get_random_entry('nationalities')
        self.min_sound_volume_heard = 3
        self.haircolor = self.wh.textpools.get_random_entry('hair colors')
        self.race = self.wh.textpools.get_random_entry('races')
        self.birthplace = self.wh.textpools.get_random_entry('cities')
        self.mind_content_load('Human')
        #TODO age, height, weight

    def can_self_eat_this(self, what):
        reason = ''
        results = []

        result1, reason1 = Lifeform.can_self_eat_this(self, what)
        results.append(result1)
        self.wh.debug('1: %s' % result1)
        if not result1:
            reason += reason1

        result2 = not isinstance(what,zh_Zombie)
        results.append(result2)
        self.wh.debug('2: %s' % result2)
        if not result2:
            reason = stradd(reason,' ',"Humans cannot eat zombies!")

        result3 = isinstance(what,Animal) or (not isinstance(what,Animal) and not isinstance(what,Corpse))
        results.append(result3)
        self.wh.debug('3: %s' % result3)
        if not result3:
            reason = stradd(reason,' ',"Humans cannot eat non-animal corpses!")

        result = and_many(results)
        return result, reason

    def he(self):
        return gender2heshe(self.gender)

    def him(self):
        return gender2himher(self.gender)

    def his(self):
        return gender2hishers(self.gender)

    def does_self_block_adding_thing_to_self_cell(self):
        return True

    def statedump(self):
        return Lifeform.statedump(self) #TODO

    def understands_speech(self):
        return True

    def desc_human_traits(self):
        haircolor_blurb = ''
        if self.race not in ('black','asian','hispanic','Native American'):
            haircolor_blurb = '%s ' % self.haircolor
        s = '%s%s %s born in %s' % (haircolor_blurb, self.race, self.gender, self.birthplace)
        return s

    def can_be_picked_up(self):
        return False

    def is_capable_of_speech(self):
        return self.is_alive()

    def get_odds_of_rnd_move(self):
        return 1,2 # 50% chance is default

    def describe(self, withid=False):
        s = Thing.describe(self,withid)
        if self.name is not None:
            s += ' named %s' % self.name
        return s

    def full_describe(self, withid=False):
        what = awordify(self.desc_human_traits())
        whois = 'who is'
        if not self.is_alive():
            whois = 'that was once'
        return '%s, %s %s' % (self.describe(withid), whois, what)

class HumanCorpse(Human,Corpse):
    char = '%'
    foodvalue_min = 2
    foodvalue_max = 5
    basebasedesc = 'human corpse'
    render_importance = Corpse.render_importance + 1

    def __init__(self, webhack, orighuman=None):
        Human.__init__(self,webhack)
        self.name = None
        Corpse.__init__(self,webhack,orighuman)

    def get_render_importance(self):
        ri = Corpse.get_render_importance(self)
        lloc = 'in inventory'
        if self.loc is not None:
            lloc = 'at %s,%s' % (self.loc.r, self.loc.c)
        self.wh.log('HumanCorpse %s %s get_render_importance(): %s' % (self.describe(), lloc, ri))
        return ri

    def can_be_picked_up(self):
        return Corpse.can_be_picked_up(self)

    def does_self_block_adding_thing_to_self_cell(self):
        return Corpse.does_self_block_adding_thing_to_self_cell(self)

    def is_alive(self):
        return False

    def full_describe(self, withid=False):
        if self.origlifeform:
            s = awordify(self.origlifeform.desc_human_traits())
            return 'the corpse of %s' % s
        else: return Corpse.full_describe(self,withid)
Human.corpseclass = HumanCorpse

class AnimalCorpse(Animal,Corpse):
    char = '%'
    foodvalue_min = 2
    foodvalue_max = 5
    basebasedesc = 'animal corpse'

    def __init__(self, webhack, origlifeform=None):
        Animal.__init__(self,webhack)
        self.name = None
        Corpse.__init__(self,webhack,origlifeform)

    def get_render_importance(self):
        return Corpse.get_render_importance(self)

    def can_be_picked_up(self):
        return Corpse.can_be_picked_up(self)

    def does_self_block_adding_thing_to_self_cell(self):
        return Corpse.does_self_block_adding_thing_to_self_cell(self)

    def is_alive(self):
        return False

    def full_describe(self, withid=False):
        return Corpse.full_describe(self,withid=withid)
Animal.corpseclass = AnimalCorpse

class American(Human):
    def __init__(self, wh):
        Human.__init__(self,wh)
        self.nationality = 'American'
        self.basebasedesc = self.nationality
        self.name = self.wh.get_rnd_person_name(nationality=self.nationality,gender=self.gender)
        self.mind_content_load('American')
        self.wh.ai.sk.add_skills_from_bundle(self,'American citizen')

    def statedump(self):
        return Human.statedump(self) #TODO

class Scientist(Human):
    char = 'S'
    def __init__(self, wh, use_rnd_name=True, gender=None):
        Human.__init__(self,wh,use_rnd_name=use_rnd_name,mind2use=ScientistMind(self),gender=gender)
        self.basebasedesc = 'scientist'
        self.mind_content_load('Scientist')
        self.wh.ai.sk.add_skills_from_bundle(self,'scientist')

class VictorVenturius(Scientist):
    char = 'V'
    def __init__(self, wh):
        Scientist.__init__(self,wh,use_rnd_name=False,gender='male')
        self.name = 'Victor Venturius'
        self.mind_content_load('Venturius',subdir='zombiehack/')
        #TODO custom speech file with cool Venturius quotes

class HeinrichHexenhammer(Scientist):
    char = 'V'
    def __init__(self, wh):
        Scientist.__init__(self,wh,use_rnd_name=False,gender='male')
        self.name = 'Dr. Heinrich von Hexenhammer'
        self.mind_content_load('Hexenhammer',subdir='zombiehack/')
        #TODO custom speech file with cool Hexenhammer quotes

class Doctor(Human):
    char = 'D'
    def __init__(self, wh):
        Human.__init__(self,wh)
        self.basebasedesc = 'doctor'
        self.wh.ai.sk.add_skills_from_bundle(self,'doctor')

class Soldier(Human):
    char = 'A'
    def __init__(self, wh):
        Human.__init__(self,wh)
        self.basebasedesc = 'soldier'

class You(American):
    digests = True
    starves = True
    char = '@'
    charcolor = HtmlColors.YOU
    render_importance = 9999
    atkhitchance = (3,4)

    def __init__(self, webhack):
        American.__init__(self,webhack)
        self.wh.ai.mem.clear_memories(self)
        self.wh.ai.th.clear_thoughts(self)
        self.wh.ai.be.clear_beliefs(self)
        self.basebasedesc = 'you'
        self.clear_speech()
        self.name = None
        self.haircolor = 'blonde'
        self.race = 'white'
        self.gender = 'male'
        self.init_hp((6,8))
        #NOTE: goals format is [goal1, goal2, ...]
        #NOTE: goal format is (desc,check-is-goal-satisfied-currently-fn-name,whether-ever-satisifed)
        #NOTE: the check fn is assumed to be a method of the wh instance
        survival_goal = ('Stay alive.','is_goal_satisfied_you_stay_alive',True)
        self.goals = [survival_goal,]

    def does_always_hit(self):
        return American.does_always_hit(self) or (self is self.wh.you and self.wh.cfg('you_always_hit'))

    def does_always_do_kill_dmg(self):
        return American.does_always_do_kill_dmg(self) or (self is self.wh.you and self.wh.cfg('you_always_do_kill_dmg'))

    def get_basedesc(self):
        return self.basebasedesc

    def statedump(self):
        s = []
        app(s, American.statedump(self))
        app(s, ' name:%s hp:%s basedesc:"%s" goals:%s' % (self.name, self.hp, self.get_basedesc(), self.goals))
        return ''.join(s)

    def should_ai_control_actions(self):
        return False

    def is_invuln(self):
        return American.is_invuln(self) or self.wh.cfg('you_invuln')

    def sound_reaches_self(self, sound_event):
        event = sound_event
        can_hear, reasons = self.can_hear_this_sound_right_now(event)
        if can_hear or self.wh.cfg('you_hear_all') or (not can_hear and ('because dead' in reasons)): # Yes, you can hear things when you're dead. You'll get used to it.
            who = event.who
            whatsaid = event.whatsaid
            if len(whatsaid) > 1 and whatsaid.endswith('.') and not whatsaid.endswith('...'):
                sz = len(whatsaid)
                whatsaid = whatsaid[:sz-1] + ','
            whodesc = who.describe()
            if whodesc.startswith('The'):
                whodesc = 't' + whodesc[1:]
            #TODO indicate rough rel direction of sound origin loc
            said = 'said'
            if event.type == SoundEvent.YELL_TYPE:
                said = 'yelled'
            if who == self:
                whatsaid = sentence(whatsaid)
                whatsaidbywho = 'You %s "%s"' % (said, whatsaid)
            else:
                whatsaidbywho = '"%s" %s %s.' % (whatsaid, said, whodesc)
            self.wh.feedback(whatsaidbywho)
        else:
            self.wh.log('YOU CANT HEAR THIS: %s' % event)

    def think_this_interesting(self, thing):
        return thing.would_you_find_interesting()

    def would_you_find_interesting(self):
        return False

    def is_capable_of_random_speech_by_ai(self):
        return False

    def would_say_something_aloud_randomly_now(self):
        return False

    def would_self_attack_this_thing(self, thing):
        if isinstance_any(thing,(Lifeform,Door,Window,Barricade,Wall)): return True
        else: return Human.would_self_attack_this_thing(self,thing)

    def __str__(self):
        return self.get_basedesc()

class YouCorpse(You,HumanCorpse):
    char = '%'
    charcolor = You.charcolor
    basebasedesc = 'corpse'
    render_importance = HumanCorpse.render_importance + 1
    #TODO find out what order superclass method impls would be called in if 2+ superclasses gave me methods of the same name -- which one would be called by default? first in list? last? if I knew the order and it was stable, then I could delete some of the method impls in this class which merely pass the call on to the particular superclass method I want to have called; instead, I could rely on the inheritance order, for example

    def __init__(self, webhack, you):
        You.__init__(self,webhack)
        HumanCorpse.__init__(self,webhack,you)

    def get_render_importance(self):
        You.get_render_importance(self)

    def get_basedesc(self):
        return 'your corpse'

    def is_invuln(self):
        HumanCorpse.is_invuln(self)

    def does_self_block_adding_thing_to_self_cell(self):
        return HumanCorpse.does_self_block_adding_thing_to_self_cell(self)

    def is_alive(self):
        return HumanCorpse.is_alive(self)
You.corpseclass = YouCorpse

#####################
# Human Types - end #
#####################

##########################
# Building Types - begin #
##########################

class Wall(Thing):
    char = '#'
    render_importance = 5

    def __init__(self, webhack):
        Thing.__init__(self,webhack)
        self.basebasedesc = 'wall'
        self.init_hp(100)

    def can_be_picked_up(self):
        return False

    def does_self_block_adding_thing_to_self_cell(self):
        return True

    def would_you_find_interesting(self):
        return False

class Barricade(Thing):
    char = '#'
    layout_char = 'B'
    render_importance = 5
    charcolor = HtmlColors.DARKYELLOW

    def __init__(self, webhack):
        Thing.__init__(self,webhack)
        self.basebasedesc = 'barricade'
        self.init_hp(25)

    def can_be_picked_up(self):
        return False

    def does_self_block_adding_thing_to_self_cell(self):
        return True

    def would_you_find_interesting(self):
        return False

class Door(Thing,IsOpenCloseable):
    char = '+'
    render_importance = 6

    def __init__(self, webhack):
        Thing.__init__(self,webhack)
        IsOpenCloseable.__init__(self)
        self.basebasedesc = 'door'
        self.init_hp(20)

    def can_be_picked_up(self):
        return False

    def would_you_find_interesting(self):
        return True

    def does_self_block_adding_thing_to_self_cell(self):
        return not self.opened

    def render_char(self):
        ch, color = Thing.render_char(self)
        if self.opened: return 'O', color
        else: return '+', color

    def get_render_importance(self):
        corpseclasses = get_instantiable_thing_classes(globals(),Corpse)
        ris = [cl.render_importance for cl in corpseclasses if hasattr(cl,'render_importance')]
        if not self.opened:
            ri = max(ris) + 1
            self.wh.log('closed Door get_render_importance() %s' % ri)
            return ri
        else:
            ri = min(ris) - 1
            if ri < 0: ri = 0
            self.wh.log('open Door get_render_importance() %s' % ri)
            return ri

class Window(Thing):
    char = '0'

    def __init__(self, webhack):
        Thing.__init__(self,webhack)
        self.broken = False
        self.basebasedesc = 'window'
        self.init_hp(2)

    def can_be_picked_up(self):
        return False

    def would_you_find_interesting(self):
        return True

    def does_self_block_adding_thing_to_self_cell(self):
        return not self.broken

    def render_char(self):
        ch, color = Thing.render_char(self)
        if self.broken: return 'O', color
        else: return '0', color

class Stairway(Thing):
    char = 'S'
    UP = 'up'
    DOWN = 'down'
    DIRECTIONS = ('up','down')

    def __init__(self, wh, selfloc, destloc, direction):
        Thing.__init__(self,wh)
        assert selfloc is not None
        assert destloc is not None
        assert direction in Stairway.DIRECTIONS
        #TODO if Thing has loc field already, then get rid of selfloc here:
        self.render_importance = 6
        self.selfloc = selfloc
        self.destloc = destloc.clone()
        if direction == Stairway.UP: self.char = '<'
        elif direction == Stairway.DOWN: self.char = '>'
        self.direction = direction
        self.basebasedesc = 'stairway'
        self.init_hp(40)
        #TODO thing instance's render char should depend on self.dir: > or <
        self.wh.ev.add_listener((StairsRequest, {'stairway':self}), self, 'execute_stairs')

    def get_basedesc(self):
        return '%s %s' % (awordify(self.direction), self.basebasedesc)

    def __str__(self):
        return 'some stairway'
        #s = 'Stairway %s at %s to %s' % (self.id_thing(), self.selfloc, self.destloc)
        #return s

    def can_be_picked_up(self):
        return False

    def execute_stairs(self, stairs_event):
        event = stairs_event
        who = event.who
        direction = event.direction
        self.wh.geo.move_this_from_here_to_there(who, self.destloc, movedesc='stairway travelling')
        s = who.describe() + ' took the stairs '+direction+' to another floor'
        self.wh.feedbacksen(s)

class Route(Thing):
    char = '/'

    def __init__(self, wh, selfloc, destloc, destdesc=None):
        Thing.__init__(self,wh)
        assert selfloc is not None
        assert destloc is not None
        #TODO if Thing has loc field already, then get rid of selfloc here:
        self.render_importance = 6
        self.selfloc = selfloc
        self.destloc = destloc.clone()
        self.destdesc = destdesc
        self.basebasedesc = 'route'
        self.init_hp(9999) #TODO should be indestructible, just blockable
        #TODO thing instance's render char should depend on self.dir: > or <
        self.wh.ev.add_listener((RouteRequest, {'route':self}), self, 'execute_route')

    def __str__(self):
        return self.get_basedesc()

    def get_basedesc(self):
        return 'a path to %s' % self.get_destdesc()

    def get_destdesc(self):
        destdesc = self.destloc.region.name
        if self.destdesc is not None:
            destdesc = self.destdesc
        return destdesc

    def can_be_picked_up(self):
        return False

    def execute_route(self, route_event):
        debug('execute_route')
        event = route_event
        who = event.who
        self.wh.geo.move_this_from_here_to_there(who, self.destloc, movedesc='route travelling')
        self.wh.make_you_level_active_and_focus_ui()
        self.wh.update_seen_cells()
        s = who.describe() + ' took the path to %s' % self.get_destdesc()
        self.wh.feedbacksen(s)

class Teleporter(Thing):
    char = 'T'
    invis = True
    devmode_only_tp = False
    devmode_only_vis = True

    def __init__(self, webhack, selfloc, tptargetloc, movedesc=None, msg=None):
        Thing.__init__(self,webhack)
        self.basebasedesc = 'teleporter'
        if msg is None:
            self.msg = ' teleported somewhere!'
        else: self.msg = msg
        if movedesc is None:
            self.movedesc = 'teleporting'
        else: self.movedesc = movedesc
        self.tptargetloc = tptargetloc.clone()
        self.mylistenerreceipt = self.wh.ev.add_listener(
            (ThingEntersCellEvent, {'level':selfloc.level,'r':selfloc.r,'c':selfloc.c} ),
            self, 'fire')

    def cleanup(self): #TODO called when this thing is removed from world
        self.wh.ev.remove_listener(self.mylistenerreceipt)

    def can_be_picked_up(self):
        return False

    def fire(self, thing_enters_cell_event):
        if self.devmode_only_tp and not self.wh.cfg('devmode'):
            return
        event = thing_enters_cell_event
        thing = event.thing
        self.wh.geo.move_this_from_here_to_there(thing, self.tptargetloc, movedesc=self.movedesc)
        s = sentence(thing.describe() + self.msg)
        self.wh.feedback(s)

    def is_invisible(self):
        if self.wh.cfg('devmode'):
            if self.devmode_only_vis:
                return False
        else: return self.invis

########################
# Building Types - end #
########################


####################################
# Weapons, Gadgets & Tools - begin #
####################################

class Weapon(Thing,RndStuff):
    abstract = True
    max_dmg = 1

    def __init__(self, webhack):
        assertNotDirectInstantiate(self,Weapon)
        Thing.__init__(self, webhack)

    def is_wieldable(self):
        return True

    def get_max_dmg(self):
        return self.max_dmg

class BaseballBat(Weapon):
    char = '!'
    max_dmg = 2
    basebasedesc = 'baseball bat'

class Knife(Weapon):
    char = 'k'
    max_dmg = 2
    basebasedesc = 'knife'

class Chainsaw(Weapon):
    char = '!'
    max_dmg = 6
    color = HtmlColors.GRAY
    basebasedesc = 'chainsaw'

class Gun(Weapon):
    char = 'g'
    max_dmg = 4
    basebasedesc = 'gun'

##################################
# Weapons, Gadgets & Tools - end #
##################################


#########################
# Healing Items - begin #
#########################

class HealItem(Thing,Useable,RndStuff):
    char = '%'
    abstract = True
    charcolor = HtmlColors.GREEN
    basebasedesc = 'healitem'
    heal_amount = 1
    uses_left = 1

    def __init__(self, webhack):
        assertNotDirectInstantiate(self,HealItem)
        Thing.__init__(self,webhack)
        Useable.__init__(self)

    def use_by(self, user):
        if self.uses_left == 0:
            return 'could not use the %s because it had no uses left.' % self.basebasedesc
        if user.hp == user.hp_max:
            return 'did not use the %s because it would have been pointless.' % self.basebasedesc

        amount = min(self.heal_amount, user.hp_max - user.hp)
        user.hp += amount
        self.uses_left -= 1
        return 'used the %s, healing %s HP. It now has %s uses left.' % (self.basebasedesc, amount, self.uses_left)

    def full_describe(self, withid=False):
        return '%s (%s uses left)' % (Thing.describe(self,withid), self.uses_left)

class FirstAidKit(HealItem):
    basebasedesc = 'first aid kit'
    heal_amount = 2
    uses_left = 5

class Bandages(HealItem):
    basebasedesc = 'bandages'
    heal_amount = 1
    uses_left = 3

class Medicine(HealItem):
    basebasedesc = 'medicine'
    heal_amount = 4
    uses_left = 2

#######################
# Healing Items - end #
#######################

################
# Food - begin #
################

class Food(Thing,Edible,RndStuff):
    char = '%'
    abstract = True
    color = HtmlColors.DARKYELLOW
    basebasedesc = 'food'

    def __init__(self, webhack):
        assertNotDirectInstantiate(self, Food)
        Thing.__init__(self,webhack)
        Edible.__init__(self)

    def full_describe(self, withid=False):
        return '%s (%s)' % (Thing.describe(self,withid), self.describe_foodvalue())

class Bread(Food):
    foodvalue_min = 8
    foodvalue_max = 20
    basebasedesc = 'bread'

class Cheese(Food):
    foodvalue_min = 8
    foodvalue_max = 12
    basebasedesc = 'cheese'

class Milk(Food):
    foodvalue_min = 4
    foodvalue_max = 8
    basebasedesc = 'milk'

class Cookie(Food):
    foodvalue_min = 4
    foodvalue_max = 32
    basebasedesc = 'cookie'

class CandyBar(Food):
    foodvalue_min = 8
    foodvalue_max = 16
    basebasedesc = 'candy bar'

class Crackers(Food):
    foodvalue_min = 4
    foodvalue_max = 16
    basebasedesc = 'crackers'

class ShreddedWheat(Food):
    foodvalue_min = 8
    foodvalue_max = 36
    basebasedesc = 'shredded wheat'

class Vegetables(Food):
    foodvalue_min = 4
    foodvalue_max = 16
    basebasedesc = 'vegetables'

class Fruit(Food):
    foodvalue_min = 4
    foodvalue_max = 32
    basebasedesc = 'fruit'
    charcolor = HtmlColors.ORANGE

##############
# Food - end #
##############

##############################
# Food-Growing Trees - begin #
##############################

class FruitTree(GrowingTree):
    growtype = Fruit
    charcolor = HtmlColors.ORANGE
    basebasedesc = 'fruit tree'
    grow_period = 8

############################
# Food-Growing Trees - end #
############################

#####################################
# Readable Stuff Like Books - begin #
#####################################

class Readable:
    bodytext = ''

    def read_body(self):
        return self.bodytext

class Book(Thing,Readable,RndStuff):
    char = 'b'
    basebasedesc = 'book'
    title = 'The Definitive Non-Illustrated Guide to Something'
    bodytext = 'Blah. Blah blah blah. Blah blah blah blah blah. The End.'

    def __init__(self, webhack):
        Thing.__init__(self,webhack)

class Flyer(Thing,Readable,RndStuff):
    char = 'f'
    basebasedesc = 'flyer'
    textchoices = (\
        'Save the whales. Feed the kittens. Kittens like whale meat.',
        'SUPER SALE! EVERYTHING MUST GO! BRING THIS TO YOUR CLOSEST LOCATION FOR 20% OFF! NOT AVAILABLE IN ALL LOCATIONS. MAY EXPIRE AT ANY TIME. ILLEGAL IN SOME STATES. NO CLAIMS EXPRESSED OR IMPLIED. DOES NOT CONSTRUE LEGAL ADVICE. CONSULT YOUR DOCTOR.',
        )

    def __init__(self, webhack, bodytext=None):
        Thing.__init__(self,webhack)
        if bodytext is not None:
            self.bodytext = bodytext
        else:
            self.bodytext = random.choice(self.textchoices)

class Letter(Thing,Readable):
    char = 'l'
    basebasedesc = 'letter'
    bodytext = 'Dear Sir or Madam, it has come to our attention that... (the rest is pretty boring so you stop reading)'

    def __init__(self, webhack, bodytext=None):
        Thing.__init__(self,webhack)
        if bodytext is not None:
            self.bodytext = bodytext

class Note(Thing,Readable):
    char = 'n'
    basebasedesc = 'note'
    def __init__(self, webhack, bodytext=None):
        Thing.__init__(self,webhack)
        if bodytext is not None:
            self.bodytext = bodytext

###################################
# Readable Stuff Like Books - end #
###################################

####################
# Clothing - begin #
####################

class Clothing(Thing,HasColor):
    abstract = True
    char = 'c'

    def __init__(self, webhack):
        assertNotDirectInstantiate(self,Clothing)
        Thing.__init__(self,webhack)
        self.basebasedesc = 'article of clothing'
        #TODO size, logo, artwork, male/female
        #TODO by default, if no color param given, pick a color at random from list/set of all possible colors

    def is_wearable(self):
        return True

    def is_unwearable(self):
        return True

    def is_wieldable(self):
        return False

class RndClothing(Clothing,HasColor,RndStuff):
    abstract = True
    char = 'c'
    color = HtmlColors.BROWN

    def __init__(self, webhack, color=None):
        assertNotDirectInstantiate(self,RndClothing)
        Clothing.__init__(self,webhack)
        HasColor.__init__(self,webhack,color=color)

    def get_basedesc(self):
        pre = awordify(self.get_color())
        s = '%s %s' % (pre, self.basebasedesc)
        return s

class Hat(RndClothing):
    def __init__(self, webhack):
        RndClothing.__init__(self,webhack)
        self.basebasedesc = 'hat'
class_prep(Hat,'h')

class Helmet(RndClothing):
    def __init__(self, webhack,color=None):
        RndClothing.__init__(self,webhack,color)
        self.basebasedesc = 'helmet'
class_prep(Helmet,'h')

class EyeGlasses(RndClothing):
    def __init__(self, webhack):
        RndClothing.__init__(self,webhack)
        self.basebasedesc = 'eye glasses'
class_prep(EyeGlasses,'g')

class SunGlasses(RndClothing):
    def __init__(self, webhack):
        RndClothing.__init__(self,webhack)
        self.basebasedesc = 'sun glasses'
class_prep(SunGlasses,'g')

class Goggles(RndClothing):
    def __init__(self, webhack):
        RndClothing.__init__(self,webhack)
        self.basebasedesc = 'goggles'
class_prep(Goggles,'g')

class Scarf(RndClothing):
    def __init__(self, webhack):
        RndClothing.__init__(self,webhack)
        self.basebasedesc = 'scarf'
class_prep(Scarf,'s')

class EarMuffs(RndClothing):
    def __init__(self, webhack):
        RndClothing.__init__(self,webhack)
        self.basebasedesc = 'ear muffs'
class_prep(EarMuffs,'e')

class EarPlugs(RndClothing):
    def __init__(self, webhack):
        RndClothing.__init__(self,webhack)
        self.basebasedesc = 'ear plugs'
class_prep(EarPlugs,'e')

class NosePlugs(RndClothing):
    def __init__(self, webhack):
        RndClothing.__init__(self,webhack)
        self.basebasedesc = 'nose plugs'
class_prep(NosePlugs,'n')

class AirMask(RndClothing):
    def __init__(self, webhack):
        RndClothing.__init__(self,webhack)
        self.basebasedesc = 'air mask'
class_prep(AirMask,'a')

class Mask(RndClothing):
    def __init__(self, webhack):
        RndClothing.__init__(self,webhack)
        self.basebasedesc = 'mask'
class_prep(Mask,'m')

class NeckTie(RndClothing):
    def __init__(self, webhack):
        RndClothing.__init__(self,webhack)
        self.basebasedesc = 'neck tie'
class_prep(NeckTie,'t')

class Coat(RndClothing):
    dmg_absorption = 1

    def __init__(self, webhack,color=None):
        RndClothing.__init__(self,webhack,color)
        self.basebasedesc = 'coat'
class_prep(Coat,'c')

class LeatherJacket(RndClothing):
    char = 'j'
    color = HtmlColors.BROWN
    dmg_absorption = 2

    def __init__(self, webhack):
        RndClothing.__init__(self,webhack)
        self.basebasedesc = 'leather jacket'
class_prep(LeatherJacket)

class Vest(RndClothing):
    def __init__(self, webhack):
        RndClothing.__init__(self,webhack)
        self.basebasedesc = 'vest'
class_prep(Vest,'v')

class Shirt(RndClothing):
    def __init__(self, webhack):
        RndClothing.__init__(self,webhack)
        self.basebasedesc = 'shirt'
class_prep(Shirt,'s')

class Belt(RndClothing):
    def __init__(self, webhack):
        RndClothing.__init__(self,webhack)
        self.basebasedesc = 'belt'

    def is_wieldable(self):
        return True
class_prep(Belt,'b')

class Suspenders(RndClothing):
    def __init__(self, webhack):
        RndClothing.__init__(self,webhack)
        self.basebasedesc = 'suspenders'
class_prep(Suspenders,'s')

class Pants(RndClothing):
    def __init__(self, webhack, color=None):
        RndClothing.__init__(self,webhack,color)
        self.basebasedesc = 'pants'
class_prep(Pants,'p')

class Jeans(RndClothing):
    def __init__(self, webhack):
        RndClothing.__init__(self,webhack)
        self.basebasedesc = 'jeans'
class_prep(Jeans,'j')

class Skirt(RndClothing):
    def __init__(self, webhack):
        RndClothing.__init__(self,webhack)
        self.basebasedesc = 'skirt'
class_prep(Skirt,'s')

class MiniSkirt(RndClothing):
    def __init__(self, webhack):
        RndClothing.__init__(self,webhack)
        self.basebasedesc = 'mini-skirt'
class_prep(MiniSkirt,'s')

class Dress(RndClothing):
    def __init__(self, webhack):
        RndClothing.__init__(self,webhack)
        self.basebasedesc = 'dress'
class_prep(Dress,'d')

class Shorts(RndClothing):
    def __init__(self, webhack):
        RndClothing.__init__(self,webhack)
        self.basebasedesc = 'shorts'
class_prep(Shorts,'s')

class Bikini(RndClothing):
    def __init__(self, webhack):
        RndClothing.__init__(self,webhack)
        self.basebasedesc = 'bikini'
class_prep(Bikini,'b')

class Socks(RndClothing):
    def __init__(self, webhack):
        RndClothing.__init__(self,webhack)
        self.basebasedesc = 'socks'
class_prep(Socks,'s')

class Shoes(RndClothing):
    def __init__(self, webhack):
        RndClothing.__init__(self,webhack)
        self.basebasedesc = 'shoes'
class_prep(Shoes,'s')

class Sandals(RndClothing):
    def __init__(self, webhack):
        RndClothing.__init__(self,webhack)
        self.basebasedesc = 'sandals'
class_prep(Sandals,'s')

class HighHeels(RndClothing):
    def __init__(self, webhack):
        RndClothing.__init__(self,webhack)
        self.basebasedesc = 'high heels'
class_prep(HighHeels,'h')

class Boots(RndClothing):
    def __init__(self, webhack, color=None):
        RndClothing.__init__(self,webhack,color)
        self.basebasedesc = 'boots'
class_prep(Boots,'b')

class Costume(Clothing):
    abstract = True
    looks_like_class = None
    fidelity = 100 # loses 1 per tock when worn; when reaches 0 it no longer fools zombies
    def __init__(self, webhack):
        assertNotDirectInstantiate(self,Costume)
        Clothing.__init__(self,webhack)
        self.basebasedesc = 'costume'

    def get_symbol_shown_on_map_when_worn(self):
        return self.looks_like_class and self.looks_like_class.char or None

    def is_effective(self):
        return self.fidelity > 0

    def full_describe(self, withid=False):
        return '%s (fidelity %i)' % (Costume.describe(self,withid), self.fidelity)
class_prep(Costume,'z')

class ZombieCostume(Costume):
    looks_like_class = None #NOTE we set this after the zh_Zombie class def
    def __init__(self, webhack):
        Costume.__init__(self,webhack)
        self.basebasedesc = 'zombie costume'
    #def get_symbol_shown_on_map_when_worn(self):
    #    return self.looks_like_class.char
class_prep(ZombieCostume,'z')

##################
# Clothing - end #
##################

#################
# Money - start #
#################

class Money(Thing):
    abstract = True
    char = '$'
    charcolor = HtmlColors.MONEY

    def __init__(self, webhack, amount=1, rnd_amount=False, type='dollar'):
        Thing.__init__(self,webhack)
        self.basebasedesc = 'money'
        if rnd_amount:
            min = rnd_amount['min']
            max = rnd_amount['max']
            self.amount = rnd_in_range(min,max)
        else:
            self.amount = amount
        self.type = type
        self.describe_template = '%s %s%s'

    def get_basedesc(self):
        return 'some money'

    def pluralize_type_for_amount(self):
        if self.amount == 1: return self.type
        else: return self.type + 's'

    def describe(self, withid=False):
        idstr = self.withid_helper(withid)
        return self.describe_template % (self.amount, self.pluralize_type_for_amount(), idstr)

class USDollar(Money,RndStuff):
    charcolor = HtmlColors.USDOLLAR

    def __init__(self, webhack, amount=1, rnd_amount=False):
        Money.__init__(self,webhack,amount,rnd_amount,type='dollar')
        self.basebasedesc = 'US dollars'

    def get_basedesc(self):
        return 'some %s' % self.basebasedesc

class GoldCoin(Money):
    charcolor = HtmlColors.GOLDCOIN

    def __init__(self, webhack, amount=1, rnd_amount=False):
        Money.__init__(self,webhack,amount,rnd_amount,type='gold coin')
        self.basebasedesc = 'gold coinage'

    def get_basedesc(self):
        return 'some %s' % self.basebasedesc

###############
# Money - end #
###############

class Flare(Thing):
    char = 'f'
    charcolor = Colors.FG

    def __init__(self, webhack, lit=False):
        Thing.__init__(self,webhack)
        self.basebasedesc = 'flare'
        self.lit = lit

    def get_basedesc(self):
        return 'a %s%s' % ((self.lit and 'lit ' or ''), self.basebasedesc)


#######################
# Thing Classes - end #
#######################

##################
# Events - begin #
##################

# NOTE: TickEvent defined in event_system.py and imported into here

class AttackAttempt(Event):
    SKILLS = (Skills.HAND_TO_HAND,)
    def __init__(self, who, target, skill=Skills.HAND_TO_HAND):
        Event.__init__(self)
        assertNotNone('who', who)
        assertNotNone('target', target)
        assertNotNone('skill', skill)
        #assert skill in AttackAttempt.SKILLS, 'skill ctor param was %s but must be in %s' % (skill, AttackAttempt.SKILLS)
        #TODO assert that skill is of recognize/allowed type/value
        self.who = who
        self.target = target
        self.skill = skill

class DeathEvent(Event):
    def __init__(self, who, where):
        Event.__init__(self)
        assertNotNone('who', who)
        assertNotNone('where', where) #TODO valid where fields and coords too
        Location.assertFullyPopulatedAndValid(where)
        self.who = who
        self.where = where

class DestroyedEvent(Event):
    def __init__(self, what, where):
        Event.__init__(self)
        assertNotNone('what', what)
        assertNotNone('where', where) #TODO valid where fields and coords too
        Location.assertFullyPopulatedAndValid(where)
        self.what = what
        self.where = where

class DropRequest(Event):
    #TODO elim need for this event class! it's not a real event! I'm just using it as a bundle of params to pass to the execute_drop method (in essence, except asynch rather than sync, which is uncessary)
    def __init__(self, who, where, what='all'):
        Event.__init__(self)
        assertNotNone('who', who)
        assertNotNone('where', where)
        Location.assertFullyPopulatedAndValid(where)
        assertNotNone('what', what)
        assert what == 'all' or isinstance(what,Thing), "ctor param 'what' must be either 'all' or a Thing instance"
        self.who = who
        self.where = where
        self.what = what
        log('DropRequest() built with where: %s' % where)

class DroppedEvent(Event):
    def __init__(self, what, bywho, where):
        Event.__init__(self)
        assertNotNone('what', what)
        assertNotNone('bywho', bywho)
        assertNotNone('where', where)
        Location.assertFullyPopulatedAndValid(where)
        self.what = what
        self.bywho = bywho
        self.where = where

class FeedbackDeferred(Event):
    def __init__(self, msg):
        Event.__init__(self)
        assertNotNone('msg', msg)
        assert len(str(msg)) > 0, 'ctor param msg len must be > 0'
        self.msg = msg

class MoveRequest(Event):
    #TODO consider making 2 subclasses, one for abs dest and one for rel dest
    def __init__(self, thing, r=None, c=None, relrow=None, relcol=None, level=None, region=None):
        #TODO I don't think these params are used anymore so consider dropping them from this event class and from execute_move(): relrow, relcol, level, region
        #TODO assert that either both r & c are not None, or, that relrow & relcol are not None (and one group cannot be given/not-None if the other is)
        Event.__init__(self)
        assertNotNone('thing', thing)
        #TODO make asserts about location param combos that must be given
        self.thing = thing
        self.r = r
        self.c = c
        self.relrow = relrow
        self.relcol = relcol
        self.level = level
        self.region = region

class PickUpRequest(Event):
    def __init__(self, who, what='all'):
        Event.__init__(self)
        assertNotNone('who', who)
        assertNotNone('what', what)
        assert what == 'all' or isinstance(what,Thing), "ctor param 'what' must be either 'all' or a Thing instance"
        self.who = who
        self.what = what
        
class PickedUpEvent(Event):
    def __init__(self, what, bywho, thingwaswhere):
        Event.__init__(self)
        assertNotNone('what', what)
        assertNotNone('bywho', bywho)
        assertNotNone('thingwaswhere', thingwaswhere)
        Location.assertFullyPopulatedAndValid(thingwaswhere)
        self.what = what
        self.bywho = bywho
        self.thingwaswhere = thingwaswhere

class RouteRequest(Event):
    def __init__(self, who, route):
        Event.__init__(self)
        assertNotNone('who', who)
        assertNotNone('route', route)
        self.who = who
        self.route = route

class SoundEvent(Event):
    # SoundEvent.type values allowed:
    YELL_TYPE = 'yell'
    SPEECH_TYPE = 'speech'
    SOUND_TYPES = (YELL_TYPE, SPEECH_TYPE)

    #TODO consider making 2+ subclasses, with 1 for speech only
    def __init__(self, who, where, whatsaid, volume, type, language=None):
        Event.__init__(self)
        assertNotNone('who', who)
        assertNotNone('where', where)
        Location.assertFullyPopulatedAndValid(where)
        assertNotNone('whatsaid', whatsaid)
        assert len(str(whatsaid)) > 0, "ctor param 'whatsaid' str len must be > 0'"
        assertNotNone('volume', volume)
        assertNotNone('type', type)
        assert type in SoundEvent.SOUND_TYPES, "ctor param 'type' value '%s' is not in SOUND_TYPES %s" % (type, SoundEvent.SOUND_TYPES)
        self.who = who
        self.where = where
        self.whatsaid = whatsaid
        self.volume = volume
        self.type = type
        self.language = language

class SpeechEvent(SoundEvent):
    def __init__(self, who, where, whatsaid, volume, language=None, type=SoundEvent.SPEECH_TYPE):
        SoundEvent.__init__(self, who, where, whatsaid, volume, type, language)

class StairsRequest(Event):
    def __init__(self, who, direction, stairway):
        Event.__init__(self)
        assertNotNone('who', who)
        assertNotNone('direction', direction)
        assert direction in Stairway.DIRECTIONS, 'ctor param direction value must be one of %s; was: %s' % (Stairway.DIRECTIONS, direction)
        assertNotNone('stairway', stairway)
        self.who = who
        self.direction = direction
        self.stairway = stairway

class TestPlotEvent(Event):
    def __init__(self):
        Event.__init__(self)

class IdentifyActiveAgentEvent(Event): pass
class IsolateTheGeneEvent(Event): pass
class MapTheThingEvent(Event): pass
class IndexTheThingEvent(Event): pass
class DesignManufactureProcessEvent(Event): pass
class SetupFactoryEvent(Event): pass
class ArrangeDistroMethodEvent(Event): pass

class ThingEntersCellEvent(Event):
    #TODO: consider replacing r/c/reg/level params with a single 'loc' param
    def __init__(self, thing, region, level, r, c):
        Event.__init__(self)
        assertNotNone('thing', thing)
        assertNotNone('region', region)
        assertNotNone('level', level)
        assertNotNone('r', r)
        assertNotNone('c', c)
        self.thing = thing
        self.region = region
        self.level = level
        self.r = r
        self.c = c

class ThingRemovedFromMapEvent(Event):
    #TODO consider replacing reg/level/r/c with loc
    def __init__(self, thing, region, level, r, c):
        Event.__init__(self)
        assertNotNone('thing', thing)
        assertNotNone('region', region)
        assertNotNone('level', level)
        assertNotNone('r', r)
        assertNotNone('c', c)
        self.thing = thing
        self.region = region
        self.level = level
        self.r = r
        self.c = c

class TimePassRequest(Event):
    pass

class YouWaitRequest(Event):
    pass

class ZombieEvent(Event):
    def __init__(self, who, where):
        Event.__init__(self)
        assertNotNone('who', who)
        assertNotNone('where', where) #TODO also assert that where's fields are not None and overall is valid location/coords; probably make a Location.assertValid(loc) function member of Location and call from here
        Location.assertFullyPopulatedAndValid(where)
        self.who = who
        self.where = where

################
# Events - end #
################

#########################
# WebHack class - begin #
#########################

# WebHack: the core game engine and default game impl

class WebHack:
    short_code = None #value like 'zh' or 'fh'
    thing_class_prefix = '' #subclass values should be like 'zh_' or 'fh_'
    init_state_file_indicator = short_code

    def __init__(self):
        self.diag = True #whether diagonal movement allowed in this game
        self.help_viewfn = None
        self.usercmd_viewfn = None
        self.gamename = 'SomeWebHackGame'
        self.you = None
        self.should_clear_feedback_every_tick = True # value in effect before init_eventsystem called will matter most/best, because won't register the listener
        self.last_usercmd = (None,None)
        self.config = {}
        self.reset_config()
        self.majornpcs = {}
        self.changed_since_last_render = True
        self.rel_dir_cmd_last_submitted = {}
        self.gamedatasubdir = ''
        self.size = 300000 #placeholder value, not really used
        self.sandbox_region_key = 'sandbox-region'
        self.sandbox_level_key = 'sandbox-level'
        self.last_save_time = None
        self.last_save_tock = None
        self.gamemode = None

    def reset_config(self): # WebHack
        if self.config is None:
            self.config = {}
        self.set_cfg('you_see_all',False)
        self.set_cfg('you_hear_all',False)
        self.set_cfg('you_know_all',False)
        self.set_cfg('you_invuln',False)
        self.set_cfg('debug',True)
        self.set_cfg('trace',False)
        if not self.has_cfg('devmode'):
            self.set_cfg('devmode',False)
        self.set_cfg('you_always_hit',False)
        self.set_cfg('you_always_do_kill_dmg',False)
        self.set_cfg('no_npc_move',False)
        self.set_cfg('min_see_range',1)
        self.set_cfg('max_see_range',20)
        self.set_cfg('min_secs_between_saves',60*60) # 1 hour
        self.set_cfg('bgmusic',False)
        self.set_cfg('autoheal_tocks',10)
        self.set_cfg('autoheal_min',0.5)
        self.set_cfg('autoheal_amount',1)
        self.last_save_time = None
        self.last_save_tock = None
        self.TICKS_PER_DAY = TICKS_PER_DAY_DEFAULT

    def init_languagehelper(self): # WebHack
        self.lh = AppLanguageHelper(self)

    def get_data_lines(self, datagroupname):
        corefilename = datagroupname.replace(' ','_')
        return read_file_lines(DATADIR+'%s.txt' % corefilename)

    def load_datagroup_into_dict_entry(self, ddict, datagroupname, subdir=''):
        ddict[datagroupname] = self.get_data_lines(subdir+datagroupname)

    def believe_all_in(self, believer, datagroupname):
        blfs = self.get_data_lines(datagroupname)
        for blf in blfs:
            self.ai.be.believe(believer, blf)

    def think_all_in(self, thinker, datagroupname):
        ths = self.get_data_lines(datagroupname)
        for th in ths:
            self.ai.th.think(thinker, th)

    def init_idsys(self):
        self.idsys = IdSystem()

    def init_groups(self): # WebHack
        self.groups = Groups()

    def init_ai(self): # WebHack
        fa = WebHackFactSystem(self)

        sk = SkillSystem()
        sk.plugin = WebHackSkillSystemPlugin(self)
        sb = sk.define_skillbundle_skill
        sb('American citizen', 'English language', 1)
        sb('American citizen', 'geography of USA', 1)
        sb('American citizen', 'history of USA', 1)

        mem = MemorySystem() # TODO rename ms to mem
        mem.plugin = WebHackMemorySystemPlugin(self)

        be = BeliefSystem()

        go = GoalSystem()

        th = ThoughtSystem() # TODO rename ts to th
        th.plugin = WebHackThoughtSystemPlugin(self)

        self.ai = AiSystem(fa,sk,mem,be,go,th)

    def init_geo(self, w, h): # WebHack
        self.init_layoutmap()
        self.geo = WebHackGeoSystem(self)
        self.geo.plugin = WebHackGeoSystemPlugin(self.geo,self)
        self.geo.init('The Universe',w,h)

    def init_layoutmap(self):
        self.layoutmap = {}
        for k in master_layoutmap:
            self.layoutmap[k] = master_layoutmap[k]
        self.layoutmap['T'] = Tree
        self.layoutmap['F'] = FruitTree
        self.layoutmap['#'] = Wall
        self.layoutmap['B'] = Barricade

    def is_goal_satisfied_you_stay_alive(self):
        return self.you.is_alive()

    #TODO looks wrong that param for this method and several following is 'fn' and not 'self' - investigate and fix if needed:
    def autoui(fn):
        meta = getattr_withlazyinit(fn, 'meta', {})
        meta[AUTOUI_METAKEY] = True
        return fn

    def inventorythingusercmd(fn):
        meta = getattr_withlazyinit(fn, 'meta', {})
        meta[INVENTORYTHINGUSERCMD_METAKEY] = True
        return fn

    def directional(fn):
        meta = getattr_withlazyinit(fn, 'meta', {})
        meta[DIRECTIONAL_METAKEY] = True
        return fn

    def movecmd(fn):
        meta = getattr_withlazyinit(fn, 'meta', {})
        meta[MOVECMD_METAKEY] = True
        return fn

    def devonly(fn):
        meta = getattr_withlazyinit(fn,'meta',{})
        meta[DEVONLY_METAKEY] = True
        return fn

    def is_usercmd_allowed(self, cmd_name):
        meth_name = USERCMD_PREFIX + cmd_name
        method = getattr(self,meth_name)
        #print meth_name
        if cmd_name == 'devmode' and self.cfg('devmode_allowed'):
            return True
        if is_devonly(method) and not self.cfg('devmode'):
            return False
        return True

    def game_end_announce_format(self, s):
        return '\n' + s.upper() + '\n'

    def pick_bgmusic_file_to_play(self):
        path = envcfg('MEDIA_ROOT') + self.get_game_specific_media_subdir() + 'bgmusic/'
        fnames = os.listdir(path)
        fnames = self.strip_non_bgmusic_format_filenames(fnames)
        fname = random.choice(fnames)
        return fname

    def strip_non_bgmusic_format_filenames(self, fnames):
        return [f for f in fnames if f.lower().endswith('.mp3')]

    def get_base_media_url(self):
        return media_url(self.get_game_specific_media_subdir())

    def get_game_specific_media_subdir(self):
        #TODO to be consistent, this shouldn't be hardcoded in subclass impls of htis method, instead, this impl here should somehow get it from the db, from the Game row's 'mediasubdir' column, to be consistent with how done elsewhere on the site
        return '' # 'zomhack/'

    def get_help_blurb(self): # WebHack
        #TODO return useful info, manual, cheatsheet, common commands, tutorial, guide, play tips, advice, etc. Part of it is generic to all WebHack games, and part is specific to the particular game (ZombieHack or WolfenHack, etc.)
        s = 'Help%s%sThis is the %s help page.' % (EOL, EOL, self.gamename)
        s += (EOL * 2)
        s += 'The example in-game screenshot below will be used to explain the meaning and usage of each UI element:'
        s += EOL
        fname = 'zomhack/help_example_sshot_annotated.png'
        s += img(fname)
        s += EOL
        #TODO all the "#." toplevel entry lines should be in one file
        #TODO the <b> tags should not be inside the files, instead added here by code
        s += read_data_file('webhack/key_start',linedelim=EOL) + EOL
        s += read_data_file('webhack/key_dir_actions',linedelim=EOL,lineprefix=space(4)) + EOL
        s += read_data_file('webhack/key_mid',linedelim=EOL) + EOL

        s += space(4) + '<b>Miscellaneous Actions &amp; Commands:</b>' + EOL
        #TODO these cmds shouldn't be listed here hardcoded; instead, each usercmd fn should have an attrib/quality which indicates whether it should appear in the Help doc or not:
        usercmds = ('again','change_ui','clear','commands','desc_self','drop_all','inventory','jump','look_here','memories','pickup_all','route','say_hello','skills','sound_toggle','stairs','story','thing_classes','things_here','wait','wave_arms','yell','reset')
        cmds2 = []
        for cmd in usercmds:
            label = self.label_for_usercmd(cmd)
            cmds2.append( (cmd,label) )
        cmds = sorted(cmds2,key=lambda q: q[1])
        for cmd, label in cmds:
            fnname = 'usercmd_' + cmd 
            s += space(4) + '<b>'+label+':</b> ' + get_doc(self,fnname) + EOL

        s += read_data_file('webhack/key_end',linedelim=EOL)

        ss = EOL*2 + '<b>Play Help</b>' + EOL*2
        body = read_data_file('webhack/help_bottom',linedelim=EOL)
        min = self.cfg('autoheal_min')
        min = int(min * 100)
        params = {
            'tocks_per_day'   : self.TICKS_PER_DAY,
            'autoheal_amount' : self.cfg('autoheal_amount'),
            'autoheal_tocks'  : self.cfg('autoheal_tocks'),
            'autoheal_min'    : min}
        ss += body % params + EOL
        s += ss

        return s

    def feedbacksay(self, who, plurality, tense, sayswhat):
        verb = 'to say'
        rest = ' "' + str(sayswhat) + '"'
        return self.feedbackitv(who,verb,plurality,tense,rest)

    def feedbackitvsen(self, who, verb, plurality='singular', tense='present', rest=''):
        f = self.lh.itverbify(who,verb,plurality,tense) + rest
        f = sentence(f)
        self.feedback(f)

    def feedbackitv(self, who, verb, plurality='singular', tense='present', rest=''):
        f = self.lh.itverbify(who,verb,plurality,tense) + rest
        self.feedback(f)

    #TODO make FeedbackSystem and all these feedback methods into it?
    def feedbacksen(self, msg):
        self.feedback(sentence(msg))

    def feedback_async(self, msg):
        event = FeedbackDeferred(msg)
        self.emit_event(event)

    def feedback2(self, msgtemplate, feedback=True, who=None, ifyou=True, verb=None, tense='present', plurality='singular', whodesc=None, sentenceify=True):
        parts = {}
        if whodesc is None:
            whodesc = who.describe()
        parts['who'] = whodesc
        if verb is not None:
            parts['whoverb'] = self.lh.itverbify(who,verb,plurality,tense)
        if who is self.you:
            parts['whose'] = 'your'
        elif isinstance(who,Human) and who.is_alive() and not isinstance(who,zh_Zombie):
            if male:
                parts['whose'] = 'his'
            else:
                parts['whose'] = 'hers'
        else:
            parts['whose'] = "it's"
        msg = msgtemplate % parts
        if sentenceify:
            msg = sentence(msg)
        if ifyou:
            if who is self.you and feedback:
                self.feedback(msg)
            else:
                self.debug(msg)
        else:
            self.feedback(msg)

    def feedback_ifyou(self, who, rest, feedback=True, verb=None, tense='present'):
        msg = rest
        plurality = 'singular'
        if verb is not None:
            msg = self.lh.itverbify(who,verb,plurality,tense) + rest
        if who is self.you and feedback:
            self.feedback(msg)
        else:
            self.debug(msg)

    def feedback_ifanyyou(self, many_who, msg):
        if self.you in many_who:
            self.feedback(msg)
        else:
            self.debug(msg)

    def feedback(self, msg, shouldmakehtmlsafe=True, newlines2EOL=True):
        'text to show to user as feedback to his commands or to describe events that occurred in the game world'
        self.msgs.append( (msg,self.ev.tock,shouldmakehtmlsafe,newlines2EOL) )
        self.log(msg)

    def handle_deferred_feedback(self, feedback_deferred):
        self.feedback(feedback_deferred.msg)

    def clear_feedback(self, event=None):
        del self.msgs[:]

    def clear_feedback_every_tick(self, event=None):
        if self.should_clear_feedback_every_tick:
            self.clear_old_feedback(event)

    def clear_old_feedback(self, event=None):
        self.debug('clear_old_feedback()')
        oldmsgs = []
        for m in self.msgs:
            tockmsgcreated = m[1]
            if self.ev.tock - tockmsgcreated >= 1:
                oldmsgs.append(m)
        for m in oldmsgs:
            self.msgs.remove(m)

    def log(self, msg):
        log(msg)

    def debug(self, msg):
        if self.cfg('debug'):
            debug(msg)

    def trace(self, msg):
        if self.cfg('trace'):
            trace(msg)

    def error(self, msg):
        error(msg)

    def bug(self, msg):
        error('BUG: %s' % msg)

    def reset(self, gamemodeclass=None):
        self.log('wh.reset()')
        self.changed_since_last_render = True
        self.rel_dir_cmd_last_submitted = {}
        if gamemodeclass is None:
            dgm_class = self.__class__.demo_game_mode_class
            fgm_class = self.__class__.full_game_mode_class
            if self.gamemode is None or isinstance(self.gamemode,fgm_class):
                gamemodeclass = fgm_class
            else:
                gamemodeclass = dgm_class
        self.gamemode = gamemodeclass(self)
        self.init_languagehelper()
        self.init_game()

    def init_gameend_flags(self):
        self.gameloss = False
        self.gamewin = False

    def init_textpools(self): # WebHack
        self.textpools = TextPools()
        d = {}
        d['genders'] = ['male','female']
        load = self.load_datagroup_into_dict_entry
        load(d,'nationalities')
        load(d,'American male names')
        load(d,'American female names')
        load(d,'colors')
        load(d,'hair colors')
        load(d,'races')
        load(d,'American cities')
        load(d,'Mexican cities')
        cities = []
        cities.extend(d['American cities'])
        cities.extend(d['Mexican cities'])
        d['cities'] = cities
        self.textpools.define_pools(d)

    def get_rnd_person_name(self, nationality=None, gender=None):
        if nationality is None:
            nationality = self.textpools.get_random_entry('nationalities')
        if gender is None:
            gender = self.textpools.get_random_entry('genders')
        namepool = '%s %s names' % (nationality, gender)
        return self.textpools.get_random_entry(namepool)

    def init_misc(self):
        self.majornpcs = {}
        self.init_predefined_building_layouts()

    def init_sandbox_level(self, region):
        sandbox, lk = self.geo.new_level('Development Sandbox Level', region)
        self.sandbox_region_key, self.sandbox_level_key = self.geo.get_keys_for_level(sandbox)

    def init_game(self): # WebHack
        self.changed_since_last_render = True
        self.reset_config()
        self.init_idsys()
        self.init_misc()
        self.init_gameend_flags()
        self.init_feedback()
        self.init_groups()
        self.init_eventsystem()
        self.init_textpools()
        self.init_ai()

        w = 30
        h = 10
        self.init_geo(w,h)
        self.init_sandbox_level(self.geo.initial_region)

        # Create a simple world by default; just You on a map:
        self.geo.initial_level.environment = Level.OUTSIDE
        self.you = You(self)
        you = self.you
        self.put_on_map(you, self.geo.new_loc((h/2),(w/2)) )
        self.ev.add_listener((ThingEntersCellEvent,{'thing':self.you}),self,'make_you_level_active_and_focus_ui')
        self.update_seen_cells()

        self.init_ui()
        self.ui.show_you_level()
        #TODO once Console exists for a wh game, have a user command that lets him add or remove entries from the methods2call_per_tick list, and also just prints the current entries

    def init_eventsystem(self): # WebHack
        #TODO upgrade EventSystem so it automatically emits (from itself, not in app code) a special event (named like 'success_<event>') if the corresponding call to 'execute_<event>' just returned successfully (no error code returned or exception ripped out); Then an app could register listeners for these success events; A success event would itself have a ref/handle to the orig event instance that was acted on by the call to execute_<event>; Also, same idea but to indicate failure. Ideally, the fn impls of execute_<event> can return a tuple, with the first slot indicating success/failure boolean, and the second slot containing a textual explanation of the reason for failure, if appropriate. That explanation is attached to (or reachable from) the failed_<event> event instance.
        self.ev = AppEventSystem(self)
        self.ev.init()

        ev = self.ev
        ev.add_listener((TickEvent,{}),self,'core_engine_tick_tasks')
        if self.should_clear_feedback_every_tick:
            # the first=True tells the ES that this lis must be called first:
            ev.add_listener((TickEvent,{}),self,'clear_feedback_every_tick',first=True)
        ev.add_listener((TickEvent,{}),self,'you_make_observations_of_surroundings')
        ev.add_listener((TickEvent,{}),self,'declare_game_loss_if_you_are_dead')
        ev.add_listener((TickEvent,{}),self,'update_seen_cells_every_tick')
        ev.add_listener((TickEvent,{}),self,'your_worn_costumes_degrade')
        ev.add_listener((TickEvent,{}),self,'lifeforms_digest_stomach_content')
        ev.add_listener((TickEvent,{}),self,'lifeforms_with_empty_stomachs_starve_to_death')
        ev.add_listener((TickEvent,{}),self,'you_auto_heal_slowly')
        ev.add_listener((TimePassRequest,{}),self,'execute_timepass')
        ev.add_listener((YouWaitRequest,{}),self,'execute_you_wait')
        ev.add_listener((ThingEntersCellEvent,{}),self,'apply_terrain_effects_due_to_entering_cell')
        ev.add_listener((MoveRequest,{}),self,'execute_move')
        ev.add_listener((AttackAttempt,{}),self,'execute_attack')
        ev.add_listener((SoundEvent,{}),self,'handle_all_sounds')
        #TODO also reg listener for 'turned into zombie' event that does makes it dropall
        ev.add_listener((DeathEvent,{}),self,'just_died_thing_should_drop_inventory')
        ev.add_listener((FeedbackDeferred,{}),self,'handle_deferred_feedback')
        ev.add_listener((PickUpRequest,{}),self,'execute_pickup_request')
        ev.add_listener((DropRequest,{}),self,'execute_drop')
        #ev.add_listener(('jump',{}),self,'execute_jump')
        #ev.add_listener(('wave_arms',{}),self,'execute_wave_arms')

    def your_worn_costumes_degrade(self, tick_event):
        you = self.you
        for cos in you.get_worn_of_class(Costume):
            if cos.fidelity > 0:
                cos.fidelity -= 1

    def lifeforms_digest_stomach_content(self, tick_event):
        def fn2visit(lifeform):
            if not lifeform.does_digest():
                return
            digested = lifeform.digest()
            if lifeform.has_empty_stomach():
                if digested > 0:
                    self.feedback2('%(whoverb)s the last of %(whose)s stomach contents.', who=lifeform, verb='to digest', tense='past')

                else:
                    self.feedback2('%(whoverb)s an empty stomach so nothing to digest.', who=lifeform, verb='to have')
        level = self.geo.activelevel
        #self.geo.visit_with_all_things_in_level(fn2visit, level) # <- better perf, but more local code req
        self.geo.visit_with_every_thingclass_instance_in_level(fn2visit, level, Lifeform)

    def lifeforms_with_empty_stomachs_starve_to_death(self, tick_event):
        class Foo:
            wh = None
            def fn2visit(self, lifeform):
                if lifeform.has_empty_stomach() and lifeform.is_alive() and lifeform.may_starve():
                    if lifeform.hp > 0:
                        amt = 1
                        lifeform.hp -= amt
                        self.wh.feedback('%s lost %s hp due to starvation and now has %s hp' % (lifeform.describe(), amt, lifeform.hp))
                        if lifeform.hp < 1:
                            self.wh.make_dead_remove_and_replace_with_corpse(lifeform)
        f = Foo()
        f.wh = self
        level = self.geo.activelevel
        self.geo.visit_with_every_thingclass_instance_in_level(f.fn2visit, level, Lifeform)

    def you_auto_heal_slowly(self, tick_event):
        if (tick_event.tock % self.cfg('autoheal_tocks')) != 0:
            return
        amt = self.cfg('autoheal_amount')
        min = self.cfg('autoheal_min')
        you = self.you
        if you.is_alive() and you.hp < you.hp_max and ((float(you.hp) / float(you.hp_max)) >= min):
            you.hp += amt
            self.feedback('You heal a little.')

    def update_seen_cells_every_tick(self, tick_event):
        self.update_seen_cells()

    def update_seen_cells(self):
        debug('update_seen_cells')

        #TODO add a new visit method to GS that visits with every cell/r,c for a level and redo below with it:
        you = self.you
        yloc = you.loc
        yr = yloc.r
        yc = yloc.c
        level = self.you.loc.level
        see_range = self.get_see_range()
        debug('see_range: %i' % see_range)

        # Reset Every Cell's Lit State to False 
        for r in xrange(len(level.grid)):
            row = level.grid[r]
            for c in xrange(len(row)):
                cell = level.grid[r][c]
                cell.lit = False
        
        # TODO commented out because was causing whole level to light up
        # should fix then decomment
        # and readd some Flare instances to the start level
        # See Cells by Lit Flares

        class Foo:
            def __init__(self):
                self.flares = []
            def fn2visit(self, flare):
                r = flare.loc.r
                #c = flare.loc.c
                #cell = flare.loc.level.grid[r][c]
                #cell.lit = True
                self.flares.append(flare)
        f = Foo()
        level = self.geo.activelevel
        self.geo.visit_with_every_thingclass_instance_in_level(f.fn2visit, level, Flare)

        # if there are any flares, then light up each cell on the level that is close enough to any flare that the flare's light hits it
        if len(f.flares) > 0:
            for r in xrange(len(level.grid)):
                row = level.grid[r]
                for c in xrange(len(row)):
                    cell = level.grid[r][c]
                    cell.lit = False
                    for flare in f.flares:
                        fr = flare.loc.r
                        fc = flare.loc.c
                        d = dist(fr,fc, r,c)
                        if (d <= 1):
                            cell.lit = True
                            debug('flare has lit a cell: %i,%i' % (c,r))
        

        for r in xrange(len(level.grid)):
            row = level.grid[r]
            for c in xrange(len(row)):
                cell = level.grid[r][c]
                cell.seen = True
                if level.environment == Level.OUTSIDE: # outdoors, sun/stars/moon up above, fresh air, bears
                    if cell.lit:
                        cell.seen = True
                        debug('you see a cell because lit & outside: %i,%i' % (c,r))
                    else:
                        d = dist(r,c, yr,yc)
                        cell.seen = (d <= see_range)
                        if cell.seen: debug('you see a cell because in range & outside: %i,%i' % (c,r))
                        else: debug('you do NOT see an outside cell: %i,%i' % (c,r))
                else: # else it is Level.INSIDE (meaning indoors) so not effected by the day/night light cycle
                    cell.seen = True
                    debug('you see a cell because inside: %i,%i' % (c,r))
                    #TODO PERF bad to do this every tick if this level's environment value is always INSIDE, and never changes; I only need to set seen to True once, then never alter it again


    def get_see_range(self):
        see_range = 0
        t = self.tock_into_day_cycle()
        min = 0
        max = self.TICKS_PER_DAY / 2
        sr_diff = max - min
        self.debug('sr_diff %s' % sr_diff)
        half_day = self.TICKS_PER_DAY / 2
        self.debug('half_day %s' % half_day)
        sr_diff_per_tick = sr_diff / half_day
        self.debug('sr_diff_per_tick %s' % sr_diff_per_tick)
        if t >= 0 and t < half_day: # night
            see_range = min + (t * sr_diff_per_tick)
        else: # day
            t2 = t - half_day
            see_range = max - (t2 * sr_diff_per_tick)
        self.log('see_range %s' % see_range)
        if see_range < self.cfg('min_see_range'):
            see_range = self.cfg('min_see_range')
        if see_range > self.cfg('max_see_range'):
            see_range = self.cfg('max_see_range')
        return see_range

    def get_time_of_day_desc(self):
        reltock = self.tock_into_day_cycle()
        midnight = 0
        if reltock == midnight:
            return 'midnight'
        noon = self.TICKS_PER_DAY / 2
        if reltock == noon:
            return 'noon'
        half_day = self.TICKS_PER_DAY / 2
        quarter_day = self.TICKS_PER_DAY / 4
        if reltock >= quarter_day and reltock < noon:
            return 'morning'
        if reltock > noon and reltock <= (noon + quarter_day):
            return 'afternoon'
        if reltock > noon + quarter_day and reltock <= (noon + quarter_day + (quarter_day/2)):
            return 'evening'
        #TODO morning, afternoon, evening
        if self.is_night():
            return 'night'
        else:
            return 'day'

    def is_night(self):
        t = self.tock_into_day_cycle()
        half_day = self.TICKS_PER_DAY / 2
        if t >= (half_day / 2) and t < (half_day + (half_day / 2)):
            return False
        else:
            return True

    def tock_into_day_cycle(self):
        return self.ev.tock % self.TICKS_PER_DAY

    def handle_all_sounds(self, sound_event):
        class Foo:
            def __init__(self, sound_event):
                self.sound_event = sound_event

            def fn2visit(self, hearer):
                hearer.sound_reaches_self(sound_event)

        f = Foo(sound_event)
        level = sound_event.where.level
        self.geo.visit_with_all_things_in_level(f.fn2visit, level)

    def make_you_level_active_and_focus_ui(self, thing_enters_cell_event=None):
        self.geo.activelevel = self.you.loc.level
        self.ui.show_active_level()

    def apply_terrain_effects_due_to_entering_cell(self, thing_enters_cell_event):
        event = thing_enters_cell_event
        thing = event.thing
        level = event.level
        r = event.r
        c = event.c
        try: cell = level.grid[r][c]
        except IndexError, e:
            self.log('\n\nr,c=%s,%s   len(level.grid) = %s' % (r, c, len(level.grid)))
            self.log('level id %s' % id(level))
            self.log('thing id %s, desc %s' % (id(thing), thing.describe()))
            self.log('%s' % self.geo.report_geography(indent='\t'))
            if r >= 0 and r < len(level.grid):
                self.log('len(level.grid[%s]) = %s' % (r, len(level.grid[r])))
                pass
            raise e
        #TODO instead of making the thing wet here, instead, just make a call to cell.terrain.thing_enters_cell(event), and let the target method impl decide what to do; inside the default Terrain impl of that method, it does nothing; inside the Water class's impl, it performs the task of 'making that thing wet'
        if cell.terrain is not None and isinstance(cell.terrain,Water):
            #TODO emit event that indicates that that thing just got wet, and/or gained this fact:
            if not self.ai.fa.has_fact(thing,'wet'):
                self.ai.fa.add_fact(thing,'wet')
                if thing is self.you:
                    self.feedback('You got wet.')

    def most_important_thing_here_to_show_on_map_other_than_you(self, cell):
        answer = None
        for th in cell.things:
            if not th.is_invisible() and ((answer is None) or (self.render_importance(th) >= self.render_importance(answer))):
                answer = th
        return answer

    def render_importance(self, thing):
        return thing.get_render_importance()

    def usercmd_geo(self):
        s = self.geo.report_geography(indent=space(1))
        self.feedback('The world contains:\n'+s)
    autoui(devonly(usercmd_geo))

    def usercmd_objreport(self):
        s = ''
        if hasattr(self,'objreport'):
            s = self.objreport
        self.feedback(s)
    autoui(devonly(usercmd_objreport))

    def usercmd_majornpcs(self):
        s = 'majornpcs:  %s' % pprint.pformat(self.majornpcs)
        self.feedback(s)
    devonly(autoui(usercmd_majornpcs))

    def usercmd_no_npc_move(self):
        v = self.toggle_cfg('no_npc_move')
        s = 'no_npc_move: %s' % v
        self.feedback(s)
    devonly(autoui(usercmd_no_npc_move))

    def usercmd_lifeforms(self):
        s = ''
        lifeforms = []
        self.geo.visit_with_every_thingclass_instance_in_world(\
            lambda lf: lifeforms.append(lf), Lifeform)
        for lf in lifeforms:
            s += self.devdesc(lf) + '\n'
        self.feedback('All lifeforms in world:\n'+s+'---\n')
    devonly(autoui(usercmd_lifeforms))

    def usercmd_edibles(self):
        s = ''
        things = []
        self.geo.visit_with_every_thingclass_instance_in_world(\
            lambda th: things.append(th), Edible)
        for th in things:
            s += self.devdesc(th) + '\n'
        self.feedback('All edibles in world:\n%s---\n' % s)
    devonly(autoui(usercmd_edibles))

    def usercmd_things(self):
        s = 'All things in the world:\n\n'
        class Foo:
            things = []
            wh = self
            def fn(self, thing):
                self.things.append(thing)
        f = Foo()
        self.geo.visit_with_all_things_in_world(f.fn)
        s += 'count: ' + str(len(f.things)) + '\n\n'
        for thing in f.things:
            s += self.devdesc(thing) + '\n'
        self.feedback(s)
    devonly(autoui(usercmd_things))

    def usercmd_thing_classes(self):
        '''map symbols key'''
        classes = get_instantiable_thing_classes(globals())
        keys = []
        ddict = {}
        for cl in classes:
            keys.append(cl.__name__)
            ddict[cl.__name__] = cl
        keys.sort()
        data = []

        def build_row(k, traits, cl, self):
            color = HtmlColors.BLACK
            if hasattr(cl,'charcolor'):
                color = cl.charcolor
            charchunk = fontcolorize(cl.char,color)
            if self.cfg('devmode'):
                row = [k, charchunk, cl.__module__, traits]
            else:
                row = [k, charchunk, traits]
            return row

        for k in keys:
            cl = ddict[k]
            #k is the thing class's name:
            if len(k) >= 4 and k[2] == '_' and not k.startswith(self.thing_class_prefix):
                continue
            traits = ''
            if issubclass(cl,IsOpenCloseable):
                traits += ' (OC)'
            if issubclass(cl,Clothing):
                traits += ' (CL)'
            if issubclass(cl,Weapon):
                traits += ' (W)'
            if issubclass(cl,Edible):
                traits += ' (E)'
            if issubclass(cl,Food):
                traits += ' (F)'
            if issubclass(cl,Money):
                traits += ' (M)'
            if issubclass(cl,RndStuff):
                traits += ' (R)'
            if issubclass(cl,Lifeform):
                traits += ' (L)'
            if issubclass(cl,Human):
                traits += ' (H)'
            if issubclass(cl,Animal):
                traits += ' (AN)'
            if issubclass(cl,Corpse):
                traits += ' (CO)'
            row = build_row(k,traits,cl,self)
            data.append(row)
        #TODO add row for: open door, broken window
        #data.append(build_row('Door (open)',traits,cl,self))
        #data.append(build_row('Window (broken)',traits,cl,self))
        s = table(data,header=False,delim='')
        s += EOL + 'Code Key:'
        data = []
        data.append(['(AN)','animal'])
        data.append(['(CL)','clothing/wearable'])
        data.append(['(CO)','corpse'])
        data.append(['(E)', 'edible'])
        data.append(['(F)', 'food'])
        data.append(['(H)', 'human'])
        data.append(['(L)', 'lifeform'])
        data.append(['(M)', 'money'])
        data.append(['(OC)','open/close-eable'])
        data.append(['(R)', 'random item'])
        data.append(['(W)', 'weapon'])
        s += EOL + table(data,header=False,delim='')
        self.feedback(s,shouldmakehtmlsafe=False)
    autoui(usercmd_thing_classes)
    usercmd_thing_classes.label = 'map key'

    def usercmd_clear(self):
        '''clears the feedback portion of the screen (no impact on the game, just cleans up your screen a little)'''
        self.clear_feedback()
    autoui(usercmd_clear)

    def usercmd_config(self):
        s = 'global debug: ' + str(debugvar) + '\n'
        s += 'global force_reset: ' + str(force_reset) + '\n'
        keys = list(self.config.keys())
        keys.sort()
        s += '\n'.join(map(lambda k: str(k) + ': ' + str(self.config[k]), keys))
        self.feedback(s)
    devonly(autoui(usercmd_config))

    def cfg(self, key):
        v = self.config[key]
        return v

    def has_cfg(self, key):
        return key in self.config

    def set_cfg(self, key, value):
        global debugvar
        self.config[key] = value
        if key == 'debug':
            debugvar = value
        return self.cfg(key)

    def toggle_cfg(self, key):
        v = self.cfg(key)
        v = not v
        return self.set_cfg(key,v)

    def usercmd_debug(self):
        global debugvar
        v = self.toggle_cfg('debug')
        debugvar = v
        self.feedback('debug: ' + str(v))
    devonly(autoui(usercmd_debug))

    def usercmd_devmode(self):
        toggle_allowed = True
        if not self.cfg('devmode'):
            toggle_allowed = self.cfg('devmode_allowed')
        if toggle_allowed:
            v = self.toggle_cfg('devmode')
            self.feedback('devmode: ' + str(v))
        else:
            self.feedback('devmode not allowed')
    devonly(autoui(usercmd_devmode))

    def usercmd_win_game(self):
        self.gamewin = not self.gamewin
        self.feedback('wh.gamewin now %s' % self.gamewin)
    devonly(autoui(usercmd_win_game))

    def usercmd_lose_game(self):
        self.gameloss = not self.gameloss
        self.feedback('wh.gameloss now %s' % self.gameloss)
    devonly(autoui(usercmd_lose_game))

    def usercmd_game_mode(self):
        dgm_class = self.__class__.demo_game_mode_class
        fgm_class = self.__class__.full_game_mode_class
        prev = self.gamemode
        if not isinstance(self.gamemode,fgm_class):
            self.gamemode = fgm_class(self)
        else:
            self.gamemode = dgm_class(self)
        self.feedback('gamemode switched from %s to %s' % (prev.mode_name(), self.gamemode.mode_name()))
    devonly(autoui(usercmd_game_mode))

    def usercmd_force_reset(self):
        global force_reset
        force_reset = not force_reset
        self.feedback('force_reset: ' + str(force_reset))
    devonly(autoui(usercmd_force_reset))

    def usercmd_digests(self):
        self.you.digests = not self.you.digests
        self.feedback('you.digests: %s' % self.you.digests)
    devonly(autoui(usercmd_digests))

    def usercmd_starves(self):
        self.you.starves = not self.you.starves
        self.feedback('you.starves: %s' % self.you.starves)
    devonly(autoui(usercmd_starves))

    def usercmd_see_all(self):
        v = self.toggle_cfg('you_see_all')
        self.feedback('you_see_all: ' + str(v))
    devonly(autoui(usercmd_see_all))

    def usercmd_hearall(self):
        v = self.toggle_cfg('you_hear_all')
        self.feedback('you_hear_all: ' + str(v))
    devonly(autoui(usercmd_hearall))

    def usercmd_hit_always(self):
        v = self.toggle_cfg('you_always_hit')
        self.feedback('you_always_hit: ' + str(v))
    devonly(autoui(usercmd_hit_always))

    def usercmd_kill_always(self):
        v = self.toggle_cfg('you_always_do_kill_dmg')
        self.feedback('you_always_do_kill_dmg: ' + str(v))
    devonly(autoui(usercmd_kill_always))

    def usercmd_invuln(self):
        v = self.toggle_cfg('you_invuln')
        self.feedback('you_invuln: ' + str(v))
    devonly(autoui(usercmd_invuln))

    def usercmd_sandbox(self):
        sandbox_lev = self.geo.get_level_with_keys(self.sandbox_region_key, self.sandbox_level_key)
        oldloc_attr = 'oldloc_before_sandbox'
        if self.you.loc.level is sandbox_lev:
            if hasattr(self.you, oldloc_attr):
                destloc = getattr(self.you, oldloc_attr)
                allowed, explanation = self.can_it_move_there(self.you, destloc)
                if allowed:
                    self.geo.move_this_from_here_to_there(self.you, destloc)
                    self.make_you_level_active_and_focus_ui()
                    self.feedback('teleported you to pre-sandbox location')
                else:
                    self.feedback('could not tp you to pre-sandbox location because: %s' % explanation)
            else:
                self.feedback('could not tp you because your pre-sandbox location was not recorded')
        else:
            destloc = Location(0, 0, sandbox_lev, sandbox_lev.region)
            allowed, explanation = self.can_it_move_there(self.you, destloc)
            if allowed:
                setattr(self.you, oldloc_attr, self.you.loc.clone())
                self.geo.move_this_from_here_to_there(self.you, destloc)
                self.make_you_level_active_and_focus_ui()
                self.feedback('teleported you to the sandbox level')
            else:
                self.feedback('could not tp you to sandbox because: %s' % explanation)
    devonly(autoui(usercmd_sandbox))

    def usercmd_textpools(self):
        s = self.textpools.report()
        self.feedback(s)
    devonly(usercmd_textpools)

    def usercmd_allcmds(self):
        if not self.cfg('devmode'): return
        s = 'all commands:\n\n'
        cmdlist = self.get_usercmd_list()
        s += '\n'.join(cmdlist)
        self.feedback(s)
    devonly(autoui(usercmd_allcmds))

    def usercmd_commands(self):
        '''lists all user/action commands available to you via the Console'''
        s = 'avail commands:\n\n'
        withdev = self.cfg('devmode')
        cmdlist = self.get_usercmd_list(devonly=withdev)
        s += '\n'.join(cmdlist)
        self.feedback(s)
    autoui(usercmd_commands)

    def usercmd_devcmds(self):
        s = 'devonly commands:\n\n'
        cmdlist = self.get_usercmd_list(devonly=True)
        s += '\n'.join(cmdlist)
        self.feedback(s)
    devonly(autoui(usercmd_devcmds))

    def usercmd_nondevcmds(self):
        s = 'non-devonly commands:\n\n'
        cmdlist = self.get_usercmd_list(nondevonly=True)
        s += '\n'.join(cmdlist)
        self.feedback(s)
    devonly(usercmd_nondevcmds)

    def usercmd_autouicmds(self):
        s = 'autoui commands:\n\n'
        cmdlist = self.get_usercmd_list(autoui=True)
        s += '\n'.join(cmdlist)
        self.feedback(s)
    devonly(usercmd_autouicmds)

    def usercmd_nonautouicmds(self):
        s = 'non-autoui commands:\n\n'
        cmdlist = self.get_usercmd_list(nonautoui=True)
        s += '\n'.join(cmdlist)
        self.feedback(s)
    devonly(usercmd_nonautouicmds)

    def get_usercmd_list(self, devonly=None, nondevonly=None, autoui=None, nonautoui=None):
        default_include = True
        if devonly is not None or nondevonly is not None or autoui is not None or nonautoui is not None:
            default_include = False
        usercmds = []
        attribs = dir(self)
        #TODO the list of usercmd_ method names should be buildt once at module load, then used in all cases like that below, for better perf:
        for a in attribs:
            if a.startswith(USERCMD_PREFIX):
                include = default_include
                if self.does_method_have_meta_value(a,DEVONLY_METAKEY,True):
                    if devonly is not None: include = devonly
                else:
                    if nondevonly is not None: include = nondevonly
                if self.does_method_have_meta_value(a,AUTOUI_METAKEY,True):
                    if autoui is not None: include = autoui
                else:
                    if nonautoui is not None: include = nonautoui
                if include:
                    meth = getattr(self,a)
                    a = a[len(USERCMD_PREFIX):]
                    usercmds.append(a)
        return usercmds

    def does_method_have_meta_value(self, methodname, key, value):
        meth = getattr(self,methodname)
        if hasattr(meth,'meta'):
            return key in meth.meta and meth.meta[key] == value
        else: return False

    def get_directional_move_usercmds_bare(self):
        v = []
        attribs = dir(self)
        for a in attribs:
            if a.startswith(USERCMD_PREFIX):
                has_meta = self.does_method_have_meta_value
                if has_meta(a,DIRECTIONAL_METAKEY,True) and \
                        has_meta(a,MOVECMD_METAKEY,True):
                    bare_cmd = a[len(USERCMD_PREFIX):]
                    v.append(bare_cmd)
        return v

    def get_directional_nonmove_usercmds_bare(self):
        v = []
        attribs = dir(self)
        for a in attribs:
            if a.startswith(USERCMD_PREFIX):
                has_meta = self.does_method_have_meta_value
                if has_meta(a,DIRECTIONAL_METAKEY,True) and \
                        not has_meta(a,MOVECMD_METAKEY,True):
                    bare_cmd = a[len(USERCMD_PREFIX):]
                    v.append(bare_cmd)
        return v

    def usercmd_again(self):
        '''this is a meta-command that will execute again the last command/action you performed (this is only useful if you issued a long, complex command via the Console controls, and wish to re-execute it without re-typing)'''
        if not self.gamemode.again_command_allowed():
            return
        cmd, params = self.last_usercmd
        #TODO bug/flaw: below doesn't implement the should_persist_to_disk or replace_wh_with behavior that the main dispatch_usercmd() call does
        if cmd is not None:
            success, reason, should_persist_to_disk, replace_wh_with = self.dispatch_usercmd(cmd,params)
            #TODO seems wrong/unorthogonal to not handle the return params here

    def usercmd_your_mind(self):
        s = "Here's what's on your mind:\n"
        s += self.ai.dev_report_thing_and_his_mind(self.you)
        self.feedback(s)
    devonly(autoui(usercmd_your_mind))

    def usercmd_all_minds(self):
        s = "AI dev report on all things with minds:\n\n"
        class Foo:
            def __init__(self, wh):
                self.wh = wh
                self.s = ''

            def fn2visit(self, thing):
                if isinstance(thing,HasMind):
                    self.s += self.wh.devdesc(thing) + ':\n'
                    self.s += self.wh.ai.dev_report_thing_and_his_mind(thing)
                    #self.s += 'speech:\n%s\n\n' % thing.randomspeechset
                    self.s += 'speech:\n'
                    if thing.randomspeechset:
                        for t in list(thing.randomspeechset):
                            self.s += "'%s' (%s), " % (t, hex(id(t)))
                    self.s += '\n\n'
        f = Foo(self)
        self.geo.visit_with_all_things_in_world(f.fn2visit)
        s += f.s
        self.feedback(s)
    devonly(autoui(usercmd_all_minds))

    def devdesc(self, thing):
        s = '%s %s %s (%s)' % (thing.full_describe(), thing.id_thing_pp(), self.desc_loc_rel_you(thing), thing.hp_str())
        if isinstance(thing,HasInventory):
            if thing.has_worn():
                s += '; wearing %s' % thing.describe_worn()
            if thing.has_wielded():
                s += '; wielding %s' % thing.describe_wielded()
            if thing.has_unworn_unwielded_inventory():
                s += '; carrying %s' % thing.report_unworn_unwielded_inventory(delim=', ', withid=False)
        return s

    def desc_loc_rel_you(self, thing):
        return self.desc_loc_rel_to_things_pov(thing, self.you)

    def desc_loc_rel_to_things_pov(self, thing, pov_thing):
        s = None
        if thing.loc == pov_thing.loc:
            s = 'at your location'
        else:
            if thing.loc is None:
                s = 'at None (loc is None!)'
                return s
            coords = 'at ' + str((thing.loc.r, thing.loc.c)) + ' '
            leveldesc = None
            regiondesc = ''
            if thing.loc.level is pov_thing.loc.level:
                leveldesc = 'your level'
            else:
                leveldesc = 'level ' + str(thing.loc.level)
                regiondesc += ' in '
                if thing.loc.region is pov_thing.loc.region:
                    regiondesc += 'your region'
                else:
                    regiondesc += 'region ' + str(thing.loc.region)
            s = coords + 'on ' + leveldesc + regiondesc
        return s

    def usercmd_memories(self):
        '''see your memories of the past (mostly only ones relevant to the game's plot/story)'''
        #TODO if the when value (key in dict) is type int (a tock), then convert it to in-game-world time units, like "5 mins ago", or "2 days ago"
        s = 'You remember:\n'
        rep = self.ai.mem.report_memories(self.you)
        if len(rep) > 0:
            s += rep
        else:
            s = 'You remember nothing.'
        self.feedback(s)
    autoui(usercmd_memories)

    def usercmd_attack(self, relrow=0, relcol=0):
        self.debug('usercmd_attack() called')
        relrow = int(relrow)
        relcol = int(relcol)
        attacker = self.you
        r = attacker.loc.r + relrow
        c = attacker.loc.c + relcol
        region = attacker.loc.region
        level = attacker.loc.level
        area = level.area
        if not area.has_valid_coord(c,r):
            self.feedback('invalid attack direction because target is off map')
            return
        atkloc = Location(r,c,level,region)
        best_target = attacker.identify_best_attack_target_there(atkloc)
        if best_target == None:
            self.feedback('rel '+str((relrow,relcol))+'  rc '+str((r,c)))
            self.feedback('no attack targets in that direction')
            return
        target = best_target
        if attacker.has_wielded():
            wieldeds = attacker.wielded_list()
            mainweapon = wieldeds[0]
            skill = mainweapon.__class__.__name__.lower()
        else: # bare-handed
            skill = Skills.HAND_TO_HAND
        attack = AttackAttempt(who=attacker,target=target,skill=skill)
        if not self.ev.meet_event_execute_reqs(attack):
            self.feedback('did not attack because something was wrong')
            return
        self.debug('usercmd_attack() emitting event: ' + str(attack))
        self.emit_event(attack)
        self.ev.tick_and_process_events()
    directional(usercmd_attack)

    def attack_proceed_possible(self, attack_attempt):
        if not isinstance(attack_attempt,AttackAttempt):
            return False, 'event is not instance of AttackAttempt'
        atk = attack_attempt
        if atk.who is None: return False, 'atk.who is None'
        if atk.target is None: return False, 'atk.target is None'
        attacker = atk.who
        target = atk.target
        if not attacker.is_alive(): return False, 'who/attacker is not alive'
        if target.loc is None: return False, 'target not on the map'
        if target.loc.r is None or target.loc.c is None:
            return False, 'target lacks either an r or c coordinate in his loc: (%s,%s)' % (target.loc.r, target.loc.c)
        r = target.loc.r
        c = target.loc.c
        cell = target.loc.level.grid[r][c]
        if target not in cell.things:
            return False, "target not in it's map cell"
        return True, ''

    def execute_attack(self, attack_attempt):
        #TODO for all skill exercise, not always 1 but amt proportional to difficulty of attack and enemy and circumstances
        attacker = attack_attempt.who
        target = attack_attempt.target
        skill = attack_attempt.skill
        tardesc = target.describe()
        can_proceed, reason = self.attack_proceed_possible(attack_attempt)
        if not can_proceed:
            s = sentence('%s could not attack %s' % (attacker.describe(),tardesc))
            self.feedback_ifanyyou((attacker,target),s)
            self.log('attack_attempt (%s) not exec due to: %s' % (attack_attempt, reason))
            return
        attack = self.get_attack_to_use(attacker,target,skill)
        attack.do()
    execute_attack.reqs = [attack_proceed_possible,]

    def get_attack_to_use(self, attacker, target, skill):
        if isinstance(attacker,zh_Zombie) and isinstance(target,Lifeform) and not isinstance(target,Corpse):
            return ZombieAttack(self,attacker,target,skill)
        else:
            return NormalAttack(self,attacker,target,skill)

    def make_dead_remove_and_replace_with_corpse(self, victim):
        assert victim is not None
        assert isinstance(victim,Lifeform)
        #TODO assert that victim was already on the map

        vicloc = victim.loc.clone()
        self.make_lifeform_dead(victim)
        self.geo.remove_from_map(victim)

        event = DeathEvent(who=victim, where=vicloc)
        self.emit_event(event)
        if victim is self.you:
            self.feedback('YOU DIED!!!')
        else:
            self.log('%s died!' % victim.describe())
            #TODO emit soundevent instead, of the appropriate class (BodyFallingDownSound?):
            self.feedback('You hear the sound of a body falling down.')
        corpse = self.put_corpse_on_map_for_lifeform(victim,vicloc)
        if victim is self.you:
            self.you = corpse
        self.delete_thing(victim)
        return True, 'success'

    def put_corpse_on_map_for_lifeform(self, lifeform, loc):
        corpseclass = lifeform.get_corpse_class()
        corpse = corpseclass(self,lifeform)
        char, orig_lifeform_charcolor = lifeform.render_char()
        corpse.charcolor = orig_lifeform_charcolor #TODO wasteful of memory because better to use a corpse class-die charcolor rather than explicitly forcing each corpse instance to have an instance __dict__ entry with a charcolor reference
        self.geo.put_on_map(corpse, loc)
        return corpse

    def make_lifeform_dead(self, lifeform):
        assert lifeform is not None
        assert isinstance(lifeform,Lifeform)
        lifeform.hp = 0

    def delete_thing(self, thing):
        pass # no-op by intent; placeholder/marker to indicate this thing should cease to exist physically in the game world

    def exercise_skill(self, thing, skill, howmuch, reason=None):
        #TODO make post event instead, and have an execute listener which actually makes that call:
        self.ai.sk.exercise_skill(thing,skill,howmuch,reason)

    def init_ui(self, ui_class_name='ClassicUI'): # WebHack
        globs = globals()
        ui_class = None
        if ui_class_name in globs:
            ui_class = globs[ui_class_name]
        else:
            ui_class_name = 'ClassicUI'
            ui_class = ClassicUI
        self.ui = ui_class(self)
        self.ui_class_name_current = ui_class_name
        self.ui.show_active_level()
        self.ui.add_extra_status_fn('status_of_wh_ref_count')
        self.ui.add_extra_status_fn('status_of_garbage_len')
        self.ui.add_extra_status_fn('status_of_wh_size')
        self.ui.add_extra_status_fn('status_of_sess_size')
        self.ui.add_extra_status_fn('status_of_force_reset')
        self.ui.add_extra_status_fn('status_of_eating')
        self.ui.add_extra_status_fn('status_of_wh_gamewin')
        self.ui.add_extra_status_fn('status_of_wh_gameloss')
        self.curses_ui = CursesUI(self)

    def status_of_wh_ref_count(self):
        return 'wh refs: %s' % sys.getrefcount(self)

    def status_of_garbage_len(self):
        return 'garbage len: %s' % len(gc.garbage)

    def status_of_wh_size(self):
        return 'wh size: %s' % self.size

    def status_of_sess_size(self):
        return 'sess size: %s' % self.sess_size

    def status_of_force_reset(self):
        return 'force_reset: %s' % force_reset

    def status_of_eating(self):
        return 'digests/starves: %s/%s' % (self.you.digests, self.you.starves)

    def status_of_wh_gamewin(self):
        return 'gamewin: %s' % self.gamewin

    def status_of_wh_gameloss(self):
        return 'gameloss: %s' % self.gameloss

    def init_feedback(self): # WebHack
        self.msgs = []

    def render_ui(self, game):
        watch = StopWatch('render_ui(): ')
        s = self.ui.render(game)
        self.log(watch.stop())
        return s

    def you_make_observations_of_surroundings(self, event):
        s = self.describe_your_surroundings()
        if s is not None:
            self.feedback(s)

    def describe_your_surroundings(self):
        s = ''
        you = self.you
        yloc = you.loc

        cell = self.geo.get_cell(yloc.level,yloc.r,yloc.c)
        if cell.desc is not None:
            s += cell.desc + '\n'

        stuffhere = self.desc_list_whats_here(yloc)

        nearbystufflist = []
        adjlocs = self.you.loc.level.area.adj_cells(yloc.c, yloc.r)
        for adjloc in adjlocs:
            c,r = adjloc
            loc = yloc.clone(r=r,c=c)
            stuffinloc = self.desc_list_whats_here(loc)
            #self.debug('\n' + str(tuplerc) + ': "' +str(stuffinloc) + '"\n')
            if stuffinloc is not None and len(stuffinloc) > 0:
                nearbystufflist.append(stuffinloc)

        #self.debug(str(nearbystufflist))

        nearbystuffdesc = ''
        for i,stuff in enumerate(nearbystufflist):
            if i > 0:
                if i == len(nearbystufflist) - 1: nearbystuffdesc += ' and '
                else: nearbystuffdesc += ', '
            nearbystuffdesc += stuff

        if len(stuffhere) > 0:
            stuffhere = makehtmlsafe(stuffhere)
            s += 'You see here: '+str(stuffhere)+'.\n'
        if len(nearbystuffdesc) > 0:
            nearbystuffdesc = makehtmlsafe(nearbystuffdesc)
            s += 'You see nearby: '+str(nearbystuffdesc) + '.'
        if len(s) == 0:
            return None
        return s

    def desc_list_whats_here(self, loc):
        stuffhere = ''
        interesting_stuff = []
        stuffherelist = self.geo.list_whats_here(loc)
        can_think_stuff_interesting = hasattr(self.you,'think_this_interesting')
        if can_think_stuff_interesting:
            for thing in stuffherelist:
                if thing.is_invisible():
                    continue
                if self.you.think_this_interesting(thing):
                    interesting_stuff.append(thing.describe())

        cell = loc.level.grid[loc.r][loc.c]
        if cell.terrain is not None:
            interesting_stuff.append(cell.terrain.describe())

        for i,stuff in enumerate(interesting_stuff):
            if i > 0:
                if i == len(interesting_stuff) - 1:
                    stuffhere += ' and '
                else:
                    stuffhere += ', '
            stuffhere += stuff

        return stuffhere

    #TODO newgeo: should prob make method of GeoSystem:
    def are_these_in_same_cell(self, thingslist):
        reachedfirst = False
        model_th = None
        for th in thingslist:
            if th.loc is None or th.loc.any_fields_None():
                return False
            if not reachedfirst:
                reachedfirst = True
                model_th = th
                continue
            else:
                if th.loc == model_th.loc: continue
                else: return False
        return True

    def visit_with_every_lifeform_alive(self, fn2visit):
        def myfn2visit(thing):
            if isinstance(thing,Lifeform) and thing.is_alive():
                fn2visit(thing)
        self.geo.visit_with_all_things_in_world(myfn2visit)

    def core_engine_tick_tasks(self, event): # WebHack
        self.debug('core_engine_tick_tasks')
        # NOTE: by default, only things/entities in the activeregion should update or be informed during a tick(); Stuff in other regions will persist, and be queryable, but should be in an unchanging (and un-notified) state. The activelevel is always inside of the activeregion.
        def fn2visit(thing): thing.handle_event_tick(event)
        activeregion = self.geo.activelevel.region
        self.geo.visit_with_all_things_in_region(fn2visit, activeregion)

    def declare_game_loss_if_you_are_dead(self, event):
        if self.gamewin or self.gameloss:
            return
        if not self.you.is_alive():
            s = 'You died! You lose! Game over!'
            s = self.game_end_announce_format(s)
            self.feedback(s)
            self.ui.should_show_player_action_buttons = False
            self.gameloss = True

    def place_using_layout(self, baseloc, layout):
        things_placed = []
        level = baseloc.level
        region = baseloc.region
        baser = baseloc.r
        basec = baseloc.c
        lines = layout.split('\n')
        relr = 0
        for ln in lines:
            ln = ln.lstrip().rstrip()
            self.log('"' + str(ln) + '"')
            if len(ln) == 0:
                continue
            relc = 0
            for ch in ln:
                #self.debug('ch: ' + str(ch))
                if ch in self.layoutmap:
                    thingfactory = self.layoutmap[ch]
                    thing = thingfactory(self) #self is wh (instance of WebHack)
                    r = baser + relr
                    c = basec + relc
                    loc = baseloc.clone(r=r,c=c)
                    self.geo.put_on_map(thing,loc)
                    things_placed.append(thing)
                else:
                    if ch != '.':
                        self.log('unsupported char in layout so skipping: ' + str(ch))
                        self.log('self.layoutmap: '+str(self.layoutmap))
                relc += 1
            relr += 1
        return things_placed

    def do_any_of_this_thing_class_exist(self, thingclass):
        #print '\n\nchecking for exist of: %s\n\n' % thingclass
        #TODO refactor to iter through list of things in Groups group for that class
        #TODO if using above system, then all groups containing instances of descendant classes of thingklass should also be checked
        #TODO once converted to new geo, make sure checking ALL regions in world
        class FoundSomething(Exception):
            def __init__(self):
                Exception.__init__(self)

        class Foo:
            def __init__(self, wh, thingclass):
                self.wh = wh
                self.found = False
                self.thingclass = thingclass

            def fn2visit(self, r, c, level, region):
                #TODO should also recog instances of subclasses of thingclass
                cell = level.grid[r][c]
                if cell.is_thingclass_here(self.thingclass):
                    self.found = True
                    ex = FoundSomething()
                    raise ex

        f = Foo(self,thingclass)
        try:
            self.geo.visit_with_every_cell_in_world(f.fn2visit)
            #print 'returned gracefully from visit call, meaning it did NOT find anything'
        except FoundSomething, e:
            pass
            #print '\n\ncaught FoundSomething ex thrown from my visit call, which SHOULD mean it found something; ex: %s %s %s\n\n' % (e, id(e), e.__class__)
        #print 'returning ' + str(f.found)
        return f.found

    def are_at_least_this_many_instances_alive(self, somelifeformclass, minqty):
        class FoundMin: pass
        class Foo:
            def __init__(self, wh):
                self.wh = wh
                self.qty = 0
                self.answer = False

            def fn2visit(self, r, c, level, region):
                loc = Location(r,c,level,region)
                qtyhere = self.wh.how_many_there_and_alive(somelifeformclass,loc)
                self.qty += qtyhere
                if self.qty >= minqty:
                    self.answer = True
                    raise FoundMin()#'found min qty, so end early'

        f = Foo(self)
        try: self.geo.visit_with_every_cell_in_world(f.fn2visit)
        except FoundMin, e: pass #TODO bad! should raise specific exception subclass then catch it narrow here
        return f.answer

    def how_many_there_and_alive(self, somelifeformclass, loc):
        class Foo:
            qty = 0
            #def __init__(self):
                #self.qty = 0

            def fn2visit(self, thing):
                if thing.is_alive():
                    self.qty += 1

        f = Foo()
        self.geo.visit_for_every_instance_of_thingclass_there(f.fn2visit,somelifeformclass, loc)
        return f.qty

    def building_random(self, loc, w, h, door_qty_range=None, barricade_qty_range=None, place_chance=None, rnd_stuff=None, name=None, desc=None, layout_name=None):
        if layout_name is None:
            blueprints = self.get_or_gen_building_layout(w,h,door_qty_range,place_chance,barricade_qty_range=barricade_qty_range)
        else:
            blueprints = self.layouts_by_name[layout_name]
        components = self.place_using_layout(loc, blueprints)
        bldg = Building(loc.level, loc.c, loc.r, w, h, blueprints=blueprints, components=components)
        bldg.name = name
        bldg.desc = desc
        bldg.assertValid()
        zonekey = self.geo.add_zone(loc.level, bldg)
        if rnd_stuff:
            min_qty = 0
            if 'min_qty' in rnd_stuff:
                min_qty = rnd_stuff['min_qty']
            max_qty = 0
            if 'max_qty' in rnd_stuff:
                max_qty = rnd_stuff['max_qty']
            if 'group_name' in rnd_stuff:
                group_name = rnd_stuff['group_name']
                rnd_stuff_classes = thing_class_groups[group_name]
            else:
                rnd_stuff_classes = None
            r1 = loc.r + 1
            r2 = r1 + (h - 3)
            c1 = loc.c + 1
            c2 = c1 + (w - 3)
            self.make_and_put_rnd_stuff(min_qty, max_qty, r1, c1, c2-c1+1, r2-r1+1, loc.level, loc.region, thing_classes=rnd_stuff_classes)
        return bldg

    def make_and_put_rnd_stuff(self, min_qty, max_qty, br, bc, w, h, level, region, thing_classes=None):
        if thing_classes is None:
            thing_classes = thing_class_groups['rnd_stuff']
        qty = rnd_in_range(min_qty, max_qty)
        for q in xrange(qty):
            r = rnd_in_range(br, br+h-1)
            c = rnd_in_range(bc, bc+w-1)
            klass = random.choice(thing_classes)
            thing = klass(self)
            loc_cand = Location(r, c, level, region)
            if not thing.is_something_there_blocking_placement(loc_cand):
                self.geo.put_on_map(thing, loc_cand)

    def init_predefined_building_layouts(self):
        self.layouts = {}
        self.layouts_by_name = {}
        layouts = self.layouts

        path = DATADIR + 'layouts'
        fnames = os.listdir(path)
        for fname in fnames:
            if not fname.endswith('.dat'):
                continue
            pathname = '%s/%s' % (path,fname)
            lines = read_file_lines(pathname)
            h = len(lines)
            if h < 1:
                self.log('skipping load of layout file %s because line count < 1' % pathname)
                continue
            w = len(lines[0])
            if w < 1:
                self.log("skipping load of layout file %s because line 0's width < 1" % pathname)
                continue
            layout = '\n'.join(lines)
            key = (w,h)
            ll = None
            if key in layouts:
                ll = layouts[key]
            else:
                ll = []
                layouts[key] = ll
            ll.append(layout)
            name = fname.split('.dat')[0]
            self.layouts_by_name[name] = layout

    def get_or_gen_building_layout(self, w, h, door_qty_range=None, place_chance=None, barricade_qty_range=None):
        if door_qty_range is not None or place_chance is not None:
            return self.gen_building_layout(w,h,door_qty_range=door_qty_range,place_chance=place_chance,barricade_qty_range=barricade_qty_range)

        if chance(0,2): #TODO make like 50% chance once the code in the else block is ready
            return self.gen_building_layout(w,h,door_qty_range=door_qty_range,place_chance=place_chance,barricade_qty_range=barricade_qty_range)
        else:
            key = (w,h)
            layout = ''
            if key in self.layouts:
                lls = self.layouts[key]
                layout = random.choice(lls)
            else:
                layout = self.gen_building_layout(w,h,door_qty_range=door_qty_range,place_chance=place_chance,barricade_qty_range=barricade_qty_range)
            return layout

    def get_layout_char(self, klass):
        char = klass.char
        if hasattr(klass,'layout_char'):
            char = klass.layout_char
        return char

    def gen_building_layout(self, w, h, door_qty_range=None, place_chance=None, barricade_qty_range=None):
        if door_qty_range is None:
            door_qty_range = (1,4)
        if place_chance is None:
            place_chance = (1,3)
        if barricade_qty_range is None:
            barricade_qty_range = (0,0)
        #TODO separate door counting/logic/param from windows
        num = place_chance[0]
        den = place_chance[1]
        wallch = self.get_layout_char(Wall)
        doorch = self.get_layout_char(Door)
        windowch = self.get_layout_char(Window)
        barricade_ch = self.get_layout_char(Barricade)
        emptych = '.'
        s = ''
        min_doors, max_doors = door_qty_range
        min_barrs, max_barrs = barricade_qty_range
        door_qty = rnd_in_range(min_doors,max_doors)
        barr_qty = rnd_in_range(min_barrs,max_barrs)
        doors_placed = 0
        barricades_placed = 0
        #TODO refactor this whole method to build the map differently; instead first create a 2D array of empty spaces, then put walls in all outer edge cells, then add windows, then doors, then lastly barricades
        for r in range(h):
            for c in range(w):
                if r == 0 or r == (h-1) or c == 0 or c == (w-1): # if an outer edge
                    if doors_placed < door_qty: # Place Doors
                        if chance(num,den):
                            if doors_placed == 0: s += doorch # ensures at least 1 door
                            else:
                                ch = None
                                if chance(1,2): ch = doorch
                                else: ch = windowch
                                s += ch
                            doors_placed += 1
                        else: s += wallch

                    elif barricades_placed < barr_qty: # Place Barricades
                        if chance(num,den):
                            if barricades_placed == 0: s += barricade_ch # ensures at least 1 door
                            else:
                                ch = None
                                if chance(1,2): ch = barricade_ch
                                else: ch = windowch
                                s += ch
                            barricades_placed += 1
                        else: s += wallch

                    else:
                        s += wallch
                else: s += emptych
            s += '\n'
        return s

    def gen_thing_rectangle_layout(self, thingclass, w, h, pieces2miss=0, place_chance=None):
        ch = thingclass.char
        if hasattr(thingclass,'layout_char'):
            ch = thingclass.layout_char
        s = ''
        missed = 0
        for r in range(h):
            for c in range(w):
                if r == 0 or r == (h-1) or c == 0 or c == (w-1):
                    if missed < pieces2miss:
                        num = 1
                        den = 2
                        if place_chance is not None:
                            num = place_chance[0]
                            den = place_chance[1]
                        if chance(num,den):
                            s += '.'       
                            missed += 1
                        else:
                            s += str(ch)
                    else:
                        s += str(ch)
                else: s += '.'
            s += '\n'
        return s

    class StairwayPlacementFail(Exception):
        def __init__(self, loc1, loc2):
            self.loc1 = loc1
            self.loc2 = loc2

        def __str__(self):
            return 'could not get good loc for one or both stairs; loc1 %s, loc2 %s' % (self.loc1, self.loc2)

    class RoutePlacementFail(Exception):
        def __init__(self, loc1, loc2):
            self.loc1 = loc1
            self.loc2 = loc2

        def __str__(self):
            return 'could not get good loc for one or both routes; loc1 %s, loc2 %s' % (self.loc1, self.loc2)

    def stair_pair(self, loc1, loc2):
        'implied direction is up from loc1 to loc2'
        assert loc1 is not None
        assert loc2 is not None

        if isinstance(loc1,Level) and isinstance(loc2,Level):
            prevlev = loc1
            lev = loc2
            #TODO ensure no move blocking thing in r,c, or, re-roll
            loc1 = self.give_good_loc_for_stairs(prevlev)
            loc2 = self.give_good_loc_for_stairs(lev)
            if loc1 is None or loc2 is None:
                raise StairwayPlacementFail(loc1,loc2)

        assert isinstance(loc1,Location) and isinstance(loc2,Location)

        sts = (loc1,loc2,'up'), (loc2,loc1, 'down')
        for st in sts:
            loc_from = st[0]
            loc_to = st[1]
            dir = st[2]
            stairs = Stairway(self, loc_from, loc_to, dir)
            self.geo.put_on_map(stairs, loc_from)

    def give_good_loc_for_stairs(self, level):
        attempts = 0
        max_attempts = 500
        while attempts < max_attempts:
            c,r = level.area.get_rnd_xy()
            loc = Location(r,c,level,level.region)
            if not self.is_move_blocking_thing_there(loc):
                return loc
            attempts += 1
        else:
            return None

    def route_pair(self, loc1, loc2, edge_pref1=None, edge_pref2=None):
        'implied direction is up from loc1 to loc2'
        assert loc1 is not None
        assert loc2 is not None

        if isinstance(loc1,Level) and isinstance(loc2,Level):
            prevlev = loc1
            lev = loc2
            #TODO ensure no move blocking thing in r,c, or, re-roll
            loc1 = self.give_good_loc_for_route(prevlev,edge_pref1)
            loc2 = self.give_good_loc_for_route(lev,edge_pref2)
            if loc1 is None or loc2 is None:
                raise RoutePlacementFail(loc1,loc2)

        assert isinstance(loc1,Location) and isinstance(loc2,Location)

        sts = (loc1,loc2), (loc2,loc1)
        for st in sts:
            loc_from = st[0]
            loc_to = st[1]
            route = Route(self, loc_from, loc_to)
            self.geo.put_on_map(route, loc_from)

    def give_good_loc_for_route(self, level, edge_pref=None):
        attempts = 0
        max_attempts = 500
        while attempts < max_attempts:
            c,r = level.area.get_rnd_xy_on_edge(edge_pref)
            loc = Location(r,c,level,level.region)
            if not self.is_move_blocking_thing_there(loc) and \
                not self.geo.is_any_instance_of_thingclasses_there((Route,Stairway),loc):
                return loc
            attempts += 1
        else:
            return None

    def emit_event(self, event):
        self.debug('emit_event: %s' % event)
        self.ev.enqueue_event(event)

    def dispatch_usercmd(self, cmd, params):
        if cmd != 'again':
            if cmd == 'console':
                if 'command' in params:
                    command = params['command']
                    cmd, commandparams = self.parse_console_command(command)
                    newparams = {}
                    newparams.update(params)
                    del newparams['command']
                    newparams.update(commandparams)
                    params = newparams
                    if cmd != 'again':
                        self.last_usercmd = (cmd, params)
            else: self.last_usercmd = (cmd, params)
        wh = self
        method = None
        methodname = USERCMD_PREFIX + cmd
        if hasattr(wh,methodname):
            method = getattr(wh,methodname)
        if method is None:
            reason = 'unsupported user command "%s"' % cmd
            wh.log(reason)
            return False, reason, False
        wh.clear_feedback()
        #TODO add debug saying what method called and params passing it
        wh.debug('dispatch_usercmd is dispatching call to wh.%s with params: %s' % (methodname,params))
        cmd_response = method(**params)
        should_persist_to_disk = False
        replace_wh_with = None
        if cmd_response:
            if isinstance(cmd_response,type({})):
                if 'should_persist_to_disk' in cmd_response:
                    should_persist_to_disk = cmd_response['should_persist_to_disk']
                if 'replace_wh_with' in cmd_response:
                    replace_wh_with = cmd_response['replace_wh_with']
        # return value meanings: success, reason, should_persist_to_disk, replace_wh_with
        return True, None, should_persist_to_disk, replace_wh_with #successful dispatch; else if fail: False, '<reason>'

    def usercmd_console(self, command):
        if not self.cfg('devmode') and not self.gamemode.console_input_allowed():
            return
        s = 'We got from console: '+command
        self.feedback(s)
        self.debug(s)
        cmd, params = self.parse_console_command(command)
        self.log('we parsed as: cmd=%s params=%s' % (cmd, params))
        return #TODO wtf?!?!??! are the following lines unreachable code? is it not dispatching usecmd?!?!
        if cmd:
            success, reason, should_persist_to_disk, replace_wh_with = self.dispatch_usercmd(cmd,params)

    def parse_console_command(self, command):
        cmd = None
        params = None
        command = command.lstrip().rstrip()
        self.debug('before: ' + command)
        command = encode_whitespace_inside_quotes(command)
        self.debug('after: ' + command)
        toks = command.split(' ')
        if len(toks) > 0:
            cmd = toks[0]
            params = {}
            if len(toks) > 1:
                paramtoks = toks[1:]
                for pt in paramtoks:
                    k = None
                    v = None
                    if '=' in pt:
                        kvtoks = pt.split('=')
                        k = kvtoks[0]
                        if len(kvtoks) > 1:
                            v = kvtoks[1]
                        else:
                            v = None
                    else:
                        k = pt
                        v = True
                    params[k] = v
        return cmd, params

    def usercmd_sound_toggle(self):
        '''toggles on/off the playing of bg music and sound effects'''
        if not self.gamemode.bg_sound_allowed():
            self.feedback("bg sound not allowed in %s gamemode so no point toggling it on/off for you" % self.gamemode.mode_name())
            return

        v = self.toggle_cfg('bgmusic')
        self.feedback('play bg sounds: ' + str(v))
    autoui(usercmd_sound_toggle)

    def usercmd_change_ui(self):
        '''toggles UI style and layout; currently two choices: ClassicUI and AltUI (the default)'''
        if not self.gamemode.ui_change_allowed():
            return
        cur_ui_class_name = (hasattr(self,'ui_class_name_current') and self.ui_class_name_current) or 'ClassicUI'
        cur_ui_class = get_object(cur_ui_class_name,globals(),ClassicUI)

        new_ui_class_name = get_next_with_cycle(cur_ui_class_name,ui_class_names)
        new_ui_class = get_object(new_ui_class_name,globals(),ClassicUI)

        s = 'changing UI from %s to %s' % (cur_ui_class_name, new_ui_class_name)
        self.init_ui(ui_class_name=new_ui_class_name)
        self.ui.show_you_level()
        self.feedback(s)
        self.changed_since_last_render = True #TODO redundant?
    autoui(usercmd_change_ui)

    def usercmd_reset(self):
        '''reset game'''
        watch = StopWatch('usercmd_reset(): loading new wh initstate from disk: ')
        gameclass = self.cfg('reset_gameclass')
        modeclass = self.cfg('reset_modeclass')
        new_wh = return_new_wh_from_canned_initstates_chosen_randomly(gameclass,modeclass)
        self.debug(watch.stop())
        new_wh.changed_since_last_render = True
        new_wh.set_cfg('devmode',   self.cfg('devmode'))
        return {'replace_wh_with' : new_wh}

    def usercmd_skills(self):
        '''see your skills; for each skill, lists skill name, experience earned in it (xp), and level (how good you are at it)'''

        s = 'Your skills:\n'
        s += self.ai.sk.report_on_skills(self.you,delim='\n')
        self.feedback(s)
    autoui(usercmd_skills)

    def usercmd_story(self):
        '''see the game's background story and plot status'''

        s = 'Background\n \n%s\n \n' % self.introblurb
        s += 'Goals\n \n'
        if hasattr(self.you,'goals') and self.you.goals is not None:
            for g in self.you.goals:
                (desc, checkmethname, satisfied_ever) = g
                checkmeth = getattr(self,checkmethname)
                satisfied_now = checkmeth()
                s += '%s\n    (met ever: %s, met now: %s)\n \n' % (desc, satisfied_ever, satisfied_now)

        s += 'Plots\n \n'
        for plot in self.plots:
            report = plot.report_status()
            lns = report.split('\n')
            lns = map(lambda ln: '    '+ln, lns)
            s += '\n'.join(lns)
            #s += '\n' + plot.report_status()

        lns = s.split('\n')
        for ln in lns:
            self.feedback(ln)

    def usercmd_others_thoughts(self):
        class Foo:
            def __init__(self, wh):
                self.wh = wh
                self.report = ''

            def fn2visit(self, lf):
                if lf is self.wh.you: return
                thoughts = str(self.wh.ai.th.list_thoughts(lf))
                t = lf.describe() + ' is thinking: ' + str(thoughts)
                self.report += t + '\n'

        f = Foo(self)
        self.visit_with_every_lifeform_alive(f.fn2visit)
        self.feedback(f.report)
    autoui(devonly(usercmd_others_thoughts)) 

    def usercmd_look(self, relrow=0, relcol=0):
        class MyDCH(DirectionalCommandHelper):
            def do_for_one_candidate_case(self, lifeform):
                dmg = lifeform.hp_str()
                if dmg is None:
                    dmg = ''
                else:
                    dmg = ' (%s)' % dmg
                s = '%s%s' % (lifeform.full_describe(), dmg)
                self.wh.feedback(s)

        dch = MyDCH(self,relrow,relcol,Thing)
        dch.do()
    directional(usercmd_look)

    def usercmd_ask_follow(self, relrow=0, relcol=0):
        class MyDCH(DirectionalCommandHelper):
            def do_for_one_candidate_case(self, lifeform):
                if not lifeform.understands_speech():
                    self.wh.feedback_async(sentence(lifeform.describe() + ' does not give any indication of having understood what you just said'))
                    return
                if self.wh.ai.th.has_thought(lifeform,THINK_SHOULD_FOLLOW_YOU):
                    whatsaid = "I have already agreed to do that."
                    self.wh.say(lifeform, whatsaid)
                    return
                self.wh.ai.th.think(lifeform,THINK_SHOULD_FOLLOW_YOU)
                whatsaid = "Ok, I'll follow you."
                self.wh.say(lifeform, whatsaid)
        dch = MyDCH(self,relrow,relcol)
        dch.do()
        self.ev.tick_and_process_events()
    directional(usercmd_ask_follow)

    def usercmd_ask_not_follow(self, relrow=0, relcol=0):
        class MyDCH(DirectionalCommandHelper):
            def do_for_one_candidate_case(self, lifeform):
                if not lifeform.understands_speech():
                    self.wh.feedback_async(sentence(lifeform.describe() + ' does not give any indication of having understood what you just said'))
                    return
                if not self.wh.ai.th.has_thought(lifeform,THINK_SHOULD_FOLLOW_YOU):
                    whatsaid = 'I was not following you intentionally. Jerk.'
                    self.wh.say(lifeform, whatsaid)
                    return
                self.wh.ai.th.unthink(lifeform,THINK_SHOULD_FOLLOW_YOU)
                whatsaid = "Ok, I'll stop following you."
                self.wh.say(lifeform, whatsaid)
        dch = MyDCH(self,relrow,relcol)
        dch.do()
        self.ev.tick_and_process_events()
    directional(usercmd_ask_not_follow)

    def usercmd_ask_not_move(self, relrow=0, relcol=0):
        class MyDCH(DirectionalCommandHelper):
            def do_for_one_candidate_case(self, lifeform):
                if not lifeform.understands_speech():
                    self.wh.feedback_async(sentence(lifeform.describe() + ' does not give any indication of having understood what you just said'))
                    return
                if self.wh.ai.th.has_thought(lifeform,THINK_SHOULD_NOT_MOVE):
                    whatsaid = "I have already agreed to do that."
                    self.wh.say(lifeform, whatsaid)
                    return
                self.wh.ai.th.think(lifeform,THINK_SHOULD_NOT_MOVE)
                whatsaid = "Ok, I won't leave this spot."
                self.wh.say(lifeform, whatsaid)
        dch = MyDCH(self,relrow,relcol)
        dch.do()
        self.ev.tick_and_process_events()
    directional(usercmd_ask_not_move)

    def usercmd_ask_not_not_move(self, relrow=0, relcol=0):
        class MyDCH(DirectionalCommandHelper):
            def do_for_one_candidate_case(self, lifeform):
                if not lifeform.understands_speech():
                    self.wh.feedback_async(sentence(lifeform.describe() + ' does not give any indication of having understood what you just said'))
                    return
                if not self.wh.ai.th.has_thought(lifeform,THINK_SHOULD_NOT_MOVE):
                    whatsaid = 'I was not not moving out of some sort of intentional plan to not move. I just happened to be here right now. Jerk.'
                    self.wh.say(lifeform, whatsaid)
                    return
                self.wh.ai.th.unthink(lifeform,THINK_SHOULD_NOT_MOVE)
                whatsaid = "Ok, I won't necessarily stay in this spot anymore."
                self.wh.say(lifeform, whatsaid)
        dch = MyDCH(self,relrow,relcol)
        dch.do()
        self.ev.tick_and_process_events()
    directional(usercmd_ask_not_not_move)

    def usercmd_open(self, relrow=0, relcol=0):
        self.sub_usercmd_openclose('open',relrow,relcol)
    directional(usercmd_open)

    def usercmd_close(self, relrow=0, relcol=0):
        self.sub_usercmd_openclose('close',relrow,relcol)
    directional(usercmd_close)

    def sub_usercmd_openclose(self, openorclose, relrow=0, relcol=0):
        action = openorclose # should be 'open' or 'close'
        you = self.you
        loc = self.geo.determine_loc(you.loc, relrow, relcol)
        if loc is None:
            self.feedback('cant do that in that dir because it is not a valid location because not on the map')
            return

        class MyVisitorHolder(CandidateVisitorHolder):
            def meets_criteria(self, thing):
                return isinstance(thing, IsOpenCloseable)

        vh = MyVisitorHolder()
        self.geo.visit_with_every_thing_in_location(vh.fn2visit, loc)

        class MyCandidateHandleHelper(CandidateHandleHelper):
            def __init__(self, webhack, vh, action):
                CandidateHandleHelper.__init__(self, webhack, vh)
                self.action = action

            def handle_case_where_only_one_candidate(self, thing2open):
                wh = self.wh
                action = self.action
                expected_opened_state = True
                if action == 'open':
                    expected_opened_state = False
                th_desc = thing2open.basebasedesc
                if thing2open.opened != expected_opened_state:
                    what = 'opened'
                    if action == 'close':
                        what = 'closed'
                    wh.feedback('the %s is already %s' % (th_desc, what))
                else:
                    thing2open.toggle_openclose_state()
                    wh.feedback('you %s the %s' % (action, th_desc))
                    wh.ev.tick_and_process_events()

        chh = MyCandidateHandleHelper(self,vh,action)
        chh.do()
    # end of sub_usercmd_openclose() method

    def usercmd_lock(self, relrow=0, relcol=0):
        pass
    directional(usercmd_lock)

    def usercmd_unlock(self, relrow=0, relcol=0):
        pass
    directional(usercmd_unlock)

    def usercmd_pick(self, relrow=0, relcol=0):
        pass
    directional(usercmd_pick)

    def usercmd_barricade(self, relrow=0, relcol=0):
        relrow = int(relrow)
        relcol = int(relcol)
        r = self.you.loc.r + relrow
        c = self.you.loc.c + relcol
        region = self.you.loc.region
        level = self.you.loc.level
        area = level.area
        if not area.has_valid_coord(c,r):
            self.feedback('invalid barricade direction because target is off map')
            return
        barr_loc = Location(r,c,level,region)
        if self.is_move_blocking_thing_there(barr_loc):
            self.feedback('you cannot build a barricade there because something is blocking it')
            return
        #TODO require wood in inventory
        #TODO consume a wood in inventory
        barr = Barricade(self)
        self.geo.put_on_map(barr, barr_loc)
        self.feedback('You build some barricade')
        self.ev.tick_and_process_events()
    directional(usercmd_barricade)

    def usercmd_mark_safecell(self, relrow=0, relcol=0):
        relrow = int(relrow)
        relcol = int(relcol)
        r = self.you.loc.r + relrow
        c = self.you.loc.c + relcol
        region = self.you.loc.region
        level = self.you.loc.level
        area = level.area
        if not area.has_valid_coord(c,r):
            self.feedback('invalid barricade direction because target is off map')
            return
        loc = Location(r,c,level,region)
        cell = self.geo.get_cell(level,r,c)
        if not self.ai.fa.has_fact(cell,'safe'):
            self.ai.fa.add_fact(cell,'safe')
            self.feedback_async('after searching & studying that spot carefully you are now sure it is safe & secure: no zombies will come from there')
            self.ev.tick_and_process_events()
        else:
            self.feedback('you are already sure that spot is safe')
    directional(usercmd_mark_safecell)

    def usercmd_look_here(self):
        '''see description of your location/cell and surroundings (adj locations/cells)'''
        s = ''
        whatyousee = self.describe_your_surroundings()
        if whatyousee is None or len(whatyousee) == 0:
            self.log('\nwhatyousee: "' + str(whatyousee) + '"\n')
            s += "There's really nothing interesting to see in your vicinity"
        else:
            s += 'You look around you:\n'
            s += whatyousee
        self.feedback(s)
    autoui(usercmd_look_here)

    def usercmd_desc_self(self):
        '''read a description of yourself and your status, including physical traits or appearance'''
        s = 'You describe yourself:\n'
        you = self.you
        desc = you.describe()
        if len(desc) > 0:
            desc = desc[0:1].lower() + desc[1:]
        s += 'You are ' + desc + '.'
        if isinstance(you,Human):
            s += '\nYou are a human.'
        klassname = str(you.__class__)
        i = klassname.rfind('.')
        klassname = klassname[i+1:]
        s += '\nYou are a member of the ' + klassname + ' class of things.'
        if you.is_alive():
            s += '\nYou are alive.'
        else:
            s += '\nYou are dead.'
        s += '\nYou have '+str(you.hp)+' hp.'
        if isinstance(you,Corpse):
            s += '\nYou are a corpse.'
        s += '\nYou are a %s' % you.desc_human_traits() + '.'
        facts = self.ai.fa.get_facts(you)
        fs = ''
        factqty = len(facts)
        for i,f in enumerate(facts):
            if i > 0:
                if i == factqty - 1:
                    fs += ' and '
                else:
                    fs += ', '
            fs += f
        if len(fs) > 0:
            s += '\nYou are ' + fs + '.'
        s += '\nYour location is %s' % you.loc
        s += '\n' + you.id_thing_pp()
        self.feedback(s)
    autoui(usercmd_desc_self)

    def usercmd_yell(self):
        '''you yell something (not important what), as if to draw attention to yourself, or give the impression that you lack self-control or have insufficient language skills, or that your football team has just won'''
        self.feedback('You yell.')
        whatsaid = 'EEeeeerrryyyyghh!!!'
        self.say(self.you, whatsaid, volume=7)

        self.log('usercmd_yell, about to make/emit TPE')

        #self.emit_event( TestPlotEvent())
        #self.emit_event( IdentifyActiveAgentEvent())
        #self.emit_event( IsolateTheGeneEvent())
        #self.emit_event( MapTheThingEvent())
        #self.emit_event( IndexTheThingEvent())
        #self.emit_event( DesignManufactureProcessEvent())
        #self.emit_event( SetupFactoryEvent())
        #self.emit_event( ArrangeDistroMethodEvent())

        self.ev.tick_and_process_events()
    autoui(usercmd_yell)

    def usercmd_say_hello(self):
        '''you say 'Hello!' aloud'''
        self.usercmd_say('Hello!')
    autoui(usercmd_say_hello)

    def usercmd_say(self, what):
        self.log('usercmd_say: what = "%s"' % what)
        whatsaid = what.replace('_',' ')
        self.say(self.you, whatsaid)
        self.ev.tick_and_process_events()

    def say(self, who, whatsaid, volume=5, language=None):
        event = SpeechEvent(where=who.loc, who=who, volume=volume, whatsaid=whatsaid, language=language)
        self.emit_event(event)

    def yell(self, who, whatsaid, volume=7, language=None):
        event = SpeechEvent(where=who.loc, who=who, volume=volume, whatsaid=whatsaid, language=language, type=SoundEvent.YELL_TYPE)
        self.emit_event(event)

    def usercmd_save(self):
        '''save your game progress to disk (not useful 99% of the time)'''
        self.feedback('disabled command, prob delete entirely eventually')
        return

        self.debug('self.last_save: time=%s tock=%s' % (self.last_save_time, self.last_save_tock))
        if not self.gamemode.save_allowed():
            self.feedback('save is not allowed in %s mode' % self.gamemode.mode_name())
            return
        if self.ev.tock == 0:
            self.feedback('you cannot save on tock 0')
            return
        min_diff_time = self.cfg('min_secs_between_saves')
        now = None
        diff_time = None
        diff_tock = None
        if self.last_save_time:
            now = time.time()
            diff_time = now - self.last_save_time
            diff_tock = self.ev.tock - self.last_save_tock
        if not self.last_save_time or (diff_time >= min_diff_time and diff_tock >= 1):
            self.feedback('You issued a save command. Therefore, your current game state has just been saved to disk. If later the server restarts for any reason, you will (assuming a new software release did not occur in the meantime) be able to continue playing only from this point, and any subsequent progress made (after the save) will have been lost. It is recommended that you save after achieving any important accomplishment or story milestone. Keep in mind that you will not be allowed to save again for another %s seconds. This restriction helps reduce load on our machines.' % min_diff_time)
            if not now:
                now = time.time()
            self.last_save_time = now
            self.last_save_tock = self.ev.tock
            self.debug('self.last_save: time=%s tock=%s' % (self.last_save_time, self.last_save_tock))
            return {'should_persist_to_disk' : True}
        else:
            diffstr = secs_float_diff_to_summary_str(diff_time)
            self.feedback('You have already saved recently. (About %s ago, at tock %s.) You are allowed to save no more than once per %s seconds, and no more than once per tock. Try again later, if still desired then.' % (diffstr, self.last_save_tock, min_diff_time))
    #autoui(usercmd_save)
    usercmd_save.extra_show_reqs = ('may_you_save_now',)

    def may_you_save_now(self):
        return self.ev.tock != 0 and self.gamemode.save_allowed()

    def usercmd_timepass(self):
        self.emit_event(TimePassRequest())
        self.ev.tick_and_process_events()

    def execute_timepass(self, event):
        self.feedback('Time passes...')

    def usercmd_wait(self):
        '''you wait (doing nothing) and time passes (1 tock's worth)'''
        self.debug('usercmd_wait()')
        self.emit_event(YouWaitRequest())
        self.ev.tick_and_process_events()

    def execute_you_wait(self, event):
        self.feedback('You wait...')

    #def usercmd_crawl(self, relrow=0, relcol=0):
    #    pass
    #directional(movecmd(usercmd_crawl))

    #def usercmd_tiptoe(self, relrow=0, relcol=0):
    #    pass
    #directional(movecmd(usercmd_tiptoe))

    #def usercmd_run(self, relrow=0, relcol=0):
    #    pass
    #directional(movecmd(usercmd_run))

    def usercmd_walk(self, relrow=0, relcol=0):
        self.log('\nmove requested on: '+str(self.ev.tock) +'\n')
        self.debug('usercmd_walk()')
        relrow = int(relrow)
        relcol = int(relcol)
        if relrow == 0 and relcol == 0:
            self.feedback('relrow and relcol were 0 so that must mean you dont want to move')
            return
        you = self.you

        newloc = self.geo.determine_loc(you.loc, relrow, relcol)
        if newloc is not None:
            answer, reason = self.can_it_move_there(you,newloc)
            self.feedback('You try to move.')
            if answer is YES:
                event = MoveRequest(thing=you, r=newloc.r, c=newloc.c)
                self.emit_event(event)
                self.ev.tick_and_process_events()
            else:
                self.feedback("You can't move there because: %s." % reason)
        else:
            self.feedback("You can't move there because: %s." % 'it is not a valid location (not on the map)')
    directional(movecmd(usercmd_walk))

    def execute_move(self, move_event):
        self.debug('execute_move()')
        self.debug('\nmove executed on: %s\n' % self.ev.tock)

        event = move_event
        #TODO DRY violation between usercmd_move and execute_move because they both explicitly call that "can_it_move_there()" function; instead, the execute_move fn should have a metaattrib attached to which declarations what all it's preconditions are; then both inside execute_move and usercmd_move they can abstractly assert that all the required preconditions are satisfied
        #TODO convert the rnd zombie/NPC-human movement code to use this new move system

        you = self.you

        sc = sentence_capitalize # fn alias
        sen = sentence # fn alias

        thing = event.thing

        #TODO newgeo: allow movement between levels (of same or diff regions)
        #TODO newgeo: this would require getting it from the move event params

        oldloc = thing.loc
        oldr = oldloc.r
        oldc = oldloc.c
        oldlevel = oldloc.level
        oldregion = oldloc.region
        area = oldlevel.area
        w = area.w
        h = area.h

        newr = None
        newc = None
        newlevel = oldlevel
        newregion = oldregion

        relrow = None
        relcol = None

        if event.r is not None and event.c is not None:
            newr = event.r
            newc = event.c
            if event.level is not None:
                newlevel = event.level
            if event.region is not None:
                #TODO assert that if 'region' given event MUST ALSO have 'level'
                newregion = event.region
            #TODO check if r,c is valid coords in newlevel
        elif event.relrow is not None and event.relcol is not None:
            #NOTE if relrow/relcol given, it is always within same region/level
            relrow = int(event.relrow)
            relcol = int(event.relcol)
            if relrow == 0 and relcol == 0:
                self.feedback('relrow and relcol were 0 so that must mean you dont want to move')
                return
            else:
                (relrow, relcol) = area.safeify_rel_coords(oldc,oldr,relcol,relrow)
                newr = oldr + relrow
                newc = oldc + relcol
        else:
            self.error('bug: move event had neither (r,c) or (relrow,relcol) params so cant execute a move')
            return

        itv = self.lh.itverbify

        self.log( sc(itv(thing,'to be',tense='past')) + ' at ' + str(oldloc))

        newloc = Location(newr,newc,newlevel,newregion)
        answer, explanation = self.can_it_move_there(thing,newloc)
        if answer:
            self.geo.move_this_from_here_to_there(thing,newloc)
            #TODO following line needs to call a 'list things in cell' kind of method
            self.log( sc(itv(thing,'to be')) + ' now at ' + str(thing.loc))
            self.feedback( sen(thing.describe()+' moved') )
            self.exercise_skill(thing,'movement',1,'moved successfully')
        else:
            self.feedback(sc(thing.describe()+' cant move there because '+explanation))

    def is_move_blocking_thing_there(self, loc):
        level = loc.level
        cell = level.grid[loc.r][loc.c]
        for thing in cell.things:
            if thing.does_self_block_adding_thing_to_self_cell():
                return True
        return False

    def can_it_move_there(self, it, loc):
        r = loc.r
        c = loc.c
        level = loc.level
        region = loc.region
        alive = it.is_alive()
        valid_coords = level.area.has_valid_coord(c,r)
        cell = level.grid[r][c]
        no_blocker_there = not self.is_move_blocking_thing_there(loc)
        answer = alive and valid_coords and no_blocker_there 
        explanation = ''
        it_is = 'it is'
        if it == self.you: it_is = 'you are'
        if not alive: explanation += it_is + ' dead'
        if not no_blocker_there:
            if len(explanation) > 0: explanation += ' and '
            explanation += "there is a thing there that blocks movement into it's location"
        if not valid_coords:
            if len(explanation) > 0: explanation += ' and '
            explanation += 'the dest coords are not valid: '+str(loc)
        return answer, explanation

    def usercmd_wave_arms(self):
        '''you wave your arms in the air, as if to draw attention to yourself, or to provide air circulation in hopes of reducing odor'''
        pass
        #self.emit_event({'name':'wave_arms', 'who':self.you})
        #self.ev.tick_and_process_events()
    autoui(usercmd_wave_arms)

    def execute_wave_arms(self, event):
        #TODO handle 'who' param right
        self.feedback('You wave your arms in the air.')

    def usercmd_jump(self):
        '''jump/hop up-and-down once'''
        pass
        #self.emit_event({'name':'jump', 'who':self.you})
        #self.ev.tick_and_process_events()
    autoui(usercmd_jump)

    def execute_jump(self, event):
        #TODO handle 'who' param right
        self.feedback('You jump.')

    def usercmd_inventory_list(self):
        s = 'You are carrying:\n'
        inv = self.you.report_inventory()
        if len(inv) == 0:
            s = 'You are carrying nothing.'
        else:
            s += inv
        s = sentence(s)
        self.feedback(s)
    devonly(usercmd_inventory_list)

    def usercmd_inventory(self):
        '''toggles on/off a list of all things carried by you (including worn or wielded items, like clothing or weapons)'''
        self.ui.show_inventory = not self.ui.show_inventory
    autoui(usercmd_inventory)

    def usercmd_things_here(self):
        '''toggles on/off a list of all things in your location (on the ground in your cell)'''
        self.ui.show_things_here = not self.ui.show_things_here
    autoui(usercmd_things_here)

    def usercmd_pickup_all(self):
        '''pickup all items on ground in your cell (adds them to your inventory)'''
        #TODO impl note: for every thing in cell, ask the 'who' if he can pick it up, then in his method impl he (in part) asks the thing in question where it can be picked up, then inside that method it answers based on it's type, weight, whether it's mounted/attached permanently/strongly to where it is currently, etc)
        event = PickUpRequest(who=self.you, what='all')
        self.emit_event(event)
        self.ev.tick_and_process_events()
    autoui(usercmd_pickup_all)

    def usercmd_pickup(self, what):
        assert isinstance(what, type(''))

        self.log('usercmd_pickup: what="%s"' % what)
        who = self.you
        thing_id = what
        thing = self.find_thing_here_with_id(who.loc, thing_id)
        if thing is None:
            self.feedback("cant pick that up because no thing here with that ID ('%s')" % thing_id)
            return
        assert thing is not None and isinstance(thing, Thing) and thing.loc == who.loc
        event = PickUpRequest(who=who, what=thing)
        self.emit_event(event)
        self.ev.tick_and_process_events()

    def find_thing_here_with_id(self, loc, thing_id):
        assert loc is not None
        assert isinstance(thing_id,type(''))

        things = self.geo.list_whats_here(loc)
        for th in things:
            if th.id_thing() == thing_id:
                return th
        else: return None

    def execute_pickup_request(self, pickup_request):
        assert pickup_request is not None
        assert isinstance(pickup_request,PickUpRequest)

        req = pickup_request
        who = req.who
        what = req.what
        if what == 'all':
            self.do_pickup_all(who)
        else:
            self.do_pickup(who,what)

    def do_pickup_all(self, who):
        class Foo:
            def __init__(self, webhack, who):
                self.wh = webhack
                self.who = who

            def fn2visit(self, thing):
                if thing is not self.who:
                    self.wh.do_pickup(self.who,thing)
        f = Foo(self,who)
        self.geo.visit_with_every_thing_in_location(f.fn2visit,who.loc)

    def do_pickup(self, who, what):
        assert what is not who
        thing = what
        s = '%s to pickup %s' % (self.lh.itverbify(who,'to try'), thing.describe())
        s = sentence(s)
        trymsg = s
        if thing.can_be_picked_up():
            if who.can_you_pickup_this(thing):
                who.pickup(thing)
                s = '%s %s' % (self.lh.itverbify(who,'to pickup',tense='past'), thing.describe())
                self.feedbacksen(s)
            else:
                s = '%s\n%s cant pick up %s' % (trymsg, who.describe(), thing.describe())
                self.feedback_ifyou(who,s)
        else:
            s = '%s\n%s cannot be picked up' % (trymsg, thing.describe())
            self.feedback_ifyou(who,s)

    def usercmd_drop_all(self):
        '''drop all carried items to the ground'''
        event = DropRequest(who=self.you, where=self.you.loc, what='all')
        self.emit_event(event)
        self.ev.tick_and_process_events()
    autoui(usercmd_drop_all)

    def usercmd_drop(self, what):
        assert isinstance(what, type(''))
        self.log('usercmd_drop: what="%s"' % what)
        who = self.you
        thing_id = what
        thing = who.find_thing_in_inventory_with_id(thing_id)
        if thing is None:
            self.feedback("cant drop that because no thing in your inventory with that ID ('%s')" % thing_id)
            return
        assert thing is not None and isinstance(thing, Thing) and who.in_inventory(thing)
        event = DropRequest(who=who, where=who.loc, what=thing)
        self.emit_event(event)
        self.ev.tick_and_process_events()
    inventorythingusercmd(usercmd_drop)

    def execute_drop(self, drop_request):
        assert isinstance(drop_request,DropRequest)
        who = drop_request.who
        what = drop_request.what
        where = drop_request.where
        self.log('execute_drop() given drop_request with where: %s' % where)
        if not who.has_inventory():
            verb = self.lh.itverbify(who,'to carry')
            s = sentence('%s nothing' % verb)
            self.feedback_ifyou(who,s)
            return

        whatblurb = None
        if what == 'all':
            whatblurb = 'all your carried items'
            who.dropall(where)
        else:
            whatblurb = what.describe()
            try:
                who.drop(what,where)
            except DropFail, ex:
                s = sentence(str(ex))
                self.feedback_ifyou(who,s)

    def just_died_thing_should_drop_inventory(self, death_event):
        assert isinstance(death_event,DeathEvent)
        drop_request = DropRequest(what='all', who=death_event.who, where=death_event.where)
        self.execute_drop(drop_request)

    def usercmd_eat(self, what):
        assert isinstance(what, type(''))
        self.debug('usercmd_eat: what="%s"' % what)
        who = self.you
        thing_id = what
        thing = who.find_thing_in_inventory_with_id(thing_id)
        if thing is None:
            self.feedback("cant eat that because nothing in your inventory with that ID ('%s')" % thing_id)
            return
        assert thing is not None and isinstance(thing, Thing) and who.in_inventory(thing)
        if not isinstance(thing,Edible):
            self.feedback('that is not edible')
            return
        can_eat, reason = who.can_self_eat_this(thing)
        if not can_eat:
            self.feedback('You cannot eat that! %s' % reason)
            return
        edible = thing
        if edible.get_foodvalue() <= 0:
            self.feedback('that has no edible nutrition value left')
            return
        if who.has_full_stomach():
            self.feedback('You already have a full stomach.')
            return
        if who.has_empty_stomach():
            self.feedback('Your stomach was empty before eating this!')
        amount_ate = who.eat(edible)
        left = 'no edible nutrition value'
        if edible.get_foodvalue() > 0:
            left = 'about %s of nutrition' % edible.describe_foodvalue()
        self.feedback('You ate %s, gaining %s calories. There is %s left.' % (edible.describe(), amount_ate, left))
        if who.has_full_stomach():
            self.feedback('You now have a full stomach.')
        if edible.get_foodvalue() <= 0:
            self.feedback(sentence('%s is now gone' % edible.describe()))
            who.inventory_remove(edible)
            self.delete_thing(edible)
    inventorythingusercmd(usercmd_eat)

    def usercmd_use(self, what):
        assert isinstance(what, type(''))
        self.debug('usercmd_use: what="%s"' % what)
        who = self.you
        thing_id = what
        thing = who.find_thing_in_inventory_with_id(thing_id)
        if thing is None:
            self.feedback("cant use that because no thing in your inventory with that ID ('%s')" % thing_id)
            return
        assert thing is not None and isinstance(thing, Thing) and who.in_inventory(thing)
        if not isinstance(thing,Useable):
            self.feedback("it is not useable in that way")
            return
        result = who.use(thing)
        self.feedback('You %s' % result)
    inventorythingusercmd(usercmd_use)

    def usercmd_read(self, what):
        assert isinstance(what, type(''))
        self.debug('usercmd_read: what="%s"' % what)
        who = self.you
        thing_id = what
        thing = who.find_thing_in_inventory_with_id(thing_id)
        if thing is None:
            self.feedback("cant read that because no thing in your inventory with that ID ('%s')" % thing_id)
            return
        assert thing is not None and isinstance(thing, Thing) and who.in_inventory(thing)
        if not isinstance(thing,Readable):
            self.feedback("it is not readable")
            return
        body = thing.read_body()
        self.feedback('You read this from the %s:\n%s' % (thing.basebasedesc,body))
    inventorythingusercmd(usercmd_read)

    def usercmd_wear(self, what):
        assert isinstance(what, type(''))
        self.debug('usercmd_wear: what="%s"' % what)
        who = self.you
        thing_id = what
        thing = who.find_thing_in_inventory_with_id(thing_id)
        if thing is None:
            self.feedback("cant wear that because no thing in your inventory with that ID ('%s')" % thing_id)
            return
        assert thing is not None and isinstance(thing, Thing) and who.in_inventory(thing)
        if self.you.does_wear(thing):
            self.feedback('you are already wearing that')
            return
        self.you.wear(thing)
    inventorythingusercmd(usercmd_wear)

    def usercmd_unwear(self, what):
        assert isinstance(what, type(''))
        self.debug('usercmd_unwear: what="%s"' % what)
        who = self.you
        thing_id = what
        thing = who.find_thing_in_inventory_with_id(thing_id)
        if thing is None:
            self.feedback("cant unwear that because no thing in your inventory with that ID ('%s')" % thing_id)
            return
        assert thing is not None and isinstance(thing, Thing) and who.in_inventory(thing)
        if not self.you.does_wear(thing):
            self.feedback('you are not wearing that, so cannot take it off')
            return
        self.you.unwear(thing)
    inventorythingusercmd(usercmd_unwear)

    def usercmd_wield(self, what):
        assert isinstance(what, type(''))
        self.debug('usercmd_wield: what="%s"' % what)
        who = self.you
        thing_id = what
        thing = who.find_thing_in_inventory_with_id(thing_id)
        if thing is None:
            self.feedback("cant wield that because no thing in your inventory with that ID ('%s')" % thing_id)
            return
        assert thing is not None and isinstance(thing, Thing) and who.in_inventory(thing)
        if self.you.does_wield(thing):
            self.feedback('you are already wielding that')
            return
        self.you.wield(thing)
    inventorythingusercmd(usercmd_wield)

    def usercmd_unwield(self, what):
        assert isinstance(what, type(''))
        self.debug('usercmd_unwield: what="%s"' % what)
        who = self.you
        thing_id = what
        thing = who.find_thing_in_inventory_with_id(thing_id)
        if thing is None:
            self.feedback("cant unwield that because no thing in your inventory with that ID ('%s')" % thing_id)
            return
        assert thing is not None and isinstance(thing, Thing) and who.in_inventory(thing)
        if not self.you.does_wield(thing):
            self.feedback('you are not wielding that, so cannot unwield it')
            return
        self.you.unwield(thing)
    inventorythingusercmd(usercmd_unwield)

    def usercmd_stairs(self):
        "take the stairway up/down (this button only appears if stairway at your location)"
        stairway = self.get_thing_of_this_class_where_you_are(Stairway)
        if stairway is not None:
            direction = stairway.direction
            event = StairsRequest(who=self.you, direction=direction, stairway=stairway)
            self.emit_event(event)
            self.ev.tick_and_process_events()
        else: self.feedback('There are no stairs here.')
    autoui(usercmd_stairs)
    usercmd_stairs.extra_show_reqs = ('are_you_at_stairway',)

    def are_you_at_stairway(self):
        stairs = self.get_thing_of_this_class_where_you_are(Stairway)
        return not stairs is None

    def get_thing_of_this_class_where_you_are(self, thingclass):
        you = self.you
        cell = you.loc.level.grid[you.loc.r][you.loc.c]
        for thing in cell.things:
            if isinstance(thing,thingclass):
                return thing
        return None

    def usercmd_route(self):
        "follow this path to its destination (this button only appears if a path/route/trail leads away from your location)"
        route = self.get_thing_of_this_class_where_you_are(Route)
        if route is not None:
            event = RouteRequest(who=self.you, route=route)
            self.emit_event(event)
            self.ev.tick_and_process_events()
        else: self.feedback('There are no routes leading away from here.')
    autoui(usercmd_route)
    usercmd_route.extra_show_reqs = ('are_you_at_route',)
    usercmd_route.label = 'follow path'

    def are_you_at_route(self):
        route = self.get_thing_of_this_class_where_you_are(Route)
        return not route is None

    def label_for_usercmd(self, cmd):
        attrname = USERCMD_PREFIX + cmd
        method = getattr(self,attrname)
        label = cmd.replace('_',' ')
        label = getattr(method,'label',label)
        return label


#######################
# WebHack class - end #
#######################

###################
# Attacks - begin #
###################

class Attack:
    def __init__(self, wh, attacker, target, skill):
        assertNotDirectInstantiate(self, Attack)
        assertNotNone('wh',wh)
        assertNotNone('attacker',attacker)
        assert isinstance(attacker,Thing)
        assertNotNone('target',target)
        assert isinstance(target,Thing)
        assertNotNone('skill',skill) #assert that skill recognized by SkillSystem AND in AttackAttempt.SKILLS
        self.wh = wh
        self.attacker = attacker
        self.target = target
        self.skill = skill

    def do(self):
        wh = self.wh
        you = wh.you
        attacker = self.attacker
        target = self.target
        tardesc = target.describe()
        skill = self.skill

        self.feedbackitvsen(attacker,'to attack', rest = ' %s!' % tardesc)
        if chance(1,2):
            wh.exercise_skill(attacker,skill,1,'attack attempt')
        num, denom = attacker.atkhitchance #TODO should depend on situation
        wh.log('chance: '+str( (num,denom,) ))
        does_hit = chance(num,denom)
        if attacker.does_always_hit():
            does_hit = True
        if not does_hit:
            self.feedbackitvsen(attacker, 'to miss')
            return
        wh.exercise_skill(attacker,skill,1,'successful hit')
        dmg, max_dmg = self.get_damage_to_apply()
        if dmg > 0:
            wh.exercise_skill(attacker,skill,1,'did dmg')
            if dmg >= max_dmg and max_dmg > 1: # TODO do more than this to reduce abuse via weak weapons
                wh.exercise_skill(attacker,skill,1,'made max dmg attack')
        self.dmg = dmg
        self.apply_damage()

    def get_damage_to_apply(self):
        wh = self.wh
        attacker = self.attacker
        target = self.target
        weapon = self.get_weapon_used_in_attack()
        max_dmg = 0
        dmg = max_dmg
        if weapon is None: # so attack is an unarmed melee attack
            self.feedback('unarmed attack')
            max_dmg = attacker.atkdmg #TODO should be range and depend on situation
            dmg = randrangewith(max_dmg)
        else:
            self.feedback('weapon attack: %s' % weapon.basebasedesc)
            if isinstance(weapon,Weapon):
                max_dmg = weapon.get_max_dmg()
                dmg = randrangewith(max_dmg)
                self.feedback('weapon does %s dmg (out of max possible %s)' % (dmg, max_dmg))
            else:
                self.feedback('wielded item is not a weapon: %s' % weapon)
        if attacker.does_always_do_kill_dmg():
            dmg = target.hp
        return dmg, max_dmg

    def get_weapon_used_in_attack(self):
        attacker = self.attacker
        if attacker.has_wielded():
            wielded = attacker.wielded_list()
            return wielded[0]
        return None

    def apply_damage(self):
        wh = self.wh
        att = self.attacker
        tar = self.target
        tardesc = tar.describe()
        dmg = self.dmg
        if tar.is_invuln():
            failreason = 'cant apply damage %s to target %s because it is invuln' % (dmg, tardesc)
            wh.debug('\n%s\n' % failreason)
            return False, 'failed: %s' % failreason
        target_destroyed_before = tar.is_destroyed()
        amt_dmg_reduced, reason_dmg_reduced = self.get_damage_reduced()
        if amt_dmg_reduced > 0:
            dmg_orig = dmg
            dmg -= amt_dmg_reduced
            if dmg < 0:
                dmg = 0
            self.feedbacksen('attack damage %s reduced by %s due to %s' % (dmg_orig, amt_dmg_reduced, reason_dmg_reduced))
        if dmg > 0:
            tar.hp -= dmg
        att_poss_prefix = wh.lh.possessivify(att)
        dmgblurb = 'no'
        senend = '.'
        if dmg > 0:
            dmgblurb = '%s HP of' % dmg
            senend = '!'
        self.feedbacksen('%s attack caused %s damage to %s%s' % (att_poss_prefix, dmgblurb, tardesc, senend))
        whathappened = None
        if dmg > 0 and tar.is_destroyed() and not target_destroyed_before:
            awardreason = 'destroyed target'
            if isinstance(tar, Lifeform) and not isinstance(tar, Corpse):
                awardreason = 'killed opponent'
            wh.exercise_skill(att, self.skill, 1, awardreason)
            self.tar_loc_orig = tar.loc.clone()
            wh.geo.remove_from_map(tar)
            wh.delete_thing(tar)
            verb = 'destroyed'
            if isinstance(tar, Lifeform) and not isinstance(tar, Corpse):
                verb = 'killed'
            self.feedbacksen('%s %s %s!' % (att.describe(), verb, tardesc))
            tarloc = self.tar_loc_orig
            if isinstance(tar, Lifeform):
                wh.geo.ensure_in_cell_desc('There is a bloody mess here.', tarloc.level, tarloc.r, tarloc.c)
            whathappened = self.do_kill_result()
        else:
            whathappened = 'damaged target but not killed/destroyed it'
        return True, 'success: %s' % whathappened

    def feedbackitvsen(self, who, verb, plurality='singular', tense='present', rest=''):
        verbportion = self.wh.lh.itverbify(who, verb, plurality, tense)
        s = verbportion + rest
        self.feedbacksen(s)

    def feedbacksen(self, msg):
        self.feedback(sentence(msg))

    def feedback(self, msg):
        self.wh.feedback_ifanyyou((self.attacker,self.target), msg)

    def get_damage_reduced(self):
        total_amount = 0
        reasons = ''
        first_worn_bonus = True
        if isinstance(self.target, HasInventory):
            for th in self.target.worn_set():
                amount = th.damage_absorbs()
                if amount > 0:
                    prefix = ''
                    if first_worn_bonus:
                        first_worn_bonus = False
                        prefix = 'wearing '
                    total_amount += amount
                    reasons = prefix + stradd(reasons, ", ", '%s (-%s)' % (th.describe(),amount))
        return total_amount, reasons

    def do_kill_result(self):
        return None

class NormalAttack(Attack):
    def do_kill_result(self):
        tar = self.target
        tarloc = self.tar_loc_orig
        whathappened = None
        #TODO the 3-cases below should each become method bodies of Corpse, Lifeform and Thing, respectively, with same method names.
        if isinstance(tar,Corpse):
            #NOTE if vic was Your Corpse, this will leave wh.you pointing at an object which isn't on the map, because your corpse was removed from it -- like a dangling pointer (if I remember my C/C++ terminology correctly)
            event = DestroyedEvent(what=tar, where=tarloc)
            self.wh.emit_event(event)
            if self.attacker is self.wh.you:
                self.wh.feedbacksen('You destroyed the corpse.')
            if tar is self.wh.you or tar.origlifeform is self.wh.you:
                self.wh.feedbacksen('Your corpse was destroyed. How rude!')
            whathappened = 'corpse destroyed'
        elif isinstance(tar,Lifeform):
            event = DeathEvent(who=tar, where=tarloc)
            self.wh.emit_event(event)
            if tar is self.wh.you:
                self.wh.feedbacksen('YOU WERE KILLED!!!')
            self.wh.feedbacksen('You hear the sound of a body falling down.')
            corpseloc = tarloc.clone()
            corpse = self.wh.put_corpse_on_map_for_lifeform(tar, corpseloc)
            if tar is self.wh.you:
                self.wh.you = corpse
            whathappened = 'victim killed'
        else: # non-Corpse, non-Lifeform thing, like a wall, door or item
            event = DestroyedEvent(what=tar, where=tarloc)
            self.wh.emit_event(event)
            self.wh.feedbacksen(tar.describe() + ' was destroyed.')
            whathappened = 'thing destroyed'
        return whathappened

class ZombieAttack(Attack):
    def do_kill_result(self):
        tar = self.target
        tarloc = self.tar_loc_orig
        newzombie = zh_Zombie(self.wh,tar)
        if tar is self.wh.you:
            self.wh.you = newzombie
        self.wh.geo.put_on_map(newzombie, tarloc)
        s = sentence('%s turned %s into a zombie!' % (self.attacker.describe(), tar.describe()))
        self.wh.feedback_ifanyyou((self.attacker,tar), s)
        if tar is self.wh.you:
            self.wh.feedbacksen('YOU TURNED INTO A ZOMBIE!!!')
        event = ZombieEvent(who=tar, where=tarloc)
        self.wh.emit_event(event)
        whathappened = 'victim turned into a zombie'
        return whathappened

#################
# Attacks - end #
#################

##############
# AI - begin #
##############

class LifeformMind(Mind):
    def __init__(self, whosemind):
        Mind.__init__(self)
        self.whosemind = whosemind
        self.action_choice_weights_base = {}
        wt = self.action_choice_weights_base
        wt['do_nothing'] = 5
        wt['talk'] = 4
        wt['move'] = 3
        wt['attack'] = 1

    def tick(self):
        mymind = self
        me = mymind.whosemind
        mydesc = me.describe()
        myloc = me.loc
        wh = me.wh
        ai = wh.ai
        theplayer = wh.you
        # determine choices of action
        # TODO do this better (build fuller, more varied and accurate list):
        action_choices, reject_reasons = self.get_choices_of_action()
        # pick an action (current scheme: pick totally at random)
        #TODO do this better (determine which choice maximizes benefit (and/or minimizes harm) to your body, goals and interests) at this moment in time:
        #TODO take into account: in ongoing combat? pursuing goals? in middle of long-running task (that spans 1+ ticks in order to complete it)? whether you want to continue, ignore/pause or totally abandon/discard a pre-existing task or goal?
        chosen_action = random.choice(action_choices)
        self.debug_report(chosen_action,action_choices,reject_reasons)
        chosen_action.do()

    def debug_report(self, chosen_action, action_choices, reject_reasons):
        me = self.whosemind
        wh = me.wh
        if not wh.cfg('debug_ai_zombie'):
            return
        player = wh.you
        if isinstance(me,zh_Zombie) and wh.geo.is_adj_on_same_level(me,player):
            s = 'zombie AI report: '
            s += '%s %s' % (me.id_thing_pp(), wh.desc_loc_rel_you(me))
            s += ' chose %s' % bare_class_name(chosen_action.__class__)
            acs = ''
            for ac in action_choices:
                if len(acs) > 0: acs += ','
                acs += bare_class_name(ac.__class__)
            s += ' (' + acs + ')'
            s += ' rejected reasons: %s' % reject_reasons
            wh.feedback(s)

    def get_choices_of_action(self):
        mymind = self
        me = self.whosemind
        wh = me.wh
        ai = me.wh.ai
        action_choices = []
        wt = self.action_choice_weights_base
        reasons = []

        ac = DoNothingAC(self)
        if ac.is_possible_to_do_now():
            self.add_choice(ac, wt['do_nothing'], action_choices)

        if ai.would_say_something_aloud_randomly_now(me):
            ac = TalkAC(self)
            if ac.is_possible_to_do_now():
                self.add_choice(ac, wt['talk'], action_choices)

        if ai.th.has_thought(me,THINK_SHOULD_FOLLOW_YOU):
            loc = wh.you.loc
            ac = MoveCloserToSomewhereAC(self,loc)
            if ac.is_possible_to_do_now():
                weight = 40
                self.add_choice(ac, weight, action_choices)

        if mymind.does_want_to_move_randomly_now():
            ac = MoveRandomlyAC(self)
            if ac.is_possible_to_do_now():
                self.add_choice(ac, wt['move'], action_choices)

        ac = ScienceAC(self)
        if ac.is_possible_to_do_now():
            self.add_choice(ac, wt['science'], action_choices)

        #TODO if multiple attacks possible (against diff targets), include each as separate AttackAC instances in the list:
        ac = AttackAC(self)
        possible, reason = ac.is_possible_to_do_now()
        if possible:
            self.add_choice(ac, wt['attack'], action_choices)
        else:
            reasons.append('rejected AttackAC due to ' + reason)

        return action_choices, reasons

    def add_choice(self, choice, weight, choiceslist):
        for i in range(weight):
            choiceslist.append(choice)

    def is_prey(self, thing):
        return self.whosemind.would_self_attack_this_thing(thing)

    def best_adj_cell_to_move_to(self):
        rr = None
        cc = None
        me = self.whosemind
        myloc = me.loc
        level = myloc.level
        region = myloc.region
        mr = myloc.r
        mc = myloc.c

        #TODO build list of prey thing instances to consider
        prey = []
        adjcells = myloc.level.area.adj_cells(mc,mr,griddist=6)
        for adjcell in adjcells:
            c,r = adjcell
            cell = level.grid[r][c]
            for th in cell.things:
                if self.is_prey(th):
                    prey.append(th)
        if len(prey) == 0:
            # TODO pick one at random instead of returning None
            return None, None

        #TODO for each of my adj cells, calculate which is closest to any prey in list built above
        adjcells = self.whosemind.loc.level.area.adj_cells(mc,mr)
        data = {}
        dists = []
        for adjcell in adjcells:
            c,r = adjcell
            dest = Location(r, c, level, region)
            if me.is_something_there_blocking_placement(dest):
                #don't even consider this cell because cant move there anyway
                continue
            if me.is_something_there_you_would_attack(dest):
                #don't even consider this cell for movement because has something I would attack instead, so should not move right now anyway
                continue
            for p in prey:
                d = dist(r,c, p.loc.r, p.loc.c)
                k = (r,c)
                data[k] = d
                dists.append(d)
        if len(dists) == 0:
            # if this happens, it means that all adj cells were either blocked or contained prey, so therefore can't/shouldn't move
            return None, None

        dists.sort()
        nearestpreydist = dists[0]
        best_rcs = []
        for k in data:
            v = data[k]
            if v == nearestpreydist:
                best_rcs.append(k)
        #TODO instead of picking at random, pick best among them according to some other qualities, to help break the tie and truly truly pick the best:
        #print '\n\nbest_rcs %s\n\n' % best_rcs
        if len(best_rcs) == 0: return None, None
        r,c = random.choice(best_rcs)
        return r,c

    def does_want_to_move_randomly_now(self):
        me = self.whosemind
        if not me.is_alive(): return False
        if me.wh.ai.th.has_thought(me,THINK_SHOULD_NOT_MOVE):
            return False
        n,d = me.get_odds_of_rnd_move()
        return chance(n,d)

    def sound_reaches_me(self, sound_event): #TODO make it do something
        pass
#end of LifeformMind

class HumanMind(LifeformMind):
    def __init__(self, whosemind):
        LifeformMind.__init__(self,whosemind)
        wt = self.action_choice_weights_base
        wt['do_nothing'] = 6
        wt['talk'] = 10
        wt['move'] = 8
        wt['attack'] = 1

class GuardMind(HumanMind):
    def __init__(self, whosemind):
        HumanMind.__init__(self,whosemind)
        wt = self.action_choice_weights_base
        wt['do_nothing'] = 2
        wt['talk'] = 3
        wt['move'] = 8
        wt['attack'] = 10

class ScientistMind(HumanMind):
    def __init__(self, whosemind):
        HumanMind.__init__(self,whosemind)
        wt = self.action_choice_weights_base
        wt['do_nothing'] = 2
        wt['talk'] = 3
        wt['move'] = 8
        wt['science'] = 10

class ZombieMind(LifeformMind):
    def __init__(self, whosemind):
        LifeformMind.__init__(self,whosemind)
        wt = self.action_choice_weights_base
        wt['do_nothing'] = 1
        wt['talk'] = 2
        wt['move'] = 6
        wt['attack'] = 12

class AnimalMind(LifeformMind):
    def __init__(self, whosemind):
        LifeformMind.__init__(self,whosemind)
        wt = self.action_choice_weights_base
        wt['do_nothing'] = 6
        wt['talk'] = 0
        wt['move'] = 20
        wt['attack'] = 2

class ActionChoice:
    def __init__(self, lifeformmind, params={}):
        self.lm = lifeformmind
        self.params = params

    def is_possible_to_do_now(self):
        return True

    def do(self):
        pass

class DoNothingAC(ActionChoice):
    def is_possible_to_do_now(self):
        return True

    def do(self):
        pass #NOTE: no-op by intent

class ScienceAC(ActionChoice):
    def is_possible_to_do_now(self):
        return 'science' in self.lm.skills

    def do(self):
        mymind = self.lm
        me = mymind.whosemind
        mydesc = me.describe()
        myloc = me.loc
        wh = me.wh
        ai = wh.ai
        theplayer = wh.you
        wh.feedback('%s does science' % mydesc)

class MoveCloserToSomewhereAC(ActionChoice):
    def __init__(self, lifeformmind, targetloc):
        ActionChoice.__init__(self, lifeformmind)
        self.targetloc = targetloc
        self.movenow_loc = None

    def is_possible_to_do_now(self):
        mymind = self.lm
        me = mymind.whosemind
        myloc = me.loc
        mylevel = myloc.level
        myr = myloc.r
        myc = myloc.c
        if myloc == self.targetloc: return False
        #TODO below doesnt account for diff levels - I should make this work right when targetloc is on a diff level from a thing's current level, and in that case the thing is willing/capable of going up/down stairs to get there, for example
        d = dist(myloc.r,myloc.c, self.targetloc.r,self.targetloc.c)
        cant_move_there = me.is_something_there_blocking_placement(self.targetloc)
        if d == 1 and cant_move_there: return False
        adj_rcs = mylevel.area.adj_cells(myc, myr)
        cand_locs = [] # cand means candidate
        #TODO also, only consider adj cells that are CLOSER to target:
        for adj_rc in adj_rcs:
            c,r = adj_rc
            loc = myloc.clone(r=r,c=c)
            if not me.is_something_there_blocking_placement(loc):
                cand_locs.append(loc)
        if len(cand_locs) == 0: return False
        closest_dist = None
        closest = []
        for loc in cand_locs:
            d = dist(loc.r,loc.c, self.targetloc.r,self.targetloc.c)
            if closest_dist is None:
                closest_dist = d
                closest.append(loc)
            else:
                if d == closest_dist:
                    closest.append(loc)
                elif d < closest_dist:
                    closest_dist = d
                    closest = [loc]
        #TODO pick among those in smarter way:
        self.movenow_loc = random.choice(closest)
        return True

    def do(self):
        me = self.lm.whosemind
        dest = self.movenow_loc
        me.wh.debug('A FOLLOWER MOVES CLOSER TO YOU; to: %s' % dest)
        me.wh.geo.move_this_from_here_to_there(me, dest)

class TalkAC(ActionChoice):
    def is_possible_to_do_now(self):
        return True

    def do(self):
        mymind = self.lm
        me = mymind.whosemind
        mydesc = me.describe()
        myloc = me.loc
        wh = me.wh
        ai = wh.ai
        theplayer = wh.you
        whatsaid = ai.give_something_to_say_aloud(me)
        speech_volume = 5 #TODO rnd within range defined by a me field
        wh.say(me, whatsaid, volume=speech_volume)

class MoveRandomlyAC(ActionChoice):
    def is_possible_to_do_now(self):
        return True

    def do(self):
        mymind = self.lm
        me = mymind.whosemind
        mydesc = me.describe()
        myloc = me.loc
        r = myloc.r
        c = myloc.c
        wh = me.wh
        level = myloc.level
        region = myloc.region
        area = level.area
        wh.log(mydesc + ' moves')
        oldr = r
        oldc = c
        dest = None
        best_r, best_c = mymind.best_adj_cell_to_move_to()
        if best_r is None:
            relrow = random.randrange(3) - 1
            relcol = random.randrange(3) - 1
            relrow, relcol = area.safeify_rel_coords(oldc, oldr, relcol, relrow)
            newc = oldc + relcol
            newr = oldr + relrow
            dest = Location(newr, newc, level, region)
            if me.is_something_there_blocking_placement(dest):
                wh.log(mydesc + " can't move there")
                return
        else:
            dest = Location(best_r, best_c, level, region)

        if me.is_something_there_you_would_attack(dest):
            wh.log(mydesc + " won't move there because has thing would attack")
            return
        wh.geo.move_this_from_here_to_there(me, dest)

class AttackAC(ActionChoice):
    def __init__(self, lifeformmind):
        ActionChoice.__init__(self, lifeformmind)
        me = self.lm.whosemind
        self.params['who'] = me

    def is_possible_to_do_now(self):
        target = self.lm.whosemind.identify_good_attack_target()
        if target is not None:
            self.params = dict(self.params)
            #TODO determine if I can eliminate this victim param if not needed:
            self.params['victim'] = target
            me = self.params['who']
            self.attack_attempt = AttackAttempt(who=me,target=target)
            answer = self.lm.whosemind.wh.ev.meet_event_execute_reqs(self.attack_attempt)
            reason = (not answer and 'did not meet event execute reqs') or ''
            return answer, reason
        else: return False, 'could not identify good attack target'

    def do(self):
        self.lm.whosemind.wh.execute_attack(self.attack_attempt)

############
# AI - end #
############

class CandidateVisitorHolder:
    def __init__(self):
        self.visited_ever = False
        self.candidates = []

    def fn2visit(self, thing):
        log('\n%s\n' % thing.describe())
        self.visited_ever = True
        if self.meets_criteria(thing):
            self.candidates.append(thing)

    def meets_criteria(self, thing):
        return True

class CandidateHandleHelper:
    def __init__(self, webhack, vh):
        self.wh = webhack
        self.vh = vh

    def do(self):
        wh = self.wh
        vh = self.vh
        if not vh.visited_ever:
            self.handle_case_where_no_things_there()
        elif len(vh.candidates) == 0:
            self.handle_case_where_no_candidates_there()
        elif len(vh.candidates) > 1:
            self.handle_case_where_multiple_candidates(vh.candidates)
        else:
            thing = vh.candidates[0]
            self.handle_case_where_only_one_candidate(thing)

    def handle_case_where_no_things_there(self):
        self.wh.feedback('there is nothing there')

    def handle_case_where_no_candidates_there(self):
        self.wh.feedback('there is nothing there that applies')

    def handle_case_where_multiple_candidates(self, things):
        self.wh.feedback('there are several things there which might apply so not sure which you intended to target')

    def handle_case_where_only_one_candidate(self, thing):
        pass
# end of CandidateHandleHelper class

class DirectionalCommandHelper:
    def __init__(self, webhack, relrow, relcol, candidatethingclassreq=None):
        self.wh = webhack
        self.relrow = relrow
        self.relcol = relcol
        if candidatethingclassreq is None:
            self.thingclass = Lifeform
        else:
            self.thingclass = candidatethingclassreq

    def do(self):
        wh = self.wh
        you = wh.you
        loc = wh.geo.determine_loc(you.loc, self.relrow, self.relcol)
        if loc is None:
            wh.feedback('cant do that in that dir because it is not a valid location because not on the map')
            return

        class MyVisitorHolder(CandidateVisitorHolder):
            def __init__(self, thingclass):
                CandidateVisitorHolder.__init__(self)
                self.thingclass = thingclass
            def meets_criteria(self, thing):
                return isinstance(thing, self.thingclass)

        vh = MyVisitorHolder(self.thingclass)
        self.wh.geo.visit_with_every_thing_in_location(vh.fn2visit, loc)

        class MyCandidateHandleHelper(CandidateHandleHelper):
            def __init__(self, wh, vh, dch):
                CandidateHandleHelper.__init__(self,wh,vh)
                self.dch = dch

            def handle_case_where_only_one_candidate(self, thing):
                self.dch.do_for_one_candidate_case(thing)

        chh = MyCandidateHandleHelper(wh,vh,self)
        chh.do()

    def do_for_one_candidate_case(self, thing):
        pass
# end of DirectionalCommandHelper class

##############
# UI - begin #
##############

class UI:
    def __init__(self, webhack):
        self.wh = webhack
        self.shownlevel = None
        self.shownregion = None
        self.should_show_player_action_buttons = True
        self.extra_status_fns = []
        self.last_rendered_page = None
        self.show_inventory = False
        self.show_things_here = False
        self.worntag = {False:'', True:' (worn)'}
        self.wieldedtag = {False:'',  True:' (wielded)'}
        self.show_dir_buttons_in_classic_loc = True
        self.show_nondir_buttons_in_classic_loc = True
        self.show_postgame_buttons_in_classic_loc = True
        self.nondir_button_col_size_max = 5

    def add_extra_status_fn(self, fnname):
        self.extra_status_fns.append(fnname)

    def show_active_level(self):
        self.shownlevel = self.wh.geo.activelevel
        self.shownregion = self.shownlevel.region

    def show_you_level(self):
        self.shownlevel = self.wh.you.loc.level
        self.shownregion = self.shownlevel.region

    def render(self, game):
        wh = self.wh
        if not wh.changed_since_last_render and \
                self.last_rendered_page is not None:
            wh.debug('returning CACHED last_rendered_page size: %s' % len(self.last_rendered_page))
            return self.last_rendered_page

        s = self.render_core(game,[])

        # Cache the Page Rendering for Possible Future Use
        self.last_rendered_page = ''.join(s)

        # Clears a flag on the model so we know we've rendered it as it is now
        wh.changed_since_last_render = False

        wh.debug('returning NEWGEN last_rendered_page size: %s' % len(self.last_rendered_page))
        return self.last_rendered_page

    def render_core(self, game, page_elements): # in UI class
        wh = self.wh
        geo = wh.geo
        world = geo.world
        region = self.shownregion
        level = self.shownlevel
        you = wh.you
        loc = you.loc

        tock = wh.ev.tock
        usercmd_viewfn = wh.usercmd_viewfn
        help_viewfn = wh.help_viewfn

        frh = FormRenderHelper(self,game)

        s = page_elements
        s.append(img('%s/%s' % (game.mediasubdir,game.logofile)) + EOL)

        s.append(str(level.name) + space(2) + '-' + space(2))
        s.append(str(region.name))
        s.append(' - %s' % wh.get_time_of_day_desc())

        znames = geo.report_zone_names_for(loc)
        if len(znames) > 0:
            s.append(' - %s' % znames)

        # World Map Render
        s.append(AppHtmlLevelRenderer(wh,level).render())

        # Basic Status Line (tock, HP, coords, etc.)
        s.append(self.render_statusline())

        # Buttons for Common User Commands
        s.append(self.render_buttons(frh,game))

        # Inventory
        s.append(self.render_things_here(frh))

        # Things Here
        s.append(self.render_inventory(frh))

        # Textual User Feedback Log
        s.append(self.render_feedback())

        # Identify current UI and GameMode in page source comments
        s.append(self.render_ui_class_name_in_comments())
        s.append(self.render_game_mode_id_in_comments())

        return page_elements

    def render_ui_class_name_in_comments(self):
        return '\n<!--UI class: %s-->\n' % (self.__class__.__name__)

    def render_game_mode_id_in_comments(self):
        return '\n<!--game mode: %s-->\n' % (self.wh.gamemode)

    def render_statusline(self):
        wh = self.wh
        tock = wh.ev.tock
        you = wh.you
        loc = you.loc
        s = []
        wh = self.wh

        s.append('tock: %s%s' % (tock, space(4)))
        self.render_hp(s)
        self.render_stomach(s)
        self.render_loc(s)
        self.render_wielded(s)
        #self.render_last_save(s)
        s.append('%s[%s]' % (space(2),wh.gamemode.mode_name()))
        self.render_mode_indicators(s)
        self.render_extra_status_fns(s)

        return ''.join(s)

    def render_hp(self, s):
        you = self.wh.you
        hp = '%s/%s' % (you.hp, you.hp_max)
        if you.hp == you.hp_max:
            hp = fontcolorize(hp,HtmlColors.DARKGREEN)
        elif you.hp <= 2:
            hp = fontcolorize(hp,HtmlColors.RED)
        elif you.hp <= (you.hp_max / 2):
            hp = fontcolorize(hp,HtmlColors.DARKYELLOW)
        s.append('HP: %s%s' % (hp, space(4)))

    def render_stomach(self, s):
        you = self.wh.you
        stomach = '%s/%s' % (you.get_stomach(), you.get_stomach_size())
        if you.get_stomach() == you.get_stomach_size():
            stomach = fontcolorize(stomach,HtmlColors.DARKGREEN)
        elif you.get_stomach() <= 2:
            stomach = fontcolorize(stomach,HtmlColors.RED)
        elif you.get_stomach() <= (you.get_stomach_size() / 2):
            stomach = fontcolorize(stomach,HtmlColors.DARKYELLOW)
        s.append('stomach: %s%s' % (stomach, space(4)))

    def render_loc(self, s):
        coords = None
        loc = self.wh.you.loc
        if loc is not None:
            coords = str(loc.r) + ',' + str(loc.c)
        s.append('loc: (' + str(coords) + ')' + space(4))

    def render_wielded(self, s):
        if self.wh.you.has_wielded():
            m = '{%s}%s' % (self.wh.you.describe_wielded(), space(4))
            s.append(m)

    def render_last_save(self, s):
        sss = None
        wh = self.wh
        if not wh.last_save_time:
            sss = 'never'
        else:
            now = time.time()
            diff = now - wh.last_save_time
            diffstr = secs_float_diff_to_summary_str(diff)
            sss = 'tock %s about %s ago' % (wh.last_save_tock, diffstr)
        ss = 'last save: %s' % sss
        s.append(ss)

    def render_mode_indicators(self, s):
        wh = self.wh
        if wh.cfg('devmode'):
            s.append(space(2) + fontcolorize('[devmode]',HtmlColors.DEVONLY))
            s.append(EOL)

    def render_extra_status_fns(self, s):
        # Extra Status Functions (with Game-Specific Information)
        wh = self.wh
        if wh.cfg('devmode'):
            esfns = self.extra_status_fns
            for i,fnname in enumerate(esfns):
                fn = getattr(wh,fnname)
                if i == (len(esfns) / 2):
                    s.append(EOL)
                s.append(fontcolorize(fn(),HtmlColors.DEVONLY) + space(4))

    def render_console(self, frh):
        if not self.wh.cfg('devmode') and not self.wh.gamemode.console_input_allowed():
            return ''
        s = []
        hiddenfieldparams = frh.cmdparams('console')
        app(s,'<form method="post" action="'+site_url(viewurl(self.wh.usercmd_viewfn,'/'))+'">\n')
        app(s,']> <input name="command" type="text"/>\n')
        app(s,dict2hiddeninputfields(hiddenfieldparams))
        app(s,'<input type="submit"/>\n')
        app(s,'</form>')
        return ''.join(s)

    def render_inventory(self, frh):
        if not self.show_inventory:
            return ''
        you = self.wh.you
        s = 'Inventory:' + EOL
        s += self.thing_set_render_helper(you.wielded_set(),            ' (wielded)', frh)
        s += self.thing_set_render_helper(you.worn_set(),               ' (worn)',    frh)
        s += self.thing_set_render_helper(you.nonwielded_nonworn_set(), '',           frh)
        return s

    def thing_set_render_helper(self, things, tagsuffix, frh):
        you = self.wh.you
        data = []
        for th in things:
            row = []
            cell = {}
            withid = self.wh.cfg('devmode')
            desc = '%s%s' % (th.full_describe(withid=withid), tagsuffix)
            cell[table.valuekey] = desc
            cell['valign'] = 'top'
            row.append(cell)
            thid = th.id_thing()

            dropbutton = frh.button_usercmd('drop', params={'what':thid})
            row.append(dropbutton)

            if not you.does_wear(th) and you.can_wear(th):
                wearbutton = frh.button_usercmd('wear', params={'what':thid})
                row.append(wearbutton)
            elif you.does_wear(th) and you.can_unwear(th):
                unwearbutton = frh.button_usercmd('unwear', params={'what':thid})
                row.append(unwearbutton)

            if not you.does_wield(th) and you.can_wield(th):
                wieldbutton = frh.button_usercmd('wield', params={'what':thid})
                row.append(wieldbutton)
            elif you.does_wield(th) and you.can_unwield(th):
                unwieldbutton = frh.button_usercmd('unwield', params={'what':thid})
                row.append(unwieldbutton)

            if isinstance(th,Edible):
                eat_button = frh.button_usercmd('eat', params={'what':thid})
                row.append(eat_button)

            if isinstance(th,Useable):
                use_button = frh.button_usercmd('use', params={'what':thid})
                row.append(use_button)

            if isinstance(th,Readable):
                read_button = frh.button_usercmd('read', params={'what':thid})
                row.append(read_button)

            data.append(row)
        return table(data,header=False)

    def render_things_here(self, frh):
        if not self.show_things_here:
            return ''

        wh = self.wh
        you = wh.you
        things = wh.geo.list_whats_here(you.loc,skiplist=(you,))
        data = []
        vis_things = []
        for th in things:
            if not th.is_invisible():
                vis_things.append(th)
        for th in vis_things:
            row = []
            row.append(space(2))
            cell = {}
            withid = wh.cfg('devmode')
            desc = '%s%s%s' % (th.describe(withid=withid), self.worntag[th in you.worn], self.wieldedtag[th in you.wielded])
            cell[table.valuekey] = desc
            cell['valign'] = 'top'
            row.append(cell)
            thid = th.id_thing()
            if you.can_you_pickup_this(th) and th.can_be_picked_up():
                pickupbutton = frh.button_usercmd('pickup', params={'what':thid})
                row.append(pickupbutton)
            data.append(row)
        s = 'Things Here:'
        if len(data) > 0:
            s += table(data,header=False)
        else:
            s += EOL + space(2) + '(nothing)' + EOL + EOL
        return s

    def render_dir_buttons(self, frh):
        wh = self.wh

        dirbuttons_data = []
        row2 = []
        dirbuttons_data.append(row2)

        cmdchoices = wh.get_directional_move_usercmds_bare()
        cmdselected = 'walk'
        if 'move' in wh.rel_dir_cmd_last_submitted and wh.rel_dir_cmd_last_submitted['move'] in cmdchoices:
            cmdselected = wh.rel_dir_cmd_last_submitted['move']
        movebuttons = frh.directional_usercmd_button_layout(cmdchoices,cmdselected)
        row2.append(movebuttons)

        row2.append(space(2))

        cmdchoices = wh.get_directional_nonmove_usercmds_bare()
        cmdselected = 'look'
        if 'nonmove' in wh.rel_dir_cmd_last_submitted and wh.rel_dir_cmd_last_submitted['nonmove'] in cmdchoices:
            cmdselected = wh.rel_dir_cmd_last_submitted['nonmove']
        attackbuttons = frh.directional_usercmd_button_layout(cmdchoices,cmdselected)
        row2.append(attackbuttons)

        s = table(dirbuttons_data,header=False)
        return s

    def render_buttons(self, frh, game): # in UI class
        wh = self.wh
        you = wh.you
        buttonrow = []

        #if self.should_show_player_action_buttons and you.is_alive() and not wh.gamewin and not wh.gameloss:

        if you.is_alive() and not wh.gamewin and not wh.gameloss:
            if self.should_show_player_action_buttons:
                console_and_dirbuttons_data = []
                row = []
                console_and_dirbuttons_data.append(row)

                # Directional Command Buttons
                if self.show_dir_buttons_in_classic_loc:
                    dirbuttons = self.render_dir_buttons(frh)
                    row.append(dirbuttons)

                # Console
                console = self.render_console(frh)

                # Help
                helplink = siteurllink(wh.help_viewfn, linktxt='Help', getparams={'gameid':game.id})

                txt = console
                if len(console) > 0:
                    txt += space(4)
                txt += helplink
                row = [txt]
                console_and_dirbuttons_data.append(row)

                console_and_dirbuttons = table(console_and_dirbuttons_data,header=False)
                buttonrow.append(console_and_dirbuttons)
                buttonrow.append(space(2))

                if self.show_nondir_buttons_in_classic_loc:
                    self.render_and_append_nondir_buttons(frh,buttonrow)
        else:
            if self.show_postgame_buttons_in_classic_loc:
                postgamebuttons = self.render_postgame_buttons_as_row(frh)
                buttonrow.extend(postgamebuttons)
            if wh.cfg('devmode'):
                console = self.render_console(frh)
                buttonrow.append(console)

        footerdata = [buttonrow]

        return table(footerdata,header=False)

    def render_postgame_buttons_as_row(self, frh):
        postgamebuttons = []
        if self.wh.gamemode.may_watch_time_pass_after_death():
            postgamebuttons.append(frh.button_usercmd('timepass'))
        postgamebuttons.append(frh.button_usercmd('reset','reset game'))
        return postgamebuttons

    def render_and_append_nondir_buttons(self, frh, buttonrow):
        wh = self.wh

        fixedbuttons = []
        fixedbuttons.append(frh.button_usercmd('wait'))
        fixedbuttons.append(frh.button_usercmd('story'))
        if wh.gamemode.again_command_allowed():
            fixedbuttons.append(frh.button_usercmd('again'))

        regbuttons = []
        devbuttons = []

        # AutoUI Cmd Buttons - begin
        attribs = dir(wh)
        for a in attribs:
            if a.startswith(USERCMD_PREFIX):
                method = getattr(wh,a)
                if hasattr(method,'meta'):
                    #wh.debug('method '+a+' has meta: ' + str(method.meta))
                    if AUTOUI_METAKEY in method.meta and method.meta[AUTOUI_METAKEY]:
                        if is_devonly(method) and not wh.cfg('devmode'): continue
                        if hasattr(method,'extra_show_reqs'):
                            extra_reqs = getattr(method,'extra_show_reqs')
                            met_extra_reqs = True
                            for reqmethodname in extra_reqs:
                                reqmethod = getattr(wh,reqmethodname)
                                if not reqmethod():
                                    met_extra_reqs = False
                                    break
                            if not met_extra_reqs:
                                continue
                        cmd = a[len(USERCMD_PREFIX):]
                        label = wh.label_for_usercmd(cmd)
                        #TODO color is NOT working!
                        color = None
                        if is_devonly(method):
                            color = HtmlColors.RED
                            label += ' (D)'
                        b = frh.button_usercmd(cmd,label,color=color)
                        if is_devonly(method):
                            devbuttons.append(b)
                        else:
                            regbuttons.append(b)
        #end of: for a in attribs

        resetbutton = frh.button_usercmd('reset','reset game')

        actionbuttons = []
        actionbuttons.extend(fixedbuttons)
        actionbuttons.extend(regbuttons)
        actionbuttons.extend(devbuttons)
        actionbuttons.append(resetbutton)

        def addtobuttonrow(colbs, buttonrow):
            colval = []
            for cb in colbs: 
                app(colval, cb+'\n')
            d = {}
            d[table.valuekey] = ''.join(colval)
            d['valign'] = 'top'
            colval = d
            buttonrow.append(colval)

        colbs = []
        col_size_max = self.get_nondir_button_col_length_max()
        for b in actionbuttons:
            if len(colbs) == col_size_max:
                addtobuttonrow(colbs,buttonrow)
                colbs = []
            colbs.append(b)
        addtobuttonrow(colbs,buttonrow)
        # AutoUI Cmd Buttons - end

    def get_nondir_button_col_length_max(self):
        m = self.nondir_button_col_size_max
        if self.wh.cfg('devmode'): return m * 2
        else: return m

    def render_feedback(self):
        s = []
        for m in self.wh.msgs:
            msg = m[0] #m[1] is tock when msg created
            shouldmakehtmlsafe = m[2]
            newlines2EOL = m[3]
            t = msg
            if shouldmakehtmlsafe:
                t = makehtmlsafe(msg)
            if newlines2EOL:
                t = t.replace('\n',EOL)
            if not t.endswith('<br/>'):
                t += EOL
            app(s,t)
        return ''.join(s)

class ClassicUI(UI):
    pass

class AltUI(UI):
    def __init__(self, webhack):
        UI.__init__(self, webhack)
        self.show_dir_buttons_in_classic_loc = False
        self.show_nondir_buttons_in_classic_loc = False
        self.show_postgame_buttons_in_classic_loc = False
        self.nondir_button_col_size_max = 3

    def should_show_dir_buttons(self):
        return self.wh.you.is_alive() and not self.wh.gamewin and not self.wh.gameloss

    def should_show_nondir_buttons(self):
        return self.wh.you.is_alive() and not self.wh.gamewin and not self.wh.gameloss

    def render_core(self, game, page_elements): # in AltUI class
        wh = self.wh
        geo = wh.geo
        world = geo.world
        region = self.shownregion
        level = self.shownlevel
        you = wh.you
        loc = you.loc

        tock = wh.ev.tock
        usercmd_viewfn = wh.usercmd_viewfn
        help_viewfn = wh.help_viewfn

        frh = FormRenderHelper(self,game)

        s = page_elements
        s.append(img('%s/%s' % (game.mediasubdir,game.logofile)) + EOL)

        s.append(str(level.name) + space(2) + '-' + space(2))
        s.append(str(region.name))
        s.append(' - %s' % wh.get_time_of_day_desc())

        znames = geo.report_zone_names_for(loc)
        if len(znames) > 0:
            s.append(' - %s' % znames)

        # World Map Render
        map = AppHtmlLevelRenderer(wh,level).render()
        data = []
        row = []
        data.append(row)
        row.append(map)

        buttonsdata = []

        dirbuttonsrow = []
        buttonsdata.append(dirbuttonsrow)
        dirbuttons = ''
        if self.should_show_dir_buttons():
            dirbuttons = self.render_dir_buttons(frh)
        dirbuttonsrow.append(dirbuttons)

        miscbuttonsrow = []
        buttonsdata.append(miscbuttonsrow)
        miscbuttonsdata = []
        row2 = []
        miscbuttonsdata.append(row2)
        if self.should_show_nondir_buttons():
            self.render_and_append_nondir_buttons(frh,row2)
        else:
            postgamebuttons = self.render_postgame_buttons_as_row(frh)
            row2.extend(postgamebuttons)
        miscbuttonstable = table(miscbuttonsdata,header=False)
        miscbuttonsrow.append(miscbuttonstable)

        buttonstable = table(buttonsdata,header=False)

        row.append(buttonstable)
        map_plus_dirbuttons = table(data,header=False)
        s.append(map_plus_dirbuttons)

        # Basic Status Line (tock, HP, coords, etc.)
        s.append(self.render_statusline())

        # Buttons for Common User Commands
        s.append(self.render_buttons(frh,game))

        # Inventory
        s.append(self.render_things_here(frh))

        # Things Here
        s.append(self.render_inventory(frh))

        # Textual User Feedback Log
        s.append(self.render_feedback())

        # UI class/mode name/desc
        s.append(self.render_ui_class_name_in_comments())
        s.append(self.render_game_mode_id_in_comments())

        if wh.gamemode.bg_sound_allowed() and wh.cfg('bgmusic'):
            codebase = wh.get_base_media_url() + 'bgmusic/'
            fname = wh.pick_bgmusic_file_to_play()
            bgmusic = musicplay_in_body(codebase,fname)
            s.append(bgmusic)

        return page_elements

ui_class_names = ['ClassicUI', 'AltUI']

#TODO create another LR subclass that renders to an image file, then returns a string containg an <img> link to that file
class AppHtmlLevelRenderer(StringLevelRenderer):
    def __init__(self, webhack, level):
        StringLevelRenderer.__init__(self,level)
        self.bgcolor = HtmlColors.BG
        self.fgcolordefault = HtmlColors.FG
        self.wh = webhack

    def render(self):
        wh = self.wh
        you = wh.you
        #TODO convert to "list.append(string) -> ''.join(list)" idiom:
        s = ['<pre>\n',]
        #app(s,'<font name="Courier">\n')
        app(s, '<table bgcolor="%s"><tr><td>' % self.bgcolor)
        app(s,'<code>')
        map = self.level.grid
        for row in map:
            for cell in row:
                ch = '?'
                color = None
                if cell.seen or wh.cfg('you_see_all'):
                    thing2render = wh.most_important_thing_here_to_show_on_map_other_than_you(cell)
                    if thing2render is None: #means nothing there or nothing visible
                        ch = '.'
                        if cell.terrain is not None:
                            ch, color = cell.terrain.render_char()
                        else:
                            color = self.fgcolordefault
                    else:
                        ch, color = thing2render.render_char()
                        if ch is None:
                            ch = '?'
                        if color is None:
                            color = self.fgcolordefault
                else:
                    ch = '?'
                    color = self.fgcolordefault
                if cell.is_this_here(you): #ensures You always visible
                    ch, color = you.render_char()
                if color is None:
                    color = self.fgcolordefault
                #sss = '<font color="%s">%s</font>' % (color, ch)
                ch_chunk = fontcolorize(ch,color)
                app(s, ch_chunk)
            app(s, EOL)
        app(s, '</code>\n')
        app(s, '</td></tr></table>\n')
        #app(s, '</font>\n')
        app(s, '</pre>\n')
        return ''.join(s)

class FormRenderHelper:
    def __init__(self, ui, game):
        self.ui = ui # instance of UI class
        self.commonparams = {'gameid':game.id}

    def addcommonparams(self, params):
        newparams = dict(self.commonparams)
        newparams.update(params)
        return newparams

    def cmdparams(self, cmd, params={}):
        d = dict(params)
        d.update({'cmd':cmd})
        return self.addcommonparams(d)

    def button_usercmd(self, cmd, label=None, params={}, color=None):
        if label == None:
            label = cmd
        return onebuttonform(viewurl(self.ui.wh.usercmd_viewfn),label,self.cmdparams(cmd,params),color=color)

    def directional_usercmd_button_layout(self, cmdchoices, cmdselected):
        data = []
        data.append(['','',''])
        data.append(['','',''])
        data.append(['','',''])

        #TODO convert from "s +=" technique to "s.append(); ''.join(s)"

        s = []
        app(s, '<select name="command">' + EOL)
        for i,c in enumerate(cmdchoices):
            sel = ''
            if c == cmdselected:
                sel = ' selected'
            value = c
            shown = value.replace('_',' ')
            app(s, '<option value="%s"%s>%s</option>%s' % (value,sel,shown,EOL))
        app(s, '</select>' + EOL)
        s = ''.join(s)
        centercell = self.addmeta(s, {'align':'center', 'valign':'top'})

        data[1][1] = centercell

        button = self.button_usercmd2

        data[1][0] = button('<',{'relcol':-1})
        data[1][2] = button('>',{'relcol':1})
        data[0][1] = self.addmeta(button('^',{'relrow':-1}), {'align':'center'})
        data[2][1] = self.addmeta(button('V',{'relrow':1}), {'align':'center'})

        if self.ui.wh.diag:
            data[0][0] = button('\\',{'relcol':-1, 'relrow':-1})
            data[2][2] = button('\\',{'relcol':+1, 'relrow':+1})
            data[0][2] = button('/',{'relcol':+1, 'relrow':-1})
            data[2][0] = button('/',{'relcol':-1, 'relrow':+1})

        url = site_url(viewurl(self.ui.wh.usercmd_viewfn))
        s = []
        app(s, '<form method="post" action="%s"/>\n' % url)
        hiddenparams = dict(self.commonparams)
        hiddenparams['cmd'] = 'console'
        app(s, dict2hiddeninputfields(hiddenparams))
        app(s, table(data,header=False))
        app(s, '</form>')
        s = ''.join(s)
        return s

    def button_usercmd2(self, label, params={}):
        s = self.submitbutton(viewurl(self.ui.wh.usercmd_viewfn), label, params)
        return s

    def submitbutton(self, target, labeltext, params={}):
        value = str(params)
        pre = SUBMIT_STYLE_PARAMS_PREFIX
        s = '    <input type="submit" name="%s%s" value="%s"/>\n' % (pre,value,labeltext)
        return s

    def addmeta(self, rawcelldata, metadatadict):
        d = {table.valuekey:rawcelldata}
        d.update(metadatadict)
        return d

############
# UI - end #
############

##########################################
# Subsystem Subclasses & Plugins - begin #
##########################################

class WebHackGeoSystemPlugin(GeoSystemPlugin):
    def __init__(self, geosystem, webhack):
        GeoSystemPlugin.__init__(self,geosystem)
        self.wh = webhack

    def getDefaultRegion(self):
        self.geosystem.activelevel.region

    def getDefaultLevel(self):
        self.geosystem.activelevel

    def bug(self, msg): self.wh.bug(msg)
    def log(self, msg): self.wh.log(msg)
    def debug(self, msg): self.wh.debug(msg)
    def error(self, msg): self.wh.error(msg)

class WebHackGeoSystem(GeoSystem):
    def __init__(self, webhack, plugin=None):
        GeoSystem.__init__(self,plugin)
        self.wh = webhack

    def thing_instantiate(self, thingclass, ctor_extra_args=None):
        if ctor_extra_args is not None:
            return thingclass(self.wh, **ctor_extra_args)
        else:
            return thingclass(self.wh)

    def put_on_map(self, thing, loc, move=False, moveonsamelevel=False, moveonsameregion=False):
        def buildlogmsg(reason):
            return 'put_on_map() did not because '+str(reason)+'; coords was ('+str(loc)+'); thing was "'+str(thing.describe())+'" ('+str(thing)+')'

        return GeoSystem.put_on_map(self,thing,loc,move,moveonsamelevel,moveonsameregion)

    def remove_from_map(self, thing, move=False, moveonsamelevel=False, moveonsameregion=False):
        origloc = thing.loc
        GeoSystem.remove_from_map(self,thing,move,moveonsamelevel,moveonsameregion)
        event = ThingRemovedFromMapEvent(
            thing= thing,
            region= origloc.region,
            level= origloc.level,
            r= origloc.r,
            c= origloc.c)
        self.wh.emit_event(event)

    def move_this_from_here_to_there(self, thing, newloc, movedesc='moving'):
        oldloc = thing.loc
        oldcell = oldloc.level.grid[oldloc.r][oldloc.c]
        if thing not in oldcell.things:
            self.wh.log('could NOT do this because it is not in the orig loc: '+movedesc+' '+thing.describe()+' from '+str(oldloc)+' to '+str(newloc))
            return
        self.wh.log(movedesc+' '+thing.describe()+' from '+str(oldloc)+' to '+str(newloc))

        GeoSystem.move_this_from_here_to_there(self,thing,newloc)

        event = ThingEntersCellEvent(
            thing=thing,
            region=newloc.region,
            level=newloc.level,
            r=newloc.r,
            c=newloc.c)
        self.wh.emit_event(event)

    def does_cell_have_fact(self, cell, fact):
        return self.wh.ai.fa.has_fact(cell,fact)

class WebHackFactSystem(FactSystem):
    def __init__(self, webhack):
        FactSystem.__init__(self)
        self.wh = webhack

    def log(self, msg):
        self.wh.log(msg)

    def debug(self, msg):
        self.wh.debug(msg)

class AppLanguageHelper(LanguageHelper):
    def __init__(self, webhack):
        LanguageHelper.__init__(self)
        self.wh = webhack
        self.you_verbmatrix = copy.deepcopy(self.verbmatrix)
        vm = self.you_verbmatrix
        vm['to be']['singular']['past']        = 'were'
        vm['to be']['singular']['present']     = 'are'
        vm['to have']['singular']['past']      = 'had'
        vm['to have']['singular']['present']   = 'have'
        vm['to say']['singular']['present']    = 'say'
        vm['to say']['singular']['past']       = 'said'
        vm['to attack']['singular']['present'] = 'attack'
        vm['to attack']['singular']['past']    = 'attacked'
        vm['to hit']['singular']['present']    = 'hit'
        vm['to hit']['singular']['past']       = 'hit'
        vm['to miss']['singular']['present']   = 'miss'
        vm['to miss']['singular']['past']      = 'missed'
        vm['to try']['singular']['present']    = 'try'
        vm['to try']['singular']['past']       = 'tried'
        vm['to pickup']['singular']['present'] = 'pickup'
        vm['to pickup']['singular']['past']    = 'picked up'
        vm['to drop']['singular']['present']   = 'drop'
        vm['to drop']['singular']['past']      = 'dropped'
        vm['to carry']['singular']['present']  = 'carry'
        vm['to carry']['singular']['past']     = 'carried'
        vm['to digest']['singular']['present'] = 'digest'
        vm['to digest']['singular']['past']    = 'digested'

    def itverbify(self, it, verb, plurality='singular', tense='present'):
        if it is self.wh.you:
            return LanguageHelper.itverbify(self,it,verb,plurality,tense,verbmatrix=self.you_verbmatrix)
        else:
            return LanguageHelper.itverbify(self,it,verb,plurality,tense)

    def possessivify(self, it):
        if it is self.wh.you:
            return 'your'
        else:
            return LanguageHelper.possessivify(self,it)

class WebHackSkillSystemPlugin(SkillSystemPlugin):
    def __init__(self, wh):
        SkillSystemPlugin.__init__(self)
        self.wh = wh

    def gained_xp(self, thing, skill, howmuch, reason=None):
        if skill in ('movement',):
            return
        s = self.describe(thing) + ' gained ' + str(howmuch) + ' xp for ' + skill + ' skill'
        if reason != None:
            s += ' due to '+str(reason)
        s = sentence(s)
        self.wh.feedback_ifyou(thing,s)

    def level_up(self, thing, skill, level):
        s = sentence(self.describe(thing)+' gained '+skill+' skill level '+str(level))
        self.wh.feedback_ifyou(thing,s)

    def reward_unlocked(self, thing, reward):
        s = sentence(self.describe(thing)+' awarded '+skill+' status')
        self.wh.feedback_ifyou(thing,s)

    def describe(self, thing):
        return thing.describe()

    def log(self, msg):
        self.wh.log(msg)

    def debug(self, msg):
        self.wh.debug(msg)

class AppEventSystem(EventSystem):
    def __init__(self, webhack):
        EventSystem.__init__(self)
        self.wh = webhack

    def log(self, msg):
        self.wh.log(msg)

    def debug(self, msg):
        self.wh.debug(msg)

    def tick_and_process_events(self, tickqty=1):
        #TODO flaw currently in that the case where tickqty > 1 is not handled right below (it can allow the user to blow past the tock limit IF the tickqty param given is > 1):
        if not self.wh.gamemode.is_tock_limit() or (self.wh.gamemode.is_tock_limit() and (self.tock < self.wh.gamemode.get_tock_limit())):
            EventSystem.tick_and_process_events(self,tickqty)

    def tick(self):
        if not self.wh.gamemode.is_tock_limit() or (self.wh.gamemode.is_tock_limit() and (self.tock < self.wh.gamemode.get_tock_limit())):
            EventSystem.tick(self)

class WebHackMemorySystemPlugin(MemorySystemPlugin):
    def __init__(self,wh):
        MemorySystemPlugin.__init__(self)
        self.wh = wh

    def get_tock(self):
        return self.wh.ev.tock

    def log(self, msg):
        self.wh.log(msg)

    def debug(self, msg):
        self.wh.debug(msg)

class WebHackThoughtSystemPlugin(ThoughtSystemPlugin):
    def __init__(self,wh):
        ThoughtSystemPlugin.__init__(self)
        self.wh = wh

    def get_tock(self):
        return self.wh.ev.tock

    def log(self, msg):
        self.wh.log(msg)

    def debug(self, msg):
        self.wh.debug(msg)

########################################
# Subsystem Subclasses & Plugins - end #
########################################

#################
# WebHack - end #
#################

######################
# ZombieHack - begin #
######################

class ZombieHack(WebHack):
    short_code = 'zh'
    thing_class_prefix = 'zh_'
    init_state_file_indicator = short_code
    demo_game_mode_class = ZombieHackDemoGameMode
    full_game_mode_class = ZombieHackFullGameMode
    #TODO check for satisfaction of player goals: cure the zombie plague, find his lost loved one
    #TODO if player dies or turns into zombie, he loses the game and can no longer play (though he can Reset)
    #TODO if player achieves any of his other goals (other than merely surive) he wins instantly, and can choose to retire victorious or to continue playing to try to achieve the other goals, or, to just have fun doing things. You're never forced to stop playing a campaign UNLESS you lose (which is usually but not necessarily always caused by dying or turning into a zombie)
    #TODO a help page or overlay that gives player info on playing, mechanics, what stuff on the map means, etc.; should be a separate fullblown viewfn/url (def zh_help(request)...) and on it there's a link back to the main playwebgame page for zh (which itself had a Help link to this page); the body of the help text page can have parts that are generic to all WebHack games and parts which are game-specific (ZH, WolfenHack, etc.)

    def __init__(self): # ZombieHack
        WebHack.__init__(self)
        self.gamename = 'Dead By Zombie'

    def reset_config(self): # ZombieHack
        WebHack.reset_config(self)
        self.set_cfg('debug_ai_zombie',False)

    def get_game_specific_media_subdir(self):
        return 'zomhack/'

    def make_rnd_regions(self, qty):
        'may raise StairwayPlacementFail via internal call to make_rnd_region()'
        #TODO see if i have a name pool class used in Ganymede I could use here instead:
        names = ('Abeltown','Greektown','Farcourt','Miller Ave','Jefferson Park','Sunny Square','Humboldt','Janeway','The Villa','Pennway','Pleasanton')
        nametaken = {}
        for name in names:
            nametaken[name] = False
        regions = []
        for q in xrange(qty):
            while True:
                regname = random.choice(names)
                if not nametaken[regname]:
                    break
            nametaken[regname] = True
            reg, rk, baselev, baselk = self.make_rnd_region(regname)
            regions.append( (reg,rk,baselev,baselk) )
        return regions

    def make_rnd_region(self, regname):
        'may raise StairwayPlacementFail via internal call to stair_pair()'

        geo = self.geo
        w = rnd_in_range(12,60)
        h = rnd_in_range(8,30)
        self.debug('\n\n\n%s x %s\n\n\n' % (w,h))
        region, rk = geo.new_region(regname,w=w,h=h)

        lev, lk = geo.new_level('Street Level', region, levelkey=0)
        base_lev = lev
        base_lk = lk
        self.populate_level_randomly(lev)

        levqty = 2
        if levqty >= 2:
            for q in xrange(levqty-1):
                prevlev = lev
                lev, lk = geo.make_new_level_above('tmpname', prevlev)
                lev.name = '%snd floor' % (lk + 1)
                lev.environment = Level.OUTSIDE
                self.stair_pair(prevlev, lev) # NOTE: may raise StairwayPlacementFail
                self.populate_level_randomly(lev)

        return region, rk, base_lev, base_lk

    def populate_level_randomly(self, level):
        geo = self.geo
        world = geo.world
        region = level.region
        w = level.area.w
        h = level.area.h

        pm = geo.put_on_map
        pm2 = geo.put_on_map2
        maketerr = geo.make_terrainclass_at
        fillterr = geo.make_terrainclass_fill

        stdloc = Location(0,0,level,region)
        stdfloc = FuzzyLocation(r=None,c=None,br=None,bc=None,w=None,h=None,level=level,region=region)

        def loc(r, c):
            return stdloc.clone(r=r,c=c)

        def floc(r=None, c=None, br=None, bc=None, w=None, h=None):
            return stdfloc.clone(r,c,br,bc,w,h)

        bldg_qty = rnd_in_range(1,15)
        for i in xrange(bldg_qty):
            ex_bldg_zones = level.get_zones_of_class(Building)
            attempts = 1
            max_attempts = 5000
            barea = None
            max_dim = 20
            max_c = level.area.w-1
            max_r = level.area.h-1
            while attempts < max_attempts:
                if attempts >= 500:
                    max_r -= 1
                    max_c -= 1 
                if max_c < 1:
                    max_c = 1
                if max_r < 1:
                    max_r = 1
                c = rnd_in_range(1, max_c)
                r = rnd_in_range(1, max_r)
                if attempts >= 1000 and max_dim > 3:
                    max_dim -= 1
                ww = rnd_in_range(3,max_dim)
                hh = rnd_in_range(3,max_dim)
                if ww <=3 and hh <= 3:
                    self.log('considering small building')
                barea = RectArea(ww,hh,c,r)
                if attempts >= 1500 and barea.bx == 1 and barea.by == 1 and barea.w == 3 and barea.h == 3:
                    attempts = max_attempts
                    continue

                if i == 0:
                    if level.area.is_at_least_this_big(40,20):
                        barea = RectArea(40,20,1,1)
                    elif level.area.is_at_least_this_big(16,16):
                        barea = RectArea(15,15,1,1)
                
                if barea.is_within_area(level.area):
                    for eb in ex_bldg_zones:
                        if barea.overlaps(eb.area):
                            self.log('FAIL: barea overlaps with existing bldg; barea %s; ex bldg %s' % (barea, eb.area))
                            break
                    else:
                        self.log('SUCCESS: barea fits in level AND no overlaps with ex bldgs!')
                        break # area chosen is good because fits in level and NOT overlaps w/ex. bldngs
                else:
                    self.log('FAIL: barea %s not fit within level %s' % (barea, level.area))
                attempts += 1
            else:
                self.log('did NOT create rnd building %s of %s because could not fit it on level %s of region %s in less than %s attempts, so gave up' % (i+1, bldg_qty, level, region, max_attempts))
                continue
            smin = rnd_in_range(1,5)
            smax = smin + rnd_in_range(1,5)
            #zombies = self.geo.put_on_map2(zh_Zombie, fuzloc=floc, minqty=qty, maxqty=qty, zones_disallowed=houses)
            self.building_random(loc(barea.by,barea.bx), barea.w, barea.h, None, None, rnd_stuff={'min_qty':smin, 'max_qty':smax}, name='some building')

        ftree_qty = rnd_in_range(0,15)
        pm2(FruitTree, fuzloc=floc(br=0,bc=0), minqty=ftree_qty, maxqty=ftree_qty)

        humsmade = pm2(American, fuzloc=floc(br=0,bc=0), minqty=10, maxqty=10)
        humspeechset = self.get_data_lines('zombiehack/Human_speech')
        for hum in humsmade:
            hum.myenemyclasses.append(zh_Zombie)
            hum.add_to_rnd_speech(humspeechset)

        zombies = pm2(zh_Zombie, fuzloc=floc(br=0,bc=0), minqty=10, maxqty=10)

    def make_teleporter_pair_between_two_levels(self, levA, levB, leavecoord, arrivecoord):
        #NOTE: given levels may or may not be in same region; both situations supported
        #TODO don't assume that coords 0,0 and 1,0 are free/empty/avail for use below:
        levs = (levA, levB)
        for lev in levs:
            lev2 = levA
            if lev is levA:
                lev2 = levB
            if lev is levA:
                lr,lc = leavecoord
            else:
                lr,lc = 0,0
            if lev is levB:
                ar,ac = arrivecoord
            else:
                ar,ac = 1,0
            tp_loc =      Location(lr, lc, lev,  lev.region)
            tp_dest_loc = Location(ar, ac, lev2, lev2.region)
            tp = Teleporter(self, tp_loc, tp_dest_loc)
            tp.devmode_only_tp = True
            tp.devmode_only_vis = True
            self.geo.put_on_map(tp, tp_loc)

    def init_game(self): # ZombieHack
        self.gamemode.init_game()

    def init_ui(self, ui_class_name='AltUI'): # ZombieHack
        WebHack.init_ui(self, ui_class_name=ui_class_name)
        self.make_you_level_active_and_focus_ui()
        self.ui.add_extra_status_fn('status_of_zombie_count')
        self.ui.add_extra_status_fn('status_of_human_count')
        self.ui.add_extra_status_fn('status_of_goal_satisfied_develop_a_cure')
        self.ui.add_extra_status_fn('status_of_you_a_zombie')

    def init_ai(self): # ZombieHack
        WebHack.init_ai(self)
        sb = self.ai.sk.define_skillbundle_skill
        sb('scientist', 'science', '1d3+2')
        sb('doctor', 'medicine', '1d3+2')
        rew = self.ai.sk.define_reward
        rew('science', 100, 'genius')
        rew('medicine', 40, 'nurse')
        rew('medicine', 80, 'doctor')

    def init_eventsystem(self): # ZombieHack
        WebHack.init_eventsystem(self)
        #TODO regarding my reg of zombies_attack listener below, add param to call that lets me indicate that I want my callback called for every zombie in the world (lets me keep that code out of my callback method body and up in the engine where it belongs since it's so generic); when my callback called, the event payload should be accompanied by an extra param in the dict which identifies the specific zombie being evaluated for that particular call to my callback (my callback will be called one or more times, one for each zombie)
        self.ev.add_listener((TickEvent,{}),self,'declare_game_win_if_zombies_gone')
        self.ev.add_listener((TickEvent,{}),self,'declare_game_loss_if_no_more_human_breeding_pairs_left')
        self.ev.add_listener((TickEvent,{}),self,'declare_game_loss_if_you_zombie')
        self.ev.add_listener((ZombieEvent,{'who':self.you}),self,'declare_game_loss_if_you_zombie')
        self.ev.add_listener((TickEvent,{}),self,'make_zombies_at_night')
        self.ev.add_listener((TestPlotEvent,{}),self,'handle_test_plot_event')

        self.plots = []

        cureplot = CureZombiePlot(self)
        self.plots.append(cureplot)
        self.ev.add_listener((IdentifyActiveAgentEvent,{}),cureplot,'handle_IdentifyActiveAgentEvent')
        self.ev.add_listener((IsolateTheGeneEvent,{}),cureplot,'handle_IsolateTheGeneEvent')
        self.ev.add_listener((MapTheThingEvent,{}),cureplot,'handle_MapTheThingEvent')
        self.ev.add_listener((IndexTheThingEvent,{}),cureplot,'handle_IndexTheThingEvent')
        self.ev.add_listener((DesignManufactureProcessEvent,{}),cureplot,'handle_DesignManufactureProcessEvent')
        self.ev.add_listener((SetupFactoryEvent,{}),cureplot,'handle_SetupFactoryEvent')
        self.ev.add_listener((ArrangeDistroMethodEvent,{}),cureplot,'handle_ArrangeDistroMethodEvent')

    def handle_test_plot_event(self, event):
        self.log('handle_tpe')
        s = 'Venturius emerges from the Machine. He steps out of a cloud of white smoke into the center of the room.\n"I return from 1903," he announces. "I bring with me news of a great victory over the forces of darkness. We have sealed the Gates at Kalma. No demon shall pass through while our guards stand watch."\n'
        s += 'He sat down on a nearby chair. Collapsed, really. Shoulders slumped. A servant rushed to fetch him some water.'
        self.feedback(s)

    def make_zombies_at_night(self, tick_event):
        if not self.is_night(): return
        if not chance(1,6): return
        sandbox = self.geo.get_level_with_keys(self.sandbox_region_key,self.sandbox_level_key)
        if self.geo.activelevel is sandbox: return
        qty = rnd_in_range(1,2) # between 1 and 2 zombies will be created at any one time
        level = self.geo.activelevel
        region = level.region
        floc = FuzzyLocation(br=0,bc=0,level=level,region=region)
        self.log('creating %s new night zombies' % qty)
        # zombies may NOT be created inside houses
        houses = level.get_zones_of_class(Building)
        zombies = self.geo.put_on_map2(zh_Zombie, fuzloc=floc, minqty=qty, maxqty=qty, zones_disallowed=houses, cell_facts_disallowed=['safe',])
        for z in zombies:
            self.log('created new night zombie at: %s' % z.loc)

    def is_goal_satisfied_destroy_all_zombies(self):
        return not self.do_any_of_this_thing_class_exist(zh_Zombie)

    def is_goal_satisfied_you_not_zombie(self):
        return not isinstance(self.you,zh_Zombie)

    def is_goal_satisfied_develop_a_cure(self):
        return False #TODO

    def status_of_goal_satisfied_develop_a_cure(self):
        return 'cure made: ' + str(self.is_goal_satisfied_develop_a_cure())

    def status_of_you_a_zombie(self):
        return 'you zombie: ' + str(not self.is_goal_satisfied_you_not_zombie())

    def is_goal_satisfied_escape_to_personal_perm_safety(self):
        return False #TODO

    def is_goal_satisfied_keep_others_alive(self):
        return self.are_at_least_this_many_instances_alive(Human,2)

    def declare_game_win_if_zombies_gone(self, event):
        if self.gamewin or self.gameloss: return
        if not self.do_any_of_this_thing_class_exist(zh_Zombie):
            s = 'You destroyed all zombies! You win! Game over!'
            s = self.game_end_announce_format(s)
            self.feedback(s)
            self.ui.should_show_player_action_buttons = False
            self.gamewin = True

    def declare_game_loss_if_no_more_human_breeding_pairs_left(self, event):
        if self.gamewin or self.gameloss: return
        if not self.is_at_least_one_man_and_woman_alive():
            s = 'There are no more potential breeding pairs for humanity left. (There is no longer at least one man and one woman alive and non-zombie.) Too many have been lost during the zombie outbreak. The human race is now doomed to extinction! You lose! Game over!'
            s = self.game_end_announce_format(s)
            self.feedback(s)
            self.ui.should_show_player_action_buttons = False
            self.gameloss = True

    def declare_game_loss_if_you_zombie(self, zombie_event):
        #assert isinstance(zombie_event,ZombieEvent)
        event = zombie_event
        if self.gamewin or self.gameloss: return
        if isinstance(self.you,zh_Zombie):
            s = 'You turned into a zombie! You lose! Game over!'
            s = self.game_end_announce_format(s)
            self.feedback(s)
            self.ui.should_show_player_action_buttons = False
            self.gameloss = True

    def is_at_least_one_man_and_woman_alive(self):
        self.debug('\ncheck for at least one human breeding pair alive:')
        class FoundEx(Exception): pass
        class Foo:
            def __init__(self, wh):
                self.wh = wh
                self.region = None
                self.level = None
                self.answer = False
                self.found_male_alive = False
                self.found_female_alive = False

            def fn2visit(self, thing):
                #self.wh.debug('visited with: ' + self.wh.devdesc(thing))
                if isinstance(thing,Human) and thing.is_alive():
                    if thing.gender == 'male':
                        self.found_male_alive = True
                    elif thing.gender == 'female':
                        self.found_female_alive = True
                    if self.found_male_alive and self.found_female_alive:
                        self.answer = True
                        self.wh.debug('FOUND ONE HUMAN BREEDING PAIR ALIVE')
                        raise FoundEx()#e, so abort early'

        f = Foo(self)
        try: self.geo.visit_with_all_things_in_world(f.fn2visit)
        except: pass
        self.debug('at least one human breeding pair alive?   %s\n' % f.answer)
        return f.answer

    def status_of_zombie_count(self):
        return 'zombies: %s' % self.geo.get_thingclass_instance_count_in_world(zh_Zombie)

    def status_of_human_count(self):
        return 'humans: %s' % self.get_live_nonzombie_nonyou_human_count()

    def get_live_nonzombie_nonyou_human_count(self):
        class Foo:
            def __init__(self, wh):
                self.wh = wh
                self.count = 0

            def fn2visit(self, human):
                if human.is_alive() and not isinstance(human,zh_Zombie) and human is not self.wh.you:
                    self.count += 1
        f = Foo(self)
        self.geo.visit_with_every_thingclass_instance_in_world(f.fn2visit,Human)
        return f.count
#end class ZombieHack


class zh_Zombie(Lifeform):
    char = 'Z'
    charcolor = HtmlColors.RED
    atkhitchance = (2,3)
    atkdmg = 5
    digests = False
    starves = False

    def __init__(self, webhack, orighuman=None):
        Lifeform.__init__(self,webhack,mind2use=ZombieMind(self))
        self.basebasedesc = 'zombie'
        self.init_hp((8,16))
        self.myenemyclasses = [Human]
        self.orighuman = orighuman
        self.coredesc = self.basebasedesc
        self.min_sound_volume_heard = 5
        self.mind_content_load('zh_Zombie','zombiehack/')
        self.render_importance = 15

    def does_self_block_adding_thing_to_self_cell(self):
        return True

    def is_capable_of_speech(self):
        return self.is_alive()

    def can_be_picked_up(self):
        return False

    def get_odds_of_rnd_move(self):
        return 1,3 # 33% chance of rnd movement per tick

    def describe(self, withid=False):
        idstr = self.withid_helper(withid)
        defaultdesc = 'a ' + self.coredesc
        ddesc = None
        if self.orighuman != None:
            if self.orighuman.__class__ == Human:
                ddesc = defaultdesc
            else:
                ddesc = 'The %s of %s' % (self.coredesc, self.orighuman.describe())
        else:
            ddesc = defaultdesc
        return ddesc + idstr
ZombieCostume.looks_like_class = zh_Zombie

class WarriorDoll(Lifeform):
    "little evil Zuni Hunting Fetish Doll, from Trilogy of Terror"
    char = 'w'
    charcolor = HtmlColors.RED
    atkhitchance = (2,3)
    atkdmg = 4
    digests = False
    starves = False

    def __init__(self, webhack, orighuman=None):
        Lifeform.__init__(self,webhack,mind2use=ZombieMind(self))
        self.basebasedesc = 'little Zuni hunting fetish doll'
        self.init_hp((3,5))
        self.myenemyclasses = [Human]
        self.orighuman = orighuman
        self.coredesc = self.basebasedesc
        self.min_sound_volume_heard = 5
        #self.mind_content_load('zh_Zombie','zombiehack/')
        self.render_importance = 15

    def does_self_block_adding_thing_to_self_cell(self):
        return True

    def is_capable_of_speech(self):
        return False
        #return self.is_alive()

    def can_be_picked_up(self):
        return False

    def get_odds_of_rnd_move(self):
        return 3,4 # 33% chance of rnd movement per tick

####################
# ZombieHack - end #
####################


class DropFail(Exception):
    def __init__(self, thing, reason):
        self.thing = thing
        self.reason = reason

    def __str__(self):
        return self.reason

class DropFailDueToNotUnwieldable(DropFail):
    def __init__(self, thing):
        DropFail.__init__(self,thing,'did not drop because was wielded and could not unwield')

class DropFailDueToNotUnwearable(DropFail):
    def __init__(self, thing):
        DropFail.__init__(self,thing,'did not drop because was worn and could not unwear')

class Building(Zone):
    blueprints = None
    components = None # placed Thing instance list that comprises the house (walls, doors, fixtures...)
    #TODO owner? front door? back door? street/postal address? price? age?

    def __init__(self, level, bc, br, w, h, name=None, desc=None, blueprints=None, components=None):
        if name is None:
            name = 'building'
        if desc is None:
            desc = 'a building'
        Zone.__init__(self, level, bc, br, w, h, name, desc)
        if blueprints is not None:
            self.blueprints = blueprints
        if components is not None:
            self.components = components

    def assertValid(self):
        assert self.blueprints is not None
        assert isinstance(self.blueprints,type(''))
        assert self.components is not None
        assert len(self.components) > 0

class CursesUI:
    inv_alias_keys = None
    wh = None

    def __init__(self, wh):
        #TODO BUG VULN: this map can cause memory leak of item referrents! prob change to weak ref Python supports such a thing
        self.inv_alias_keys = {}
        self.wh = wh

    def get_alias_key(self, item):
        if item in self.inv_alias_keys:
            return self.inv_alias_keys[item]
        else:
            key = self.get_key_unused_by_inventory()
            self.inv_alias_keys[item] = key
            return key

    def get_key_unused_by_inventory(self):
        all_keys = 'abcdefghijklmnopqrstuvwxyz'
        all_keys = list(all_keys)
        inv = self.wh.you.list_inventory()
        used_keys = []
        for item in inv:
            if item in self.inv_alias_keys:
                used_key = self.inv_alias_keys[item]
                used_keys.append(used_key)
        pool = list(all_keys)
        for uk in used_keys:
            pool.remove(uk)
        return random.choice(pool)

#############################################
# Code That Must Come At End Of Module Load #
#############################################

# NOTE: this should come after all wh Thing subclasses have been defined in this file:

def add_thing_class_to_group(thingclass, group_name):
    if group_name not in thing_class_groups:
        thing_class_groups[group_name] = []
    if thingclass not in thing_class_groups[group_name]:
        thing_class_groups[group_name].append(thingclass)

thing_classes = get_instantiable_thing_classes(globals())
for cl in thing_classes:
    master_layoutmap[cl.char] = cl
    debug('put %s in master_layoutmap for %s' % (cl, cl.char))
    if issubclass(cl,RndStuff) and 'abstract' not in vars(cl):
        add_thing_class_to_group(cl,'rnd_stuff')
    if issubclass(cl,HealItem) and 'abstract' not in vars(cl):
        add_thing_class_to_group(cl,'healing_items')
    if issubclass(cl,Food) and 'abstract' not in vars(cl):
        add_thing_class_to_group(cl,'store_food')

add_thing_class_to_group(Book,'library_material')

#EOF
