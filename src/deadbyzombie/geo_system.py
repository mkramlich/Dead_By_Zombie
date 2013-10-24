'''
geo_system.py
by Mike Kramlich
created for WebHack
'''

import random
import time

# My Libraries
# lib is lib.py in same dir
from lib import HtmlColors, assertNotNone, stradd, tostr
from rectarea import RectArea

# that will eventually be moved to a lib directory, out of webhack/grogdjango:
from fact_system import HasFacts

from groglib import Groups, dist3

'''
TODO

newgeo: create a new alt version of groglib.dist (and dist2) that can take an x,y,z instead of just x,y, and yield the correct distance for that

make convenience methods to calculate distance (built on top of groglib.dist and dist2)
'''

class GeoSystem:
    def __init__(self, plugin=None):
        if plugin is not None:
            self.plugin = plugin
        else:
            self.plugin = GeoSystemPlugin(self) #replace with app-specific instance if needed
        self.default_level_w = 20
        self.default_level_h = 10
        self.activelevel = None

    def init(self, worldname, w=None, h=None):
        if w is None:
            w = self.default_level_w
        if h is None:
            h = self.default_level_h

        world = World(self,w,h)
        world.name = worldname
        self.world = world

        #TODO the Dayton Ohio and Street Level names should not be hardcoded here, since are application/scenario specific for BZ; GeoSystem should be application-agnostic

        region = Region(self.world)
        region.name = 'Dayton, Ohio'
        self.initial_region = region
        self.initial_regionkey = 'initial'
        world.regions[self.initial_regionkey] = self.initial_region

        level = Level(region)
        level.name = 'Street Level'
        self.activelevel = level
        self.initial_level = level
        self.initial_levelkey = 0
        region.levels[self.initial_levelkey] = self.initial_level

    def new_region(self, name, key=None, w=None, h=None):
        self.log('new_region: w,h: %s,%s' % (w,h))
        region = Region(self.world,w,h)
        region.name = name
        if key is None:
            #TODO VULN here because this may not truly be unique, but only in situations where several calls to new_level are executed in very very close proximity in time
            unique_ish_piece = str(self.rnd_id())
            key = '%s-%s' % (name, unique_ish_piece)
        else:
            if key in self.world.regions:
                raise 'given region key %s is already in use' % key
        self.world.regions[key] = region
        return region, key

    def make_new_level_above(self, name, level2beabove):
        rk, lk = self.get_keys_for_level(level2beabove)
        region = self.world.regions[rk]
        w, h = level2beabove.area.get_wh()
        newlevel = Level(region)
        newlevel.name = name
        new_lk = lk + 1
        region.levels[new_lk] = newlevel
        return newlevel, new_lk

    def new_level(self, levelname, region, env=None, levelkey=None):
        level = Level(region)
        level.name = levelname
        if env is None:
            env = Level.OUTSIDE
        level.environment = env
        if levelkey is None:
            #TODO VULN here because this may not truly be unique, but only in situations where several calls to new_level are executed in very very close proximity in time
            unique_ish_piece = str(self.rnd_id())
            levelkey = '%s-%s' % (levelname, unique_ish_piece)
        else:
            if levelkey in region.levels:
                raise 'given level key %s is already in use' % levelkey
        region.levels[levelkey] = level
        return level, levelkey

    def get_keys_for_level(self, level):
        'returns regionkey,levelkey; None,None if not found'
        levelkey = None
        regionkey = None
        for rk in self.world.regions:
            region = self.world.regions[rk]
            for lk in region.levels:
                lev = region.levels[lk]
                if lev is level:
                    return rk, lk
        return None, None

    def get_region_in_world(self, region_key):
        return self.world.regions[region_key]

    def get_level_in_region(self, region, level_key):
        return region.levels[level_key]

    def get_level_with_keys(self, region_key, level_key):
        reg = self.get_region_in_world(region_key)
        return self.get_level_in_region(reg, level_key)

    def getDefaultRegion(self):
        return self.plugin.getDefaultRegion()

    def getDefaultLevel(self):
        return self.plugin.getDefaultLevel()

    def rnd_id(self):
        return int(time.time() * 1000 * 1000 * 10)

    def propose_new_zonekey(self):
        return 'zone-%s' % self.rnd_id()

    def identify_unused_zonekey(self, level, max_attempts=100):
        zonekey = None
        attempts = 0
        while attempts < max_attempts:
            zonekey = self.propose_new_zonekey()
            if zonekey not in level.zones:
                break
            attempts += 1
        else: return None
        return zonekey

    def add_zone(self, level, zone, zonekey=None):
        if not zonekey:
            max_attempts = 100
            zonekey = self.identify_unused_zonekey(level,max_attempts)
            if not zonekey:
                raise 'add_zone() was called without a zonekey given so it tried to generate one; it could not identify one that was unused after %s attempts, so it gave up' % max_attempts
        else:
            if zonekey in level.zones:
                raise 'add_zone() attempt rejected because given zonekey %s is already in use' % zonekey
        level.zones[zonekey] = zone
        zone.level = level
        return zonekey

    def new_loc(self, r, c, level=None, region=None):
        if region is None:
            region = self.getDefaultRegion()
        if level is None:
            level = self.getDefaultLevel()
        return Location(r,c,level,region)

    def get_zones_containing(self, loc, klass=None):
        if klass is None:
            klass = Zone
        zones = []
        allzones = loc.level.get_zones_of_class(klass)
        for z in allzones:
            if z.area.contains(loc.c,loc.r):
                zones.append(z)
        return zones

    def report_zone_names_for(self, loc, delim=', ', klass=None):
        if klass is None:
            klass = Zone
        s = ''
        zones = self.get_zones_containing(loc, klass=klass)
        for z in zones:
            s = stradd(s, delim, z.name)
        return s

    def make_terrainclass_at(self, terrainclass, loc):
        level = loc.level
        r = loc.r
        c = loc.c
        try:
            cell = level.grid[r][c]
            cell.terrain = terrainclass()
        except:
            self.log('\n\nr,c: %s,%s' % (r,c))
            self.log('len(level.grid): %s' % len(level.grid))
            self.log('len(level.grid[0]): %s\n\n' % len(level.grid[0]))
            raise

    def make_terrainclass_fill(self, terrainclass, loc, w, h):
        for rr in xrange(h):
            r = loc.r + rr
            for cc in xrange(w):
                c = loc.c + cc
                newloc = loc.clone(r=r,c=c)
                self.make_terrainclass_at(terrainclass, newloc)

    def bug(self, msg):   self.plugin.bug(msg)
    def log(self, msg):   self.plugin.log(msg)
    def debug(self, msg): self.plugin.debug(msg)
    def error(self, msg): self.plugin.error(msg)

    def get_cell(self, level, r, c):
        return level.grid[r][c]

    def ensure_in_cell_desc(self, desc, level, r, c):
        cell = self.get_cell(level,r,c)
        if cell.desc is None:
            cell.desc = ''
        if desc not in cell.desc:
            #if len(cell.desc) > 0: cell.desc += '\n'
            #cell.desc += desc
            cell.desc = stradd(cell.desc,'\n',desc)

    def add_to_cell_desc(self, extra_desc, level, r, c):
        cell = self.get_cell(level,r,c)
        if cell.desc is None:
            cell.desc = ''
        #if len(cell.desc) > 0: cell.desc += '\n'
        #cell.desc += extra_desc
        cell.desc = stradd(cell.desc,'\n',extra_desc)

    def does_cell_have_fact(self, cell, fact):
        return False #TODO give better impl than this

    def determine_loc(self, loc, relrow, relcol):
        newloc = None
        r = loc.r + relrow
        c = loc.c + relcol
        if loc.level.area.has_valid_coord(c,r):
            newloc = Location(r, c, loc.level, loc.region)
        return newloc

    def is_adj_on_same_level(self, thing1, thing2):
        if thing1.loc is None or thing2.loc is None:
            return False
        d = dist3(thing1.loc.r, thing1.loc.c, thing2.loc.r, thing2.loc.c)
        return (d == 1) and (thing1.loc.level == thing2.loc.level)

    def is_on_same_level_and_within_range(self, thing1, thing2, range):
        if thing1.loc is None or thing2.loc is None:
            return False
        d = dist3(thing1.loc.r, thing1.loc.c, thing2.loc.r, thing2.loc.c)
        return (d <= range) and (thing1.loc.level == thing2.loc.level)

    def put_on_map(self, thing, loc, move=False, moveonsamelevel=False, moveonsameregion=False):
        assert thing is not None
        assert isinstance(thing,HasLocation)
        assert loc is not None
        assert isinstance(loc,Location)

        def buildlogmsg(reason):
            return 'put_on_map() did not because '+str(reason)+'; coords was ('+str(loc)+'); thing was "'+str(thing.describe())+'" ('+str(thing)+')'

        def bugmsg(reason):
            self.bug(buildlogmsg(reason))

        if thing is None:
            s = 'thing was None'
            bugmsg(s)
            return False, s

        region = loc.region
        level = loc.level
        area = level.area
        r = loc.r
        c = loc.c

        if not area.has_valid_coord(c,r):
            s = 'given invalid coords'
            bugmsg(s)
            return False, s

        grid = level.grid
        cell = grid[r][c]
        cell.things.append(thing)
        thing.loc = loc.clone()
        if not move:
            self._add_to_group_in(thing, self.world)
        if not move or (move and not moveonsameregion):
            self._add_to_group_in(thing, region)
        if not move or (move and not moveonsamelevel):
            self._add_to_group_in(thing, level)
        return True, None

    def thing_instantiate(self, thingclass, ctor_extra_args=None):
        raise NotImplementedError()

    def is_coord_in_any_of_these_zones(self, level, rc, zones):
        r,c = rc
        for zone in zones:
            if zone.level is not level:
                continue
            if zone.area.contains(c,r):
                return True
        else: return False

    def put_on_map2(self, thingclass, fuzloc, qty=None, minqty=1, maxqty=1, cohab_allowed=False, zones_disallowed=[], ctor_extra_args=None, preparefn=None, cell_facts_disallowed=[]):
        assert thingclass is not None
        assert issubclass(thingclass,HasLocation)
        assert fuzloc is not None
        assert isinstance(fuzloc,FuzzyLocation)
        #TODO honor cohab_allowed: if false, it won't place in cell it's already placed a prev thing during this particular call (only -- doesn't consider shit that may already be in that cell before the call started)
        #TODO regardless of cohab_allowed, make it not overstack/populate any cell (example: cant put wall into cell where there is already a wall; or person into cell with person; but can add item to ground in a cell where there is already 1+ items; etc.)

        things_placed = []

        br = fuzloc.br
        bc = fuzloc.bc
        r = fuzloc.r
        c = fuzloc.c
        w = fuzloc.w
        h = fuzloc.h
        region = fuzloc.region
        level = fuzloc.level

        if minqty > maxqty:
            minqty = maxqty #TODO better to log bug and return without doing anything probably
        if qty is None:
            qty = minqty + random.randrange(maxqty + 1 - minqty)

        for i in xrange(qty):
            rr = None
            cc = None
            keeptrying = True
            maxattempts = 1000
            attemptsmade = 0
            thing = self.thing_instantiate(thingclass, ctor_extra_args)
            assert thing is not None
            assert isinstance(thing,HasLocation)
            if preparefn is not None:
                preparefn(thing)
            while keeptrying and attemptsmade < maxattempts:
                attemptsmade += 1
                keeptrying = False
                if r is None: 
                    if br is None:
                        br = 0
                    maxrelh = level.area.h - br
                    if h is not None:
                        if h < maxrelh:
                            maxrelh = h
                    rr = br + random.randrange(maxrelh)
                else: rr = r
                if c is None: 
                    if bc is None:
                        bc = 0
                    maxrelw = level.area.w - bc
                    if w is not None:
                        if w < maxrelw:
                            maxrelw = w
                    cc = bc + random.randrange(maxrelw)
                else: cc = c

                cell = self.get_cell(level,rr,cc)
                for fact in cell_facts_disallowed:
                    if self.does_cell_have_fact(cell,fact):
                        keeptrying = True

                if not keeptrying and self.is_coord_in_any_of_these_zones(level, (rr,cc), zones_disallowed):
                    keeptrying = True
                else:
                    loc = Location(rr,cc,level,region)
                    if thing.is_something_there_blocking_placement(loc):
                        keeptrying = True
            if not keeptrying and rr is not None and cc is not None:
                loc = Location(rr,cc,level,region)
                success, reason = self.put_on_map(thing,loc)
                if success:
                    things_placed.append(thing)
            else:
                self.log('gave up trying to place thing %s after %s attempts; moving on to next' % (thing, attemptsmade))

        return things_placed

    def remove_from_map(self, thing, move=False, moveonsamelevel=False, moveonsameregion=False):
        assert thing is not None
        assert isinstance(thing,HasLocation)
        assert thing.loc is not None
        region = thing.loc.region
        level = thing.loc.level
        r = thing.loc.r
        c = thing.loc.c
        cell = level.grid[r][c]
        cell.things.remove(thing)
        thing.loc = None
        if not move:
            self._remove_from_group_in(thing,self.world)
        if not move or (move and not moveonsameregion):
            self._remove_from_group_in(thing,region)
        if not move or (move and not moveonsamelevel):
            self._remove_from_group_in(thing,level)
        return # just for visual sep from following line, i know unnecessary

    def _add_to_group_in(self, thing, groupsowner):
        groupsowner.groups.add_to_group(thing,'things')

    def _remove_from_group_in(self, thing, groupsowner):
        groupsowner.groups.remove_from_group(thing,'things')

    def move_this_from_here_to_there(self, thing, newloc):
        assert thing is not None
        assert isinstance(thing,HasLocation)
        assert newloc is not None
        assert isinstance(newloc,Location)
        samelevel = (thing.loc.level is newloc.level)
        sameregion = (thing.loc.region is newloc.region)
        self.remove_from_map(thing, move=True, moveonsamelevel=samelevel, moveonsameregion=sameregion)
        self.put_on_map(thing, newloc, move=True, moveonsamelevel=samelevel, moveonsameregion=sameregion)

    def list_all_things_in_world(self):
        return self.world.groups.get_group('things')

    def visit_with_all_things_in_world(self, fn2visit):
        things = self.list_all_things_in_world() # returns clone of group's internal list, so safe below to descend out of this class into foreign code that might modify the same group
        for thing in things:
            fn2visit(thing)

    def visit_with_all_things_in_region(self, fn2visit, region):
        things = region.groups.get_group('things')
        for thing in things:
            fn2visit(thing)

    def visit_with_all_things_in_level(self, fn2visit, level):
        things = level.groups.get_group('things')
        for thing in things:
            fn2visit(thing)

    def list_whats_here(self, loc, skiplist=None):
        cell = loc.level.grid[loc.r][loc.c]
        things = list(cell.things)
        if skiplist is not None and len(skiplist) > 0:
            for th in skiplist:
                if th in things:
                    things.remove(th)
        return things

    def visit_with_every_thing_in_location(self, fn2visit, loc):
        r = loc.r
        c = loc.c
        level = loc.level
        cell = level.grid[r][c]
        things = list(cell.things)
        for thing in things:
            fn2visit(thing)

    def get_thingclass_instance_count_in_world(self, thingclass):
        class Foo:
            count = 0
            #def __init__(self):
                #self.count = 0
            def fn2visit(self, thing):
                self.count += 1
        f = Foo()
        self.visit_with_every_thingclass_instance_in_world(f.fn2visit,thingclass)
        return f.count

    def visit_with_every_thingclass_instance_in_world(self, fn2visit, thingclass):
        for reg in self.world.regions:
            region = self.world.regions[reg]
            self.visit_with_every_thingclass_instance_in_region(fn2visit,region,thingclass)

    def visit_with_every_thingclass_instance_in_region(self, fn2visit, region, thingclass):
        for lev in region.levels:
            level = region.levels[lev]
            self.visit_with_every_thingclass_instance_in_level(fn2visit, level,thingclass)

    def visit_with_every_thingclass_instance_in_level(self, fn2visit, level, thingclass):
        #TODO bad perf! better to iterate through a Groups group (for that thingclass, on that level)
        area = level.area
        for r in xrange(area.h):
            for c in xrange(area.w):
                cell = level.grid[r][c]
                things = list(cell.things)
                for thing in things:
                    if isinstance(thing,thingclass):
                        fn2visit(thing)

    def visit_for_every_instance_of_thingclass_there(self, fn2visit, thingclass, loc):
        cell = loc.level.grid[loc.r][loc.c]
        things = list(cell.things)
        for thing in things:
            if isinstance(thing,thingclass):
                fn2visit(thing)

    def count_thingclass_instances_here(self, thingclass, loc):
        class Foo:
            count = 0
            def fn2visit(self, thing):
                self.count += 1
        f = Foo()
        self.visit_for_every_instance_of_thingclass_there(f.fn2visit, thingclass, loc)
        return f.count

    def is_any_instance_of_thingclass_there(self, thingclass, loc):
        return self.count_thingclass_instances_there(thingclass,loc) > 0

    def is_any_instance_of_thingclasses_there(self, thingclasses, loc):
        class Found(Exception): pass

        class VisitHolder:
            answer = False

            def __init__(self, thingclasses):
                self.thingclasses = thingclasses

            def fn2visit(self, thing):
                for klass in self.thingclasses:
                    if isinstance(thing,klass):
                        self.answer = True
                        raise Found()

        vh = VisitHolder(thingclasses)
        try: self.visit_with_every_thing_in_location(vh.fn2visit,loc)
        except Found: pass
        return vh.answer

    def visit_with_every_cell_in_world(self, fn2visit):
        for k in self.world.regions:
            region = self.world.regions[k]
            for k in region.levels:
                level = region.levels[k]
                area = level.area
                def myfn2visit(r, c):
                    fn2visit(r,c,level,region)
                area.visit_with_every_cell_coords(myfn2visit)

    def visit_with_every_cell_in_activeregion(self, fn2visit):
        #TODO instead of self.activeregion, make it so every region can have a list of string attributes, that are app defined, if any; one may be "active"; another may be "vied by user currently", etc.; then in the GeoSystem API let the caller specify to limit his call to only those region(s) that possess a certain attribute tag, like "active", etc.
        region = self.activelevel.region
        for k in region.levels:
            level = region.levels[k]
            area = level.area
            def myfn2visit(r, c):
                fn2visit(r,c,level)
            area.visit_with_every_cell_coords(myfn2visit)

    def report_geography(self, indent='\t', endline='\n'): 
        s = ''
        for rk in self.world.regions:
            reg = self.world.regions[rk]
            s += 'region: %s - %s (%s x %s)%s' % (reg.name, reg.desc, reg.w, reg.h, endline)
            for lk in reg.levels:
                lev = reg.levels[lk]
                s += '%slevel: %s - %s%s' % (indent, lev.name, lev.desc, endline)
                for zk in lev.zones:
                    zone = lev.zones[zk]
                    s += '%szone: %s - %s %s%s' % ((indent*2), zone.name, zone.desc, zone.desc_boundary(), endline)
        return s

