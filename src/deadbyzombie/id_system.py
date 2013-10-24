'''
id_system.py
by Mike Kramlich
'''

import pprint

class IdSystem:
    debug_enabled = False

    def __init__(self):
        self.ids = {}

    def log(self, msg):
        print msg

    def debug(self, msg):
        if self.debug_enabled:
            self.log(msg)

    def id_new(self, obj):
        #self.debug('id_new() called with: %s' % obj)
        idd = hex(id(obj))
        self.ids[idd] = obj
        self.debug('id_new() returning: %s' % idd)
        return idd

    def ids_dump(self):
        pprint.pprint(self.ids)

class HasID:
    def __init__(self, idsys):
        self.myid = idsys.id_new(self)

    def id_thing(self):
        return self.myid

    def id_thing_pp(self):
        # pp in method name means pretty printed, as in pprint
        return '[ID: %s]' % self.id_thing()

    def withid_helper(self, withid):
        idstr = ''
        if withid:
            idstr = ' %s' % self.id_thing_pp()
        return idstr
