import Console

'''
This provides a curses-like wrapper around Fredrik Lundh's Console module.
It is rough, does only what I need, and does not claim to be fully curses
compatible.

by Mike Kramlich
'''

COLOR_WHITE = 0 # curses color defs
COLOR_BLACK = 1
COLOR_BLUE = 2
COLOR_RED = 3
COLOR_GREEN = 4
COLOR_YELLOW = 5
COLOR_MAGENTA = 6

# FLC means "Fredrik Lundh's Console.py"
FLC_COLOR_BLACK = FLC_COLOR_000000 = 0
FLC_COLOR_BLUE = FLC_COLOR_0000A8 = 1
FLC_COLOR_GREEN = FLC_COLOR_00A800 = 2
FLC_COLOR_RED = FLC_COLOR_A80000 = 4
FLC_COLOR_MAGENTA = FLC_COLOR_A800A8 = 5
FLC_COLOR_YELLOW = FLC_COLOR_FCFC54 = 14
FLC_COLOR_WHITE = FLC_COLOR_FCFCFC = 15

curses_to_flc = {
    COLOR_WHITE   : FLC_COLOR_WHITE,
    COLOR_BLACK   : FLC_COLOR_BLACK,
    COLOR_BLUE    : FLC_COLOR_BLUE,
    COLOR_RED     : FLC_COLOR_RED,
    COLOR_GREEN   : FLC_COLOR_GREEN,
    COLOR_YELLOW  : FLC_COLOR_YELLOW,
    COLOR_MAGENTA : FLC_COLOR_MAGENTA,
}

con = None

def flc_style(fg, bg):
    return fg + bg * 16

alpha_lower = 'abcdefghijklmnopqrstuvwxyz'
alpha_upper = alpha_lower.upper()

class Scr:
    keysym_to_charstr = {
        'Return' : '\r',
        'space'  : ' ',
        'Up'     : '8',
        'Down'   : '2',
        'Left'   : '4',
        'Right'  : '6'}

    passthru_set = alpha_lower + alpha_upper + ',`'

    def getmaxyx(self):
        return con.size()[1], con.size()[0]

    def erase(self):
        con.page()

    def addstr(self, row, col, txt, attr=None):
        if attr is not None:
            fg, bg = pairs[attr]
            fg_flc = curses_to_flc[fg]
            bg_flc = curses_to_flc[bg]
            style = flc_style(fg_flc, bg_flc)
            con.text(col, row, txt, style)
        else:
            con.text(col, row, txt)

    def move(self, row, col): # move cursor to
        con.pos(col,row)

    def refresh(self):
        pass

    def getch(self):
        while True:
            ev = con.get() #peek() #get() #char()
            print 'ev: %s' % ev
            print 'type(ev): %s' % type(ev)

            print 'dir(ev): %s' % dir(ev)
            print 'ev.type: %s' % ev.type
            if ev.type != "KeyPress":
                continue
            print 'ev.keycode: %i' % ev.keycode
            print 'ev.keysym: "%s"' % ev.keysym
            print 'ev.char: "%s"' % ev.char

            if ev.keysym in self.keysym_to_charstr:
                ch = self.keysym_to_charstr[ev.keysym]
                break
            elif (ev.char != "") and ev.char in self.passthru_set:
                ch = ev.char
                break
            else:
                continue
        print 'scr.getch() returning: "%s"' % ch
        return ch

def wrapper(callback_fn, *sysargs):
    global con
    con = Console.getconsole()
    con.title('Dead By Zombie')
    scr = Scr()
    callback_fn(scr,sysargs)

#class Textbox():
#    pass

def start_color():
    pass

pairs = {}

def init_pair(id, fg, bg):
    pairs[id] = (fg, bg)

def color_pair(id):
    return id

digits = '0123456789'
input_field_passthru_set = alpha_lower + alpha_upper + digits + '-'

def input_field(h, w, r, c): # NOTE this is NOT a curses function, but a quick hack func replacement for Textbox
    cc = c
    rr = r
    txt = ''
    while True:
        con.pos(c,r)
        ev = con.get()
        if ev.type != "KeyPress":
            continue
        if ev.keysym == 'Return':
            break
        if ev.keysym == 'Left':
            if cc > c:
                cc -= 1
                txt = txt[:-1]
                con.text(c,r,txt.ljust(20))
            continue
        if ev.keysym == 'Right':
            if cc < c + w - 1:
                cc += 1
            continue
        
        ch = None
        if ev.keysym == 'space':
            ch = ' '
        elif (ev.char != "") and ev.char in input_field_passthru_set:
            ch = ev.char

        if ch and cc < c + w:
            con.text(cc,rr,ch)
            txt += ch
            if cc < c + w - 1:
                cc += 1
    return txt

