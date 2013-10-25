from __future__ import with_statement

import linecache
import os
import pickle
import random
import sys
import textwrap

if sys.platform == 'darwin' or sys.platform.startswith('linux'):
    import curses
    import curses.textpad
    import curses.wrapper
    from curses.textpad import Textbox
elif sys.platform == 'win32':
    import Console_curses_wrapper as curses
    from Console_curses_wrapper import input_field

DBZ = '.'

from deadbyzombie import webhack
from webhack import FilePersister, deserialize
from misc_lib import chance, HtmlColors, load_file_as_python_to_dict, rand_diff, rand_range, rand_success, read_file_lines, rnd_in_range, split_width

app_name = 'Dead By Zombie'

class Obj: pass

# Saved Game State
mapw = 0
maph = 0
msgs = []

# Non-Saved State
mode = None
scr = None

mode_stack = []

def mode_push(new_mode):
    global mode
    mode_stack.append(mode)
    mode = new_mode
    
def mode_pop():
    global mode
    mode = mode_stack.pop()

def msgs_display_limit():
    return scr.getmaxyx()[0] - (maph + 1)

def msg(txt):
    global msgs
    if len(msgs) >= msgs_display_limit():
        msgs = msgs[1:]
    msgs.append(txt)

def centerp(row, txt):
    col = (scr.getmaxyx()[1] - len(txt)) / 2
    addstr(row,col,txt)

def addstr(row, col, txt, attr=None):
    try:
        if attr is not None:
            scr.addstr(row,col,txt,attr)
        else:
            scr.addstr(row,col,txt)
    except curses.error:
        pass #TODO this is tmp hack fix for the addstr ERR bug when term size doesn't provide enough rows & cols for my curses session window

def in_range(min, val, max):
    return val >= min and val < max

def hitanykey():
    scr.getch()

current_state = None

def change_current_state(new_state):
    global current_state
    current_state = new_state

def cur_state():
    return current_state

class Mode:
    name = ''
    default_attr = None
    should_mode_pop_after_handle_ch = False
    should_mode_pop_when_key_not_handled = False
    should_mode_pop_when_any_key_pressed = False

    def __init__(self):
        self.disabled_keys = {}
        id = color_id('white-black')
        self.default_attr = curses.color_pair(id)

    def handle_getch(self, ch):
        #TODO upgrade this feature to work in the new universe:
        if ch in self.disabled_keys:
            return

        #TODO load only once, at app startup, and cache results
        main_cfg = load_file_as_python_to_dict('conf/config-main')
        keys = main_cfg['keys']
        cur_set_name = main_cfg['set']
        default_set_name = 'default-set' #TODO ditto

        retval = None

        mode_name = self.__class__.__name__

        handled = False

        if mode_name in keys[cur_set_name]:
            handled = True
            methname = None
            if ch in keys[cur_set_name][mode_name]:
                methname = keys[cur_set_name][mode_name][ch]
            elif ch in keys[default_set_name][mode_name]:
                methname = keys[default_set_name][mode_name][ch]
            else:
                handled = False

            if methname:
                meth = getattr(self,methname)
                retval = meth()

        if self.should_mode_pop_after_handle_ch:
            mode_pop()
        elif not handled and self.should_mode_pop_when_key_not_handled:
            mode_pop()
        elif self.should_mode_pop_when_any_key_pressed:
            mode_pop()

        return retval
        
    def addstr(self, row, col, txt, color_name=None):
        if color_name is not None:
            id = color_id(color_name)
            #raise '%s' % id
            attr = curses.color_pair(id)
        else:
            attr = self.default_attr
        addstr(row,col,txt,attr)

    def refresh_display(self):
        scr.erase()
        self.render()
        scr.move(scr.getmaxyx()[0]-1, scr.getmaxyx()[1]-1)
        scr.refresh()

    def render(self):
        pass

    def describe_hp(self):
        you = cur_state().you
        hp = '%s/%s' % (you.hp, you.hp_max)
        color_name = None
        if you.hp == you.hp_max:
            color_name = 'green-black'
        elif you.hp <= 2:
            color_name = 'red-black'
        elif you.hp <= (you.hp_max / 2):
            color_name = 'yellow-black'
        return ( ('HP: ',None),
                 (hp,    color_name) )

    def describe_stomach_for_render(self):
        you = cur_state().you
        stomach = '%s/%s' % (you.get_stomach(), you.get_stomach_size())
        color = None
        if you.get_stomach() == you.get_stomach_size():
            color = 'green-black'
        elif you.get_stomach() <= 2:
            color = 'red-black'
        elif you.get_stomach() <= (you.get_stomach_size() / 2):
            color = 'yellow-black'
        return (('stomach: ',None), (stomach,color))

    def post_handle_getch(self):
        pass
        
    def usercmd(self, cmd, params={}):
        wh = cur_state()
        if wh.is_usercmd_allowed(cmd):
            success, reason, should_persist_to_disk, replace_wh_with = wh.dispatch_usercmd(cmd,params)
        
    def usercmd_rel(self, cmd, relrow, relcol):
        wh = cur_state()
        if wh.is_usercmd_allowed(cmd):
            params = {'relrow':relrow, 'relcol':relcol}
            success, reason, should_persist_to_disk, replace_wh_with = wh.dispatch_usercmd(cmd,params)    