class GeoSystemPlugin:
    def __init__(self, geosystem):
        self.geosystem = geosystem

    def getDefaultRegion(self):
        return None

    def getDefaultLevel(self):
        return None

    def bug(self, msg): print msg
    def log(self, msg): print msg
    def debug(self, msg): print msg
    def error(self, msg): print msg

class HasLocation:
    def __init__(self):
        self.loc = None

    def assertHasLocation(self):
        assert self.loc is not None
        self.loc.assertFullyPopulatedAndValid()

    def get_region(self):
        if self.loc is not None: return self.loc.region
        else: return None

    def get_level(self):
        if self.loc is not None: return self.loc.level
        else: return None

    def is_something_there_blocking_placement(self, loc):
        #TODO also block if: man-sized thing there, and self is man-sized (all non-tiny lifeforms block move by other non-tiny lifeforms); items on ground in ell don't block move; tiny lifeforms (mice, bacteria, etc.) do NOT block move; most furniture does not (chairs) but some large/bulky ones might
        level = loc.level
        cell = level.grid[loc.r][loc.c]
        for thing in cell.things:
            if thing.does_self_block_adding_thing_to_self_cell():
                return True
        return False

    def does_self_block_adding_thing_to_self_cell(self):
        return False

class Location:
    def __init__(self, r, c, level, region):
        self.r = r
        self.c = c
        self.level = level
        self.region = region

    def assertFullyPopulatedAndValid(self):
        assertNotNone('region',self.region)
        assertNotNone('level',self.level)
        assertNotNone('r',self.r)
        assertNotNone('c',self.c)
        assert isinstance(self.region,Region)
        assert isinstance(self.level,Level)
        assert self.r >= 0
        assert self.c >= 0

    def any_fields_None(self):
        return self.r is None or self.c is None or self.region is None or self.level is None

    def __eq__(self, other):
        if self is None and other is None:
            return True

        if self is None and other is not None:
            return False

        if self is not None and other is None:
            return False

        return self.r == other.r and self.c == other.c and self.level is other.level and self.region is other.region

    def clone(self, r=None, c=None, level=None, region=None):
        def parse(pname, s, base, loc):
            if s is None:
                return base
            else:
                if isinstance(s,type('')):

                    if s.startswith('+') and len(s) >= 2:
                        if s.startswith('++'):
                            return base + 1
                        else:
                            return base + int(s[1:]) # format: '+1', '+23', etc.

                    elif s.startswith('-') and len(s) >= 2:
                        if s.startswith('--'):
                            return base - 1
                        else:
                            return base - int(s[1:]) # format: '+1', '+23', etc.

                    else:
                        raise 'bad param value format given to clone method for param "'+pname+'"; the param value was: "' + s + '"; while cloning loc: ' + str(loc)
                else: return s #though if here s is not string but int

        #print 'BEFORE handling r inside clone()'
        r = parse('r', r, self.r, self)
        c = parse('c', c, self.c, self)
        #print 'AFTER the parsing of c inside clone()'
        if level is None: level = self.level
        if region is None: region = self.region
        #print 'AFTER handling region inside clone()'
        return Location(r,c,level,region)

    def __str__(self):
        return '(%s,%s) on level %s in region %s' % (self.r, self.c, self.level, self.region)

