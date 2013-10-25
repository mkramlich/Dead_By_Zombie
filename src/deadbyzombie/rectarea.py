'''
rectarea.py
by Mike Kramlich
'''

from misc_lib import in_range, rnd_in_range, rnd_bool, equals_any
import random

class RectArea:
    edge_pref_allowed_values = (None,'top','bottom','left','right')

    #TODO upgrade RectArea.adj_cells() fn to internally cache results of previous calls, and return values from that cache; maybe make that behavior a config optional (based on boolean flag field of the RectArea instance, that is set by the app at ctor time)...better way to implement that is to ensure that all RA instances have a ref to a behind-the-scenes singleton cache of values. That way each RA does not maintain it's own private cache of adj cells. in webhack, there will be many levels that have the same w,h, so therefore each of those level's sets of adj cell caches would be identical (in relative terms).

    def __init__(self, width, height, bx=0, by=0):
        self.bx = bx
        self.by = by
        self.w = width
        self.h = height

    def __str__(self):
        return '%sx%s at %s,%s' % (self.w, self.h, self.bx, self.by)

    def get_wh(self):
        return self.w, self.h

    def get_base_xy(self):
        return self.bx, self.by

    def get_boundary_params(self):
        return self.bx, self.by, self.w, self.h

    def get_rnd_xy(self):
        x = rnd_in_range(self.bx, self.w-1)
        y = rnd_in_range(self.by, self.h-1)
        return x,y

    def get_rnd_xy_on_edge(self, edge_pref=None):
        assert equals_any(edge_pref,self.edge_pref_allowed_values), 'edge_pref was %s but must be one of these values: %s' % (edge_pref,self.edge_pref_allowed_values)
        if edge_pref is None:
            if rnd_bool(): edge_pref = 'top-or-bottom'
            else: edge_pref = 'left-or-right'
        if 'top' in edge_pref or 'bottom' in edge_pref:
            x = rnd_in_range(self.bx, self.w-1)
            if edge_pref == 'top':
                y = self.by
            elif edge_pref == 'bottom':
                y = self.by + self.h - 1 
            else:
                y = random.choice( (self.by, self.by+self.h-1) )
        else:
            y = rnd_in_range(self.by, self.h-1)
            if edge_pref == 'left':
                x = self.bx
            elif edge_pref == 'right':
                x = self.bx + self.w - 1 
            else:
                x = random.choice( (self.bx, self.bx+self.w-1) )
        return x,y

    def is_at_least_this_big(self, w, h):
        return self.w >= w and self.h >= h

    def contains(self, x, y):
        return self.has_valid_coord(x,y)

    def visit_with_every_coord(self, fn2call):
        for xr in xrange(self.w):
            x = self.bx + xr
            for yr in xrange(self.h):
                y = self.by + yr
                fn2call(x,y)

    def overlaps(self, area):
        class GotHit(Exception): pass
        def fn2visit(x,y):
            if area.contains(x,y):
                raise GotHit
        #TODO perf: this is prob an unecessarily slow/inefficient/tedious way to do it; instead, figure out the math
        try: self.visit_with_every_coord(fn2visit)
        except GotHit: return True
        else: return False

    def has_valid_coord(self, x, y):
        return y is not None and x is not None \
            and y >= self.by and y < self.by + self.h \
            and x >= self.bx and x < self.bx + self.w

    def is_within_area(self, area2):
        assert isinstance(area2,RectArea)
        return in_range( self.by,            area2.by, area2.h-1) \
            and in_range(self.by + self.h-1, area2.by, area2.h-1) \
            and in_range(self.bx,            area2.bx, area2.w-1) \
            and in_range(self.bx + self.w-1, area2.bx, area2.w-1)

    def adj_cells(self, x, y, griddist=1):
        'griddist is not a true distance but how many cell steps it would take to reach a particular cell from some origin cell; an adj cell has a griddist of 1; the origin cell is 0 grid dist from itself'
        #TODO make it populate and draw from a cache of answers
        #TODO actually, since in WebHack all levels in a region have the same area size, then they should all use the same cache, rather than each RectArea having it's own distinct private cache; to be even more efficient, all regions in world that have the same area size should use the same exact cache instance

        assert griddist >= 0, 'RectArea.adj_cells: given bad griddist param %s; must be >= 0' % griddist
        validadjcells = []
        for yrel in xrange(griddist * -1, griddist + 1): # -1,2
            for xrel in xrange(griddist * -1, griddist + 1): # -1,2
                xx = x + xrel
                yy = y + yrel
                if xx == x and yy == y:
                    continue
                if self.has_valid_coord(xx,yy):
                    validadjcells.append( (xx,yy) )
        return validadjcells

    def safeify_rel_coords(self, xold, yold, xrel, yrel):
        x = xold + xrel
        y = yold + yrel

        if   x < self.bx:           xrel = 0
        elif x >= self.bx + self.w: xrel = 0

        if   y < self.by:           yrel = 0
        elif y >= self.by + self.h: yrel = 0

        return (yrel, xrel)

    def visit_with_every_cell_coords(self, fn2visit):
        #TODO instance field option to instead use a cached list of coord tuples (stuffed into an instance field), and iterate through that to get r,c values to pass to fn2visit()
        bx, by, w, h = self.bx, self.by, self.w, self.h
        for y in xrange(by + h):
            for x in xrange(bx + w):
                fn2visit(y,x)

    # Instance Methods - end

    # Class Methods

    def new_rnd_area(min_w=1, max_w=1000, min_h=1, max_h=1000):
        w,h = new_rnd_wh(min_w,max_w,min_h,max_h)
        return RectArea(w,h,0,0)

    def new_rnd_wh(min_w=1, max_w=1000, min_h=1, max_h=1000):
        assert min_w <= max_w
        assert min_h <= max_h
        w = rnd_in_range(min_w,max_w)
        h = rnd_in_range(min_h,max_h)
        return w,h

# RectArea class - end

#EOF