def render_feedback_as_lines(wrap_w):
    lines = []

    for m in cur_state().msgs:
        msg = m[0] #m[1] is tock when msg created
        shouldmakehtmlsafe = m[2] #TODO unused
        newlines2EOL = m[3] #TODO unused
        lines_by_newline = msg.split('\n')
        for line in lines_by_newline:
            lines_by_wrap = split_width(line,wrap_w)
            for line2 in lines_by_wrap:
                lines.append(line2)
    return lines


def is_allowed_by_version(what):
    whats_disallowed_in_demo = ('route', 'stairs')
    if is_only_demo_allowed() and what in whats_disallowed_in_demo:
        return False
    else:
        return True


class DefaultMode(Mode):
    name = 'Default Mode'
    toparea_h = 7

    def render(self):
        self.render_mode_info()
        self.render_tock()
        self.render_locinfo()
        self.render_hp()
        self.render_stomach()
        self.render_coords()
        self.render_wielded()
        self.render_map()
        self.render_feedback()
        self.render_version_mode()

    def render_version_mode(self):
        if is_only_demo_allowed():
            self.addstr(0,20,'(%s)' % describe_version_unlocked())

    def render_mode_info(self):
        if mode.__class__ is DefaultMode:
            self.addstr(0, 0, app_name)
        else:
            self.addstr(0, 0, mode.name)
        
    def render_tock(self):
        wh = cur_state()
        tock = wh.ev.tock
        self.addstr(2, 0, 'time: %s' % tock)
        
    def render_locinfo(self):
        wh = cur_state()
        geo = wh.geo
        world = geo.world
        shownlevel = geo.activelevel
        shownregion = shownlevel.region
        region = shownregion
        level = shownlevel
        you = wh.you
        loc = you.loc

        self.addstr(2,12, wh.get_time_of_day_desc())
        self.addstr(2,24, level.name)
        self.addstr(2,44, region.name)

        znames = geo.report_zone_names_for(loc)
        znames_msg = znames
        self.addstr(5,15, '%s' % znames_msg)

    def render_hp(self):
        c = 0
        for chunk in self.describe_hp():
            txt, color = chunk
            self.addstr(4,c,txt,color)
            c += len(txt)

    def render_stomach(self):
        c = 20
        for chunk in self.describe_stomach_for_render():
            txt = chunk[0]
            color = chunk[1]
            self.addstr(4, c, txt, color)
            c += len(txt)

    def render_coords(self):
        coords = None
        loc = cur_state().you.loc
        if loc is not None:
            coords = '%s,%s' % (loc.r, loc.c)
        self.addstr(5,0,'loc: (%s)' % coords)

    def render_wielded(self):
        wh = cur_state()
        if wh.you.has_wielded():
            self.addstr(4,40,'{%s}' % wh.you.describe_wielded())
            
    def row_qty_in_shown_map(self):
        shownlevel = cur_state().geo.activelevel
        val = len(shownlevel.grid) #grid is array of map rows
        return val

    def shownlevel(self):
        wh = cur_state()
        geo = wh.geo
        world = geo.world
        return cur_state().geo.activelevel

    def feedback_h(self):
        min_feedback_h = 5
        scr_h = scr.getmaxyx()[0]
        lev = self.shownlevel()
        return max(min_feedback_h, scr_h - self.toparea_h - lev.area.get_wh()[1])

    def render_map(self):
        fgcolordefault = HtmlColors.BLACK

        wh = cur_state()
        you = wh.you
        geo = wh.geo
        world = geo.world
        shownlevel = geo.activelevel
        map = shownlevel.grid

        scr_h = scr.getmaxyx()[0]
        scr_w = scr.getmaxyx()[1]
        view_scr_base_r = self.toparea_h
        view_scr_base_c = 0
        map_base_r = 0
        map_base_c = 0
        self.view_h = scr_h - self.toparea_h - self.feedback_h()
        self.view_w = scr_w
        your_loc = cur_state().you.loc

        # try to center the map viewport on the player's position:
        map_base_r = your_loc.r - (self.view_h / 2)
        map_base_c = your_loc.c - (self.view_w / 2)
        lev_h = shownlevel.area.get_wh()[1]
        lev_w = shownlevel.area.get_wh()[0]
        if lev_h - map_base_r < self.view_h:
            map_base_r -= self.view_h - (lev_h - map_base_r)
        if lev_w - map_base_c < self.view_w:
            map_base_c -= self.view_w - (lev_w - map_base_c)
        if map_base_r < 0:
            map_base_r = 0
        if map_base_c < 0:
            map_base_c = 0

        def map_coords_in_viewport(r, c):
            scr_r = r - map_base_r + view_scr_base_r
            scr_c = c - map_base_c + view_scr_base_c
            return view_scr_base_r <= scr_r < view_scr_base_r + self.view_h and \
                view_scr_base_c <= scr_c < view_scr_base_c + self.view_w

        for r,row in enumerate(map):
            for c,cell in enumerate(row):
                if not map_coords_in_viewport(r,c): continue
                ch = '?'
                color = None
                if cell.seen or wh.cfg('you_see_all'):
                    thing2render = wh.most_important_thing_here_to_show_on_map_other_than_you(cell)
                    if thing2render is None: #means nothing there or nothing visible
                        ch = '.'
                        if cell.terrain is not None:
                            ch, color = cell.terrain.render_char()
                        else:
                            color = fgcolordefault
                    else:
                        ch, color = thing2render.render_char()
                        if ch is None:
                            ch = '?'
                        if color is None:
                            color = fgcolordefault
                else:
                    ch = '?'
                    color = fgcolordefault
                if cell.is_this_here(you): #ensures You always visible
                    ch, color = you.render_char()
                if color is None:
                    color = fgcolordefault
                color_name = hc2name(color)

                scr_r = view_scr_base_r + r - map_base_r
                scr_c = view_scr_base_c + c - map_base_c
                if scr_r < view_scr_base_r:
                    scr_r = self.toparea_h
                if scr_c < view_scr_base_c:
                    scr_c = self.toparea_w
                try:
                    self.addstr(scr_r,scr_c,ch,color_name)
                except:
                    raise '%s %s %s %s %s %s %s' % (scr_r, scr_c, ch, color_name, r, map_base_r, view_scr_base_r)

    def render_feedback(self):
        scr_h = scr.getmaxyx()[0]
        scr_w = scr.getmaxyx()[1]
        wrap_w = scr_w - 1

        lines = render_feedback_as_lines(wrap_w)

        r = scr_h - self.feedback_h() + 1
        c = 0
        max_r = scr_h - 1
        all_shown = True
        for line in lines:
            if r > max_r:
                all_shown = False
                break
            try:
                self.addstr(r,c,line)
                r += 1
            except:
                raise 'r %s     max_r %s     c %s\n"%s"' % (r, max_r, c, line)

        if not all_shown:
            more_msg = 'MORE'
            self.addstr(max_r, scr_w - len(more_msg) - 1, more_msg, 'black-white')

    def back_to_IntroScreen(self):
        mode_pop()

    def walk_northeast(self):
        self.usercmd_rel('walk',-1,+1)

    def walk_north(self):
        self.usercmd_rel('walk',-1,0)

    def walk_northwest(self):
        self.usercmd_rel('walk',-1,-1)

    def walk_east(self):
        self.usercmd_rel('walk',0,+1)

    def walk_west(self):
        self.usercmd_rel('walk',0,-1)

    def walk_southeast(self):
        self.usercmd_rel('walk',+1,+1)

    def walk_south(self):
        self.usercmd_rel('walk',+1,0)

    def walk_southwest(self):
        self.usercmd_rel('walk',+1,-1)

    def wait(self):
        self.usercmd('wait')

    def pickup_all(self):
        self.usercmd('pickup_all')

    def route(self):
        if is_allowed_by_version('route'):
            self.usercmd('route')
        else:
            cur_state().feedback('That is not allowed in this version of the game.')

    def stairs(self):
        if is_allowed_by_version('stairs'):
            self.usercmd('stairs')
        else:
            cur_state().feedback('That is not allowed in this version of the game.')

    def story(self):
        self.usercmd('story')

    def memories(self):
        self.usercmd('memories')

    def skills(self):
        self.usercmd('skills')

    def modechg_FeedbackScreen(self):
        mode_push(FeedbackScreen())

    def modechg_ChooseRelDirToAttack(self):
        mode_push(ChooseRelDirToAttack())

    def modechg_ChooseRelDirToOpen(self):
        mode_push(ChooseRelDirToOpen())

    def modechg_ChooseRelDirToClose(self):
        mode_push(ChooseRelDirToClose())

    def modechg_ChooseRelDirToMakeBarricade(self):
        mode_push(ChooseRelDirToMakeBarricade())

    def modechg_ChooseRelDirToMakeSafe(self):
        mode_push(ChooseRelDirToMakeSafe())

    def modechg_ChooseThingToEat(self):
        mode_push(ChooseThingToEat())

    def modechg_ChooseHealableItemToUse(self):
        mode_push(ChooseHealableItemToUse())

    def modechg_ChooseItemToRead(self):
        mode_push(ChooseItemToRead())

    def modechg_ChooseItemToWield(self):
        mode_push(ChooseItemToWield())

    def modechg_ChooseItemToUnwield(self):
        mode_push(ChooseItemToUnwield())

    def modechg_ChooseItemToWear(self):
        mode_push(ChooseItemToWear())

    def modechg_ChooseItemToUnwear(self):
        mode_push(ChooseItemToUnwear())

    def modechg_ChooseThingToDrop(self):
        mode_push(ChooseThingToDrop())

    def modechg_ChooseThingToPickup(self):
        mode_push(ChooseThingToPickup())

    def modechg_InventoryView(self):
        mode_push(InventoryView())

    def modechg_ThingsHere(self):
        mode_push(ThingsHere())

    def modechg_ChooseRelDirToAskStay(self):
        mode_push(ChooseRelDirToAskStay())

    def modechg_ChooseRelDirToAskNotStay(self):
        mode_push(ChooseRelDirToAskNotStay())

    def modechg_ChooseRelDirToAskFollow(self):
        mode_push(ChooseRelDirToAskFollow())

    def modechg_ChooseRelDirToAskNotFollow(self):
        mode_push(ChooseRelDirToAskNotFollow())

    def modechg_QuickSave(self):
        mode_push(QuickSave())

    def modechg_QuickLoad(self):
        mode_push(QuickLoad())

    def toggle_devmode(self):
        self.usercmd('devmode')

    def toggle_you_starves(self):
        self.usercmd('starves')

    def toggle_you_see_all(self):
        self.usercmd('see_all')

    def toggle_you_hit_always(self):
        self.usercmd('hit_always')

    def toggle_you_kill_always(self):
        self.usercmd('kill_always')

    def toggle_you_invuln(self):
        self.usercmd('invuln')

    def quit(self):
        return False
            