class FuzzyLocation(Location):
    #TODO __str__ method
    def __init__(self, r=None, c=None, br=None, bc=None, w=None, h=None, level=None, region=None):
        Location.__init__(self,r,c,level,region)
        self.r = r
        self.c = c
        self.br = br
        self.bc = bc
        self.w = w
        self.h = h
        self.level = level
        self.region = region

    def __str__(self):
        return tostr(self)

    def clone(self, r=None, c=None, br=None, bc=None, w=None, h=None, level=None, region=None):
        if r is None:      r      = self.r
        if c is None:      c      = self.c
        if br is None:     br     = self.br
        if bc is None:     bc     = self.bc
        if w is None:      w      = self.w
        if h is None:      h      = self.h
        if level is None:  level  = self.level
        if region is None: region = self.region
        return FuzzyLocation(r,c,br,bc,w,h,level,region)

class World(HasFacts):
    'a game universe; only 1 world exists when playing'
    default_level_w = 20
    default_level_h = 10

    def __init__(self, wh, w=None, h=None):
        HasFacts.__init__(self)
        self.wh = wh #webhack game instance #TODO self.wh should not be defined here but in app-subclass
        self.name = ''
        # has 1+ regions
        self.regions = {} # key is key-name of region
        self.groups = Groups()
        if w is not None:
            self.default_level_w = w
        if h is not None:
            self.default_level_h = h

    def log(self, msg):
        self.wh.log(msg)

