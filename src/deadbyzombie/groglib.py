# groglib.py
# a collection of miscellaneous homegrown Python library code
# by Mike Kramlich

import random
import math
import commands

def read_with_includes(filepath):
    basepath = ''
    if '/' in filepath:
        lastslashpos = filepath.rfind('/')
        basepath = filepath[:lastslashpos+1]
    lines = read_file_lines(filepath)
    if len(lines) < 1:
        return ''
    includeprefix = '#include '
    lines2 = []
    for line in lines:
        if line.startswith(includeprefix):
            rest = line[len(includeprefix):]
            filepath2include = basepath + rest
            #print 'would include: %s' % filepath2include
            body_from_include = read_with_includes(filepath2include)
            addlines = body_from_include.splitlines()
            lines2.extend(addlines)
        else:
            lines2.append(line)
    return '\n'.join(lines2)

def load_config_for_env(confdir='conf/', topfname='config', envkey='env', envfnamesuffix='.cfg'):
    fname = confdir + topfname
    topcfg = load_file_as_python_to_dict(fname)
    #print fname + ':\n' + str(topcfg)
    env = topcfg[envkey]
    fname = confdir + env + envfnamesuffix
    s = read_with_includes(fname)
    #envcfg = load_file_as_python_to_dict(fname)
    envcfg = load_string_as_python_to_dict(s)
    return env, envcfg

def percent(val_float):
    return '%s%%' % (val_float * 100)

def load_csv_file(filename):
    #TODO make it skip file lines begining with # - have opt param to enable/disable this feature, as well as to override what prefix to use instead of #
    #TODO option to silently ignore/skip blank lines (lines w/only whitespace)
    outlines = []
    lines = read_file_lines(filename)
    for line in lines:
        line = line.lstrip().rstrip()
        tup = line.split(',')
        newtup = []
        for v in tup:
            v = v.lstrip().rstrip()
            newtup.append(v)
        outlines.append(newtup)
    return outlines

def commandcd(dir,cmd):
	return commands.getoutput('cd '+dir+'; '+cmd)

def extract1stColAsList(lines):
	retval = []
	for line in lines:
		words = line.split(' ')
		col1 = words[0]
		retval.append(col1)
	return retval

def randex(array):
    return array[random.randrange(len(array))]

def roundmoney(val):
    val = val * 100
    val = int(val)
    val = val / 100
    return val

def rand_range(min, span):
    return min + random.randrange(span + 1)

def rand_range_signed(max_magnitude):
    v = random.randrange(max_magnitude+1)
    if v != 0 and random.randrange(2) == 0: v = -v
    return v

def rand_diff(max_magnitude_x, max_magnitude_y):
    xd = rand_range_signed(max_magnitude_x)
    yd = rand_range_signed(max_magnitude_y)
    return (xd, yd)

def read_file(filename):    
    f = file(filename, 'r')     
    s = f.read()
    f.close()
    return s

def read_file_lines(filename):    
    s = read_file(filename)
    return s.splitlines()

def read_data(datagroupname):
    return read_file('data/'+datagroupname+'.txt')

def read_data_lines(datagroupname):
    return read_file_lines('data/'+datagroupname+'.txt')    

def load_data_as_python_to_dict(datagroupname):
    fname = 'data/' + datagroupname + '.txt'
    return load_file_as_python_to_dict(fname)

def load_file_as_python_to_dict(filename):
    s = read_file(filename)
    ld = load_string_as_python_to_dict(s)
    debug('read this for '+filename+':')
    debug('ld: ' + str(ld))
    return ld

def load_string_as_python_to_dict(stryng):
    gd = {}
    ld = {}
    exec stryng in gd, ld
    #debug('gd: ' + str(gd))
    return ld

def get_keys_for_value(dicty, value):
    keys = []
    for key in dicty:
        if dicty[key] == value:
            keys.append(key)
    return keys

def dist(x1,y1, x2,y2):
    xd = abs(x2 - x1)
    yd = abs(y2 - y1)
    tmp = (xd * xd) + (yd * yd)
    d = math.sqrt(tmp)
    d = int(d)
    return d
    
def dist2(x1,y1, x2,y2):
    xd = abs(x2 - x1)
    yd = abs(y2 - y1)
    if xd < yd: return xd
    else: return yd    

def dist3(x1,y1, x2,y2):
    #TODO this is a FIXED re-impl of dist2 -- migrate apps off of using dist2 and instead onto dist3 (I'm pretty sure, but judge it on case by case basis)
    xd = abs(x2 - x1)
    yd = abs(y2 - y1)
    if xd > yd: return xd
    else: return yd    

class Groups:
    def __init__(self):
        self.groups = {}
    
    def add_to_group(self, thing, group_name):
        "method param 'group_name' can be a string name, or, a list of string names"
        gns = []
        if isinstance(group_name, list):
            gns = group_name
        else:
            gns.append(group_name)
    
        for gn in gns:
            group = None
            if gn in self.groups:
                group = self.groups[gn]
            else:
                group = self.groups[gn] = []
            if not thing in group:
                group.append(thing)
            #TODO post event?
    
    def remove_from_group(self, thing, group_name):
        group = self.groups[group_name]
        if thing in group:
            group.remove(thing)
            #TODO post event?
        else:
            #TODO fix me: following thnig.name only works for sprites not classes!:
            print 'remove_from_group(): thing '+str(thing)+' ('+str(thing)+') not in group '+str(group_name)+" so can't remove"
            
    def remove_from_all_groups(self, thing):
        for gn in self.groups:
            self.remove_from_group(thing, gn)
        
    def clear_group(self, group_name):
        self.groups[group_name] = []
        #TODO post event?
        
    def clear_all_groups(self):
        for gn in self.groups:
            self.groups[gn] = []
        
    def get_group(self, group_name):
        group = None
        if group_name in self.groups:
            group = self.groups[group_name]        
        else:
            group = []
            self.groups[group_name] = group
        return list(group)

    def in_group(self, thing, group_name):
        if group_name in self.groups:
            return thing in self.groups[group_name]
        else:
            return False

class State(object):
    def __init__(self): pass
    def enter(self, params={}): pass
    def exit(self): pass


logfile = None

cfg = {}

currentTick = 0
#refactor away the currentTick and other ganymede-isms that shouldn't be here
def log(msg):
    global logfile
    if 'preface_with_tick' in cfg and cfg['preface_with_tick']:
        msg = str(currentTick)+': '+msg
    logfile.write(msg)
    logfile.flush()

debug_enabled = False

def debug(msg):
    if debug_enabled:
        msg += '\n'
        print msg
        log(msg)

def init_logfile():
    global logfile
    print 'init_logfile() called'
    logfile = file('log.txt','w')    
    print 'logfile is now '+str(logfile)

def imagefn(img_fname_base):
    return 'images/' + img_fname_base

def play_synthesized_speech_on_mac(text):
    commands.getoutput('/usr/bin/say '+text)

def dump(obj):
	for a in dir(obj):
		v = getattr(obj,a)
		if not callable(v): print a+' = '+str(v)
		
def chance(num,denom):
    if num > 0 and denom > 0: return (random.randrange(denom) < num)
    else: return False

def get1stKeyWithValue(map,value):
    for i in map.items():
        (k,v) = i
        if v == value: return k
    return None