class ChooseRelDirToActMode(DefaultMode):
    name = 'Choose Rel Dir To Act Mode'
    cmd = None
    should_mode_pop_after_handle_ch = True
    
    def __init__(self, cmd):
        DefaultMode.__init__(self)
        self.cmd = cmd

    def act_northeast(self):
        self.usercmd_rel(self.cmd,-1,+1)

    def act_north(self):
        self.usercmd_rel(self.cmd,-1,0)

    def act_northwest(self):
        self.usercmd_rel(self.cmd,-1,-1)

    def act_east(self):
        self.usercmd_rel(self.cmd,0,+1)

    def act_west(self):
        self.usercmd_rel(self.cmd,0,-1)

    def act_southeast(self):
        self.usercmd_rel(self.cmd,+1,+1)

    def act_south(self):
        self.usercmd_rel(self.cmd,+1,0)

    def act_southwest(self):
        self.usercmd_rel(self.cmd,+1,-1)
        
class ChooseRelDirToAttack(ChooseRelDirToActMode):
    name = 'Choose Rel Dir To Attack'
    def __init__(self):
        ChooseRelDirToActMode.__init__(self,'attack')
        
class ChooseRelDirToOpen(ChooseRelDirToActMode):
    name = 'Choose Rel Dir To Open'
    def __init__(self):
        ChooseRelDirToActMode.__init__(self,'open')
        