class Region(HasFacts):
    'represents a set of closely related levels or areas, like a single building (and all the floors in it); or a single dungeon (and all the levels in it), etc.'
        # has 1+ levels
        # all levels of a region must have the same dimensions (even if portions of any given level are empty, unused, unreachable to the player, etc.)
        # if any two levels have a number as their key in the levels dict, then that number means the relative height/floor/level within that region, so a level with key 2 would be considered "one floor above" a level with key 1
        # levels with string name keys are not assumed to have any relative stack/level/floor relationship with any of the other levels, not by the engine anyway; but an app (wh subclass) is free to interpret it anyway it wishes
        #key in levels is level name or a number indicating relative z-axis in a level stack (like floors of a building)
        #extra traits/attribs (state, qualities, recordkeeping)

    def log(self, msg):
        if hasattr(self,'world') and self.world is not None:
            self.world.log(msg)
        else:
            print msg #TODO bad, should go to real logger of some kind

    def __init__(self, world, w=None, h=None):
        #self.log('Region(): w,h: %s,%s' % (w,h))
        #raise 'yo'
        HasFacts.__init__(self)
        assert world is not None
        assert isinstance(world,World)
        self.world = world # obj ref to world it is part of
        self.name = '' # player-facing name of region, not internal; may or may not be the same as the key in world.regions
        self.desc = '' # player-facing description of the region
        self.levels = {}
        self.groups = Groups()
        if w is None:
            w = world.default_level_w
        if h is None:
            h = world.default_level_h
        self.w = w
        self.h = h
        #self.log('Region: self: w,h: %s,%s' % (self.w, self.h))

    def __str__(self):
        return str(self.name)