class ChooseRelDirToClose(ChooseRelDirToActMode):
    name = 'Choose Rel Dir To Close'
    def __init__(self):
        ChooseRelDirToActMode.__init__(self,'close')

class ChooseRelDirToMakeBarricade(ChooseRelDirToActMode):
    name = 'Choose Rel Dir To Make Barricade'
    def __init__(self):
        ChooseRelDirToActMode.__init__(self,'barricade')

class ChooseRelDirToMakeSafe(ChooseRelDirToActMode):
    name = 'Choose Rel Dir To Make Safe'
    def __init__(self):
        ChooseRelDirToActMode.__init__(self,'mark_safecell')

class ChooseRelDirToAskStay(ChooseRelDirToActMode):
    name = 'Choose Rel Dir To Ask Stay'
    def __init__(self):
        ChooseRelDirToActMode.__init__(self,'ask_not_move')

class ChooseRelDirToAskNotStay(ChooseRelDirToActMode):
    name = 'Choose Rel Dir To Ask Not Stay'
    def __init__(self):
        ChooseRelDirToActMode.__init__(self,'ask_not_not_move')

class ChooseRelDirToAskFollow(ChooseRelDirToActMode):
    name = 'Choose Rel Dir To Ask Follow'
    def __init__(self):
        ChooseRelDirToActMode.__init__(self,'ask_follow')

class ChooseRelDirToAskNotFollow(ChooseRelDirToActMode):
    name = 'Choose Rel Dir To Ask Not Follow'
    def __init__(self):
        ChooseRelDirToActMode.__init__(self,'ask_not_follow')

def split_list(srclist, max_size_per): #TODO is std Python function for this?
    lists = []
    curlist = None
    for item in srclist:
        if curlist is None or (len(curlist) + 1 > max_size_per):
            curlist = []
            lists.append(curlist)
        curlist.append(item)
    return lists

class ThingsView(Mode):
    name = None
    list_prefix = None
    cmd = None
    should_mode_pop_after_handle_ch = False
    should_mode_pop_when_key_not_handled = True
    things_by_page = {}
    page = 0
    cursor = 0 
    things_per_page = 30
    header_h = 6

    def __init__(self):
        Mode.__init__(self)
        self.things_per_page = scr.getmaxyx()[0] - self.header_h
        self.eligible_items = self.get_eligible_items()
        self.things_by_page = split_list(self.eligible_items, self.things_per_page)

    def get_eligible_items(self):
        pass
    
    def render(self):
        self.addstr(0, 0, self.name)
        self.render_body_at_row(4)

    def get_line_prefix(self, i):
        return ((self.cursor == i) and '-> ') or '   '

    def render_body_at_row(self, base_r):
        if self.list_prefix:
            self.addstr(base_r, 0, '%s:' % self.list_prefix)
        page_qty = len(self.things_by_page) > 0 and len(self.things_by_page) or 1
        page_tmpl = 'Page %s of %s'
        page_c = scr.getmaxyx()[1] - len(page_tmpl) #TODO len() not strictly correct but close enough
        self.addstr(base_r,page_c, page_tmpl % (self.page+1, page_qty))
        if len(self.things_by_page) < 1:
            return
        for i,thing in enumerate(self.things_by_page[self.page]):
            r = base_r + 2 + i
            prefix = self.get_line_prefix(i)
            txt = '%s%s' % (prefix, self.render_entry(thing))
            color_name = ((self.cursor == i) and 'black-white') or None
            self.addstr(r, 0, txt, color_name)

    def render_entry(self, thing):
        desc = thing.full_describe()
        you = cur_state().you
        if you.does_wield(thing):
            desc += ' (wielded)'
        if you.does_wear(thing):
            desc += ' (worn)'
        return desc

    def cursor_up(self):
        if len(self.things_by_page) < 1:
            mode_pop()
            return
        newcursor = self.cursor - 1
        if newcursor < 0:
            newpage = self.page - 1
            if newpage < 0:
                return
            else:
                self.page = newpage
                self.cursor = len(self.things_by_page[self.page]) - 1
        else:
            self.cursor = newcursor

    def cursor_down(self):
        if len(self.things_by_page) < 1:
            mode_pop()
            return
        newcursor = self.cursor + 1
        if newcursor >= self.things_per_page:
            newpage = self.page + 1
            if newpage < len(self.things_by_page):
                self.page = newpage
                self.cursor = 0
        elif newcursor >= len(self.things_by_page[self.page]):
            return
        else:
            self.cursor = newcursor

    def do_cmd_with_thing(self):
        if self.cmd is not None:
            thing = None
            try:
                if len(self.things_by_page) > 0:
                    things_on_page = self.things_by_page[self.page]
                    if self.cursor < len(things_on_page):
                        thing = things_on_page[self.cursor]
                        thingid = thing.id_thing()
                        self.usercmd(self.cmd, {'what':thingid})
            except Exception, ex:
                raise '%s: %s %s' % (ex, self.page, self.cursor)
        mode_pop()

class ChooseThingToEat(ThingsView):
    name = 'Choose Thing To Eat'
    list_prefix = 'Edible Items'
    cmd = 'eat'

    def get_eligible_items(self):
        edibles = []
        wh = cur_state()
        inv = wh.you.list_inventory()
        for item in inv:
            edible, reason = wh.you.can_self_eat_this(item)
            if edible:
                edibles.append(item)
        return edibles

    def render(self):
        ThingsView.render(self)
        c = 0
        for chunk in self.describe_stomach_for_render():
            txt = chunk[0]
            color = chunk[1]
            self.addstr(2, c, txt, color)
            c += len(txt)

class ChooseHealableItemToUse(ThingsView):
    name = 'Choose Healing Item To Use'
    list_prefix = 'Healing Items'
    cmd = 'use'

    def get_eligible_items(self):
        return cur_state().you.list_inventory_of_class(webhack.HealItem)

    def render(self):
        ThingsView.render(self)
        c = 0
        for chunk in self.describe_hp():
            txt, color = chunk
            self.addstr(2,c,txt,color)
            c += len(txt)

class ChooseItemToRead(ThingsView):
    name = 'Choose Item To Read'
    list_prefix = 'Readable Items'
    cmd = 'read'

    def get_eligible_items(self):
        return cur_state().you.list_inventory_of_class(webhack.Readable)

class ChooseItemToWield(ThingsView):
    name = 'Choose Item To Wield'
    list_prefix = 'Unwielded Unworn Items'
    cmd = 'wield'

    def get_eligible_items(self):
        return cur_state().you.nonwielded_nonworn_list()

class ChooseItemToUnwield(ThingsView):
    name = 'Choose Item To Unwield'
    list_prefix = 'Wielded Items'
    cmd = 'unwield'

    def get_eligible_items(self):
        return cur_state().you.wielded_list()