class Level(HasFacts): # extend RectArea? or has RectArea?
    INSIDE = 'inside'
    OUTSIDE = 'outside'
    ENVIRONMENTS = (INSIDE,OUTSIDE)

    def __init__(self, region):
        HasFacts.__init__(self)
        assert region is not None
        assert isinstance(region,Region)
        self.region = region # obj ref to region it is part of
        self.name = '' # optional; level may have no name, or not be player visible
        self.desc = ''
        w = region.w
        h = region.h
        #TODO BUG POTENTIAL on line below since order inconsistent between area(w,h) & grid[r][c]
        self.area = RectArea(w,h)
        self.environment = Level.OUTSIDE
        cellmatrix = []
        for r in xrange(h):
            row = []
            for c in xrange(w):
                cell = Cell()
                #cell = Cell(r,c)
                #cell = Cell(self,r,c)
                row.append(cell)
            cellmatrix.append(row)
        self.grid = cellmatrix
        self.zones = {} # key is zone id/name (unique within level only)
        self.groups = Groups()

    def get_zones_of_class(self, zoneclass):
        zones = []
        for k in self.zones:
            zone = self.zones[k]
            if isinstance(zone,zoneclass):
                zones.append(zone)
        return zones

    def __str__(self):
        return str(self.name)

class Zone(HasFacts): # extend RectArea?
    "a zone is a rectangular portion of a single level that has special behaviors, meaning, state, triggers, name, description, inhabitants, effects, etc., distinct from other zones in that level, and distinct from non-zone areas; a cell may be part of 0+ zones, no limit; an example of a good use of a zone would be a house; the rectangular area containing the outer wall boundary of the house, or, it's associated land, would be modelled as a zone"
    def __init__(self, level, bc, br, w, h, name=None, desc=None):
        assert level and isinstance(level,Level)
        assert bc is not None and bc >= 0
        assert br is not None and br >= 0
        assert w is not None and w >= 1
        assert h is not None and h >= 1
        assert not name or isinstance(str(name),type(''))
        assert not desc or isinstance(str(desc),type(''))
        HasFacts.__init__(self)
        self.level = level # obj ref to what level it is part of
        self.name = name
        self.desc = desc
        self.area = RectArea(w,h,bc,br)

    def desc_boundary(self):
        return 'br=%s bc=%s w=%s h=%s' % (self.area.by, self.area.bx, self.area.w, self.area.h)

    def __str__(self):
        return tostr(self)