class ChooseItemToWear(ThingsView):
    name = 'Choose Item To Wear'
    list_prefix = 'Unwielded Unworn Items'
    cmd = 'wear'

    def get_eligible_items(self):
        return cur_state().you.nonwielded_nonworn_list()

class ChooseItemToUnwear(ThingsView):
    name = 'Choose Item To Unwear'
    list_prefix = 'Worn Items'
    cmd = 'unwear'

    def get_eligible_items(self):
        return cur_state().you.worn_list()

class ChooseThingToDrop(ThingsView):
    name = 'Choose Thing To Drop'
    list_prefix = 'Inventory'
    cmd = 'drop'

    def get_eligible_items(self):
        return cur_state().you.list_inventory()

class ChooseThingToPickup(ThingsView):
    name = 'Choose Thing to Pickup'
    list_prefix = 'Carriable Items'
    cmd = 'pickup'

    def get_eligible_items(self):
        wh = cur_state()
        you = wh.you
        things = wh.geo.list_whats_here(you.loc,skiplist=(you,))
        things = [th for th in things
            if not th.is_invisible()
            and you.can_you_pickup_this(th)
            and th.can_be_picked_up()]
        return things

    def render(self):
        ThingsView.render(self)
        c = 0
        for chunk in self.describe_stomach_for_render():
            txt = chunk[0]
            color = chunk[1]
            self.addstr(2, c, txt, color)
            c += len(txt)

class InventoryView(ThingsView):
    name = 'Inventory'
    list_prefix = 'Items Carried'
    cmd = None

    def get_eligible_items(self):
        inv = []
        you = cur_state().you
        inv.extend(you.wielded_list())
        inv.extend(you.worn_list())
        inv.extend(you.nonwielded_nonworn_list())
        return inv

class ThingsHere(ThingsView):
    name = 'Area Report'
    list_prefix = 'Things Here'
    cmd = None

    def get_eligible_items(self):
        wh = cur_state()
        you = wh.you
        things = wh.geo.list_whats_here(you.loc, skiplist=(you,))
        return [th for th in things if not th.is_invisible()]

class FeedbackScreen(ThingsView):
    name = None
    list_prefix = 'Feedback'
    cmd = None
    header_h = 2

    def get_eligible_items(self):
        scr_w = scr.getmaxyx()[1]
        wrap_w = scr_w - 1
        return render_feedback_as_lines(wrap_w)

    def render(self):
        self.render_body_at_row(0)

    def render_entry(self, entry):
        return entry

    def get_line_prefix(self, i):
        return ''

def saves_location():
    return '%s/%s' % (DBZ, 'saves')

def quick_save_location():
    return '%s/%s' % (saves_location(), 'quicksave')

def load_from_default_initstate():
    load_fname_from_initstates('default.zh.full.gamestate')

def load_state_from_fpath(fpath):
    wh = None
    f = file(fpath,mode='rb')
    data = f.read()
    f.close()
    if len(data) > 0:
        wh = deserialize(data,'wh',protocol=2)
        wh.size = len(data)
        return wh

def load_fname_from_saves(fname):
    fpath = '%s/%s' % (saves_location(), fname)
    wh = load_state_from_fpath(fpath)
    change_current_state(wh)

def load_fname_from_initstates(fname):
    fpath = '%s/%s' % ('data/webhack/initstates', fname)
    wh = load_state_from_fpath(fpath)
    change_current_state(wh)

def load_from_quicksave():
    fpath = quick_save_location()
    wh = load_state_from_fpath(fpath)
    change_current_state(wh)
    return fpath

class QuickSave(Mode):
    name = None
    should_mode_pop_after_handle_ch = True

    def __init__(self):
        Mode.__init__(self)

        fpath = quick_save_location()
        per = FilePersister()
        wh = cur_state()
        wh.size = per.persist_state_with_filename(wh,fpath)
        #TODO handle gracefully if save attempt fails, and show message to user, without exiting the app
        self.result = 'The quick save attempt was a success!'
        self.fpath = fpath

    def render(self):
        self.addstr(0,0,'Quick Save')
        self.addstr(2,0, self.result)
        self.addstr(4,0, '(saved to: %s)' % self.fpath)

class QuickLoad(Mode):
    name = None
    should_mode_pop_after_handle_ch = True

    def __init__(self):
        Mode.__init__(self)
        try:
            fpath = load_from_quicksave()
        #TODO handle gracefully if load attempt fails, and show message to user, without exiting the app
            self.result = 'The quick load attempt was a success!'
        except IOError:
            self.result = 'The quick load attempt FAILED!'
        self.fpath = fpath

    def render(self):
        self.addstr(0,0,'Quick Load')
        self.addstr(2,0, self.result)
        self.addstr(4,0, '(loaded from: %s)' % self.fpath)

def in_bounds(x, y, x0, y0, w, h):
    val = (x >= x0 and x <= x0 + w and y >= y0 and y <= y0 + h)
    return val

class SplashScreen(Mode):
    name = None
    box_r = 3
    box_c = 7
    box_w = 65
    box_h = 12

    def __init__(self):
        scr_h = scr.getmaxyx()[0]
        scr_w = scr.getmaxyx()[1]

        self.zombies = []
        qty = rnd_in_range(400,500)
        for i in range(qty):
            r = rnd_in_range(0,scr_h-2)
            c = rnd_in_range(0,scr_w-2)
            z = (r,c)
            self.zombies.append(z)
        

    def render(self):
        scr_h = scr.getmaxyx()[0]
        scr_w = scr.getmaxyx()[1]

        def center(r, txt, color_name=None):
            c = scr_w / 2 - len(txt) / 2
            self.addstr(r,c,txt,color_name)

        def box(r, c, h, w, ch):
            for y in range(r,r+h): # fill in with blank space before drawing the outer walls
                for x in range(c,c+w):
                    self.addstr(y,x,' ')
            for rr in (r, r+h-1):
                for cc in range(c, c+w):
                    self.addstr(rr,cc,ch)
            for rr in range(r, r+h):
                for cc in (c, c+w-1):
                    self.addstr(rr,cc,ch)

        def centered_box(h, w, ch):
            c = scr_w / 2 - w / 2
            r = scr_h / 2 - h / 2
            box(r,c,h,w,ch)

        for z in self.zombies:
            r,c = z
            self.addstr(r,c,'Z','red-black')

        centered_box(self.box_h,self.box_w,'#')

        center(self.box_r+10, app_name.upper())

        # Teaser Quotes
        wrap_w = 60
        center(self.box_r+13, "Day is for the living. Night is for the dead.")

        center(scr_h - 14, 'Hit Any Key', 'black-white')

    def handle_getch(self, ch):
        mode_push(IntroScreen())

    def text(self, r, c, txt, wrap_w):
        lns = txt.split('\n')
        for ln in lns:
            if len(ln.strip()) == 0:
                r += 1
                continue
            lns_wrapped = textwrap.wrap(ln,wrap_w)
            for ln2 in lns_wrapped:
                self.addstr(r,c,ln2)
                r += 1


class IntroScreen(Mode):
    name = None
    should_mode_pop_after_handle_ch = False
    cursor = 0

    def __init__(self):
        Mode.__init__(self)
        self.choices = (
            ('Resume Play',         'resume_play'),
            ('Continue Saved Game', 'continue_from_last_game'),
            ('Restart Game',        'restart_game'),
            ('About',               'about'),
            ('Quit',                'quit'))
        self.game_loaded = False

    def render(self):
        self.addstr(0,0, app_name)
        r = 2
        for i,entry in enumerate(self.choices):
            label = entry[0]
            target_methname = entry[1]
            if not self.game_loaded and target_methname == 'resume_play':
                if self.cursor == 0:
                    self.cursor = 1
                continue
            color_name = ((self.cursor == i) and 'black-white') or None
            self.addstr(r,0,label,color_name)
            r += 1

    def cursor_up(self):
        self.cursor -= 1
        if self.cursor < 0:
            self.cursor = 0

    def cursor_down(self):
        self.cursor += 1
        if self.cursor >= len(self.choices):
            self.cursor = len(self.choices) - 1

    def execute_choice_at_cursor(self):
        entry = self.choices[self.cursor]
        target_methname = entry[1]
        meth = getattr(self,target_methname)
        return meth()

    def resume_play(self):
        mode_push(DefaultMode())

    def continue_from_last_game(self):
        try:
            load_from_quicksave()
        except IOError:
            load_from_default_initstate()
        self.game_loaded = True
        self.move_cursor_to_resume_play_choice()
        mode_push(DefaultMode())

    def restart_game(self):
        load_from_default_initstate()
        self.game_loaded = True
        self.move_cursor_to_resume_play_choice()
        mode_push(DefaultMode())

    def about(self):
        mode_push(AboutScreen())

    def quit(self):
        return False

    def move_cursor_to_resume_play_choice(self):
        found = -1
        for i,choice in enumerate(self.choices):
            if choice[1] == 'resume_play':
                found = i
                break
        if found > -1:
            self.cursor = found


class AboutScreen(Mode):
    name = None
    should_mode_pop_when_any_key_pressed = True

    def render(self):
        ver = 1.1
        txt = (app_name,
            '',
            'version %s' % ver,
            '',
            'https://github.com/mkramlich/Dead_By_Zombie',
            'http://synisma.neocities.org/deadbyzombie.html',
            '',
            'design, writing & programming by Mike Kramlich',
            '',
            'promotional artwork by Richard Pace',
            "    Richard's website and online gallery:",
            '    http://richardpace.deviantart.com')
        r = 0
        for ln in txt:
            self.addstr(r,0,ln)
            r += 1
        self.addstr(r+4,0,'Hit Any Key','black-white')