class Cell(HasFacts):
    #TODO consider convert ctor params to take Location only:
    def __init__(self):
    #def __init__(self, r, c):
    #def __init__(self, level, r, c):
        HasFacts.__init__(self)
        #assert level and isinstance(level,Level)
        #assert r is not None and r >= 0
        #assert c is not None and c >= 0
        #self.level = level # obj ref to what level it is part of
        #self.r = r # (r,c) is this cell's coords in the level grid
        #self.c = c
        self.name = None # optional; usually not set or used (left None)
        self.terrain = None # optional, usually None, and engine assumes a default terrain based on the circumstances
        self.things = [] # list of things in this cell
        #self.traits = None # supplemental metadata, state, conditions about cell
        self.desc = None
        self.seen = False
        #consider: self.zones = [] # list of zones this cell is part of?

    def is_this_here(self, obj):
        if isinstance(self.things,type([])):
            return obj in self.things
        else: return cell.things == obj 

    def has_things(self):
        return len(self.things) > 0

    # was: wh.is_thingclass_there(thingklass, r, c)
    def is_thingclass_here(self, thingclass):
        for thing in self.things:
            if isinstance(thing,thingclass): return True
        return False

class Terrain(HasFacts):
    def __init__(self):
        HasFacts.__init__(self)

    def render_char(self):
        return '.', HtmlColors.BLACK

    def describe(self):
        return 'some terrain'

class Water(Terrain):
    def __init__(self):
        Terrain.__init__(self)

    def render_char(self):
        return '~', HtmlColors.BLUE

    def describe(self):
        return 'some water'

class LevelRenderer:
    def __init__(self, level):
        assert level is not None
        assert isinstance(level,Level)
        self.level = level

    def render(self):
        pass

class StringLevelRenderer(LevelRenderer):
    def __init__(self, level):
        LevelRenderer.__init__(self,level)

    def render(self):
        return ''

#EOF