def is_full_allowed():
    return True

def is_only_demo_allowed():
    return not is_full_allowed()

def describe_version_unlocked():
    return 'FULL'

def reset_world():
    global px, py, msgs 

    px = 10
    py = 10

    msgs = []

def restart_game():
    global mode
    reset_world()
    mode = BrowseMapMode()

colormap = None
        
def color_set(color_name, fg, bg):
    global colormap
    
    if colormap is None:
        colormap = {}
    id = len(colormap.keys()) + 1
    colormap[color_name] = id
    curses.init_pair(id,fg,bg)
    
def color_id(color_name):
    return colormap[color_name]
    
html_color_to_name_map = {}
d = html_color_to_name_map
d[HtmlColors.WHITE] = 'black-white'
d[HtmlColors.BLACK] = 'white-black'
d[HtmlColors.RED] = 'red-black'
d[HtmlColors.GREEN] = 'white-black'
d[HtmlColors.BLUE] = 'blue-black'
d[HtmlColors.YELLOW] = 'white-black'
d[HtmlColors.UNKNOWN] = 'white-black' #magenta or cyan
d[HtmlColors.UNKNOWN2] = 'white-black' # opposite of above
d[HtmlColors.PINK] = 'white-black'
d[HtmlColors.DARKRED] = 'white-black'
d[HtmlColors.DARKGREEN] = 'dark-green-black'
d[HtmlColors.DARKDARKGREEN] = 'white-black'
d[HtmlColors.DARKYELLOW] = 'dark-yellow-black'
d[HtmlColors.DARKDARKYELLOW] = 'white-black'
d[HtmlColors.DARKDARKDARKYELLOW] = 'white-black'
d[HtmlColors.BROWN] = d[HtmlColors.DARKYELLOW]
d[HtmlColors.ORANGE] = d[HtmlColors.DARKYELLOW]
d[HtmlColors.GRAY] = 'white-black'
d[HtmlColors.DARKGRAY] = 'white-black'

def hc2attr(html_color):
    name = None
    if html_color in html_color_to_name_map:
        name = html_color_to_name_map[html_color]
    else:
        name = 'white-black'
    return curses.color_pair(color_id(name))
    
def hc2name(html_color):
    if html_color in html_color_to_name_map:
        return html_color_to_name_map[html_color]
    else:
        return 'white-black'

def init(stdscr, *args):
    global scr, mode

    scr = stdscr
    curses.start_color() 
    color_set('white-black',       curses.COLOR_WHITE,  curses.COLOR_BLACK)
    color_set('white-blue',        curses.COLOR_WHITE,  curses.COLOR_BLUE)
    color_set('white-red',         curses.COLOR_WHITE,  curses.COLOR_RED)
    color_set('white-yellow',      curses.COLOR_WHITE,  curses.COLOR_YELLOW)
    color_set('white-green',       curses.COLOR_WHITE,  curses.COLOR_GREEN)
    color_set('black-yellow',      curses.COLOR_BLACK,  curses.COLOR_YELLOW)
    color_set('blue-black',        curses.COLOR_BLUE,   curses.COLOR_BLACK)
    color_set('yellow-black',      curses.COLOR_YELLOW, curses.COLOR_BLACK)
    color_set('black-magenta',     curses.COLOR_BLACK,  curses.COLOR_MAGENTA)
    color_set('dark-green',        curses.COLOR_WHITE,  curses.COLOR_GREEN)
    color_set('red',               curses.COLOR_WHITE,  curses.COLOR_RED)
    color_set('dark-yellow',       curses.COLOR_WHITE,  curses.COLOR_YELLOW)
    color_set('dark-green-black',  curses.COLOR_GREEN,  curses.COLOR_BLACK)
    color_set('dark-yellow-black', curses.COLOR_YELLOW, curses.COLOR_BLACK)
    color_set('green-black',       curses.COLOR_GREEN,  curses.COLOR_BLACK)
    color_set('yellow-black',      curses.COLOR_YELLOW, curses.COLOR_BLACK)
    color_set('red-black',         curses.COLOR_RED,    curses.COLOR_BLACK)
    color_set('black-white',       curses.COLOR_BLACK,  curses.COLOR_WHITE)

    min_req_w = mapw + 5
    min_req_h = maph + 5
    if scr.getmaxyx()[1] < min_req_w or scr.getmaxyx()[0] < min_req_h:
        raise 'terminal window size must be at least %s cols by %s lines!' % (min_req_w, min_req_h)

    mode = SplashScreen()
    mode.refresh_display()

    while True:
        chi = scr.getch()
        ch = chi
        if in_range(0,chi,256):
            ch = chr(chi)
        retval = mode.handle_getch(ch)
        if retval is not None and not retval: # is it False but not None?
            break
        mode.post_handle_getch()
        mode.refresh_display()


def main():
    curses.wrapper(init, sys.argv)
