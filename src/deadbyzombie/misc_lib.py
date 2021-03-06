import datetime
import math
import random
import time

logfile = None
cfg = {}
currentTick = 0
debug_enabled = False
#refactor away the currentTick and other ganymede-isms that shouldn't be here

def init_logfile():
    global logfile
    print 'init_logfile() called'
    logfile = file('log.txt','w')    
    print 'logfile is now '+str(logfile)

def log(msg):
    global logfile
    if 'preface_with_tick' in cfg and cfg['preface_with_tick']:
        msg = str(currentTick)+': '+msg
    logfile.write(msg)
    logfile.flush()

def debug(msg):
    if debug_enabled:
        msg += '\n'
        print msg
        log(msg)

def chance(num, denom):
    if num > 0 and denom > 0:
        return random.randrange(denom) < num
    else:
        return False

def rand_range_signed(max_magnitude):
    v = random.randrange(max_magnitude+1)
    if v != 0 and random.randrange(2) == 0:
        v = -v
    return v

def rand_diff(max_magnitude_x, max_magnitude_y):
    xd = rand_range_signed(max_magnitude_x)
    yd = rand_range_signed(max_magnitude_y)
    return (xd, yd)

def rand_range(min, span):
    return min + random.randrange(span + 1)

def rnd_in_range(min, max):
    return min + random.randrange(max - min + 1)

def rnd_bool():
    return random.randrange(2) == 0

def rand_success(chance):
    assert 0.0 <= chance <= 1.0, 'chance param %s must satisfy: 0.0 <= chance <= 1.0' % chance
    return random.random() <= chance

def randex(array):
    return array[random.randrange(len(array))]

def roundmoney(val):
    val = val * 100
    val = int(val)
    val = val / 100
    return val

def read_file(filename):    
    f = file(filename, 'r')     
    s = f.read()
    f.close()
    return s

def read_file_lines(filename):    
    s = read_file(filename)
    return s.splitlines()

def split_width(s, w):
    lns = []
    i = 0
    j = i + w
    while i < len(s):
        if j > len(s):
            j = len(s)
        ln = s[i:j]
        lns.append(ln)
        i = j
        j = i + w
    return lns

def load_string_as_python_to_dict(stryng):
    gd = {}
    ld = {}
    exec stryng in gd, ld
    #debug('gd: ' + str(gd))
    return ld

def load_file_as_python_to_dict(filename):
    s = read_file(filename)
    ld = load_string_as_python_to_dict(s)
    debug('read this for '+filename+':')
    debug('ld: ' + str(ld))
    return ld

class HtmlColors:
    WHITE              = '#FFFFFF'
    BLACK              = '#000000'
    RED                = '#FF0000'
    GREEN              = '#00FF00'
    BLUE               = '#0000FF'
    YELLOW             = '#FFFF00'
    UNKNOWN            = '#00FFFF' # magenta & cyan; i forget which is which
    UNKNOWN2           = '#FF00FF' # see comment for UNKNOWN
    PINK               = '#DD00DD'
    DARKRED            = '#DD0000'
    DARKGREEN          = '#00DD00'
    DARKDARKGREEN      = '#00AA00'
    DARKYELLOW         = '#DDDD00'
    DARKDARKYELLOW     = '#AAAA00'
    DARKDARKDARKYELLOW = '#888800'
    BROWN              = DARKYELLOW
    ORANGE             = DARKYELLOW
    GRAY               = '#DDDDDD'
    DARKGRAY           = '#AAAAAA'

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

class StopWatch:
    def __init__(self, msgpre='', msgsuf=''):
        # I'm aware of DRY violation w/start() but makes a little more accurate
        self.msgpre = msgpre
        self.msgsuf = msgsuf
        self.cputime_stopped = None
        self.walltime_stopped = None
        self.cputime_started = time.clock()
        self.walltime_started = time.time()

    def start(self, msgpre='', msgsuf=''):
        self.msgpre = msgpre
        self.msgsuf = msgsuf
        self.cputime_startedprev = self.cputime_started
        self.cputime_stoppedprev = self.cputime_stopped
        self.walltime_startedprev = self.walltime_started
        self.walltime_stoppedprev = self.walltime_stopped
        self.cputime_started = time.clock()
        self.walltime_started = time.time()

    def stop(self, msgpre=None, msgsuf=None):
        self.cputime_stopped = time.clock()
        self.walltime_stopped = time.time()
        cpudiff = self.cputime_stopped - self.cputime_started
        walldiff = self.walltime_stopped - self.walltime_started
        if msgpre is None:
            msgpre = self.msgpre
        if msgsuf is None:
            msgsuf = self.msgsuf
        return msgpre + float_secs_to_str_ms(cpudiff) + ' cpu, ' + float_secs_to_str_ms(walldiff) + ' wall' + msgsuf

def float_secs_to_str_ms(timediff):
    ms = int(timediff * float(1000))
    return str(ms) + ' ms'

def getattr_withlazyinit(obj, attrname, initvalue):
    if not hasattr(obj,attrname):
        setattr(obj,attrname,initvalue)
    return getattr(obj,attrname)

def sentence_capitalize(s):
    s2 = s
    if len(s) > 0:
        s2 = s[0:1].upper()
        if len(s) > 1:
            s2 += s[1:]
    return s2

def sentence(s):
    if len(s) > 0 and (not s[len(s)-1] in ('?','!','.','"',"'")):
        s += '.'
    return sentence_capitalize(s)

def encode_whitespace_inside_quotes(txt, quotechar="'"):
    #TODO write the reverse of this; a decode function
    #TODO also support "
    #TODO make several passes on txt, each time trying a different char in the string tuple: ", '
    #TODO allow caller to give param specifying a list of valid quote delimiters
    #quotepairs = []
    txt2 = ''
    s = txt
    while True:
        i = s.find(quotechar)
        if i != -1:
            if (i + 1) >= len(s):
                txt2 += s
                break
            j = s.find(quotechar,i+1)
            if j != -1:
                #quotepairs.append( (i,j,) )
                chunk_in_quotes = s[i:j+1] 
                chunk = chunk_in_quotes
                #TODO should also encode any '_' found in chunk by like:
                #chunk = chunk.replace(' ', '\\_')
                chunk = chunk.replace(' ', '_')
                chunk = chunk.replace(quotechar,'')
                encoded_chunk = chunk
                txt2 += s[:i]
                txt2 += encoded_chunk
                if (j+1) >= len(s):
                    break
                else:
                    s = s[j+1:]
            else:
                txt2 += s
                break
        else:
            txt2 += s
            break
    return txt2

VOWELS = ('a','e','i','o','u')
vowels2 = list(VOWELS)
# this ensures we have the uppercase and lowercase versions of each vowel:
for v in VOWELS:
    vowels2.append(v.upper())
VOWELS = vowels2

def awordify(text):
    prefix = 'a'
    if len(text) > 0 and text[0] in VOWELS:
        prefix = 'an'
    return '%s %s' % (prefix, text)

class TextPools:
    #TODO also have a function to claim/declaim
    def __init__(self):
        self.pools = {}

    def get_random_entry(self, poolname):
        pool = None
        try: pool = self.pools[poolname]
        except KeyError, e:
            print '\n\ncaught KeyError: %s' % e
            print 'pools dump:  %s\n\n' % self.pools
            raise e
        return random.choice(pool)

    def define_pools(self, new_defs_dict):
        for k in new_defs_dict:
            items = new_defs_dict[k]
            pool = []
            pool.extend(items)
            self.pools[k] = pool
        #self.pools = dict(new_defs_dict)

    def add_to_pool(self, poolname, newentry):
        pool = self.pools[poolname]
        if isinstance(newentry, type( [] )) or isinstance(newentry, type( () )):
            pool.extend(newentry)
        else:
            pool.append(newentry)

    def add_to_pools(self, extra_defs_dict):
        for k in extra_defs_dict:
            pool = []
            if k in self.pools:
                pool = self.pools[k]
            extra_items = extra_defs_dict[k]
            pool.extend(extra_items)
            self.pools[k] = pool

    def report(self, keydelim=': ', itemdelim=', ', pooldelim='\n'):
        s = ''
        names = list(self.pools.keys())
        names.sort()
        for k in names:
            items = self.pools[k]
            itemblurb = itemdelim.join(items)
            s += k + keydelim + itemblurb + pooldelim
        return s

def assertNotNone(name, val):
    assert val is not None, '%s is None' % name

def stradd(s, delim, str2append):
    if s is None:
        s = ''
    elif len(str(s)) > 0:
        s += str(delim)
    s += str(str2append)
    return s

def isinstance_any(obj, classes):
    for cl in classes:
        if isinstance(obj,cl): return True
    else: return False

def isinstance_all(obj, classes):
    for cl in classes:
        if not isinstance(obj,cl): return False
    else: return True

def isinstance_all_not(obj, classes):
    for cl in classes:
        if isinstance(obj,cl): return False
    else: return True

def isinstance_any_not(obj, classes):
    for cl in classes:
        if not isinstance(obj,cl): return True
    else: return False

def randrangewith(max_inclusive):
    return random.randrange(max_inclusive+1)

def gender2heshe(gender):
    if gender == 'male':     return 'he'
    elif gender == 'female': return 'she'
    else: return 'it'

def gender2himher(gender):
    if gender == 'male':     return 'him'
    elif gender == 'female': return 'her'
    else: return 'it'

def gender2hishers(gender):
    if gender == 'male':     return 'his'
    elif gender == 'female': return 'hers'
    else: return "it's"

def app(lst, item): #TODO bad name since also abbrev for application
    lst.append(item)

def assertNotDirectInstantiate(selfobj, klass):
    assert selfobj.__class__ is not klass, 'cannot instantiate %s, only a subclass, because %s is only a virtual base class (or consider it an interface)' % (klass.__name__, klass.__name__)

def secs_float_diff_to_summary_str(diff):
    diffstr = None
    if diff < 1:
        diffstr = '%s secs' % diff
    elif diff < 60:
        diffstr = '%s secs' % int(diff)
    elif diff < 3600:
        diffstr = '%s mins' % int(diff/60)
    elif diff < 3600 * 24:
        diffstr = '%s hours' % int(diff/3600)
    else:
        diffstr = '%s days' % int(diff/(3600*24))
    #td = datetime.timedelta(seconds=diff)
    #if td.seconds < 60:
    #    diffstr = '%s secs' % td.seconds
    #elif td.days < 1:
    #    diffstr = '%s mins' % (td.seconds / 60)
    #else:
    #    diffstr = '%s days' % td.days
    return diffstr

#TODO upgrade to Table class so i can reuse an instance, persisting table format preferences across multiple applications of the instance to diff data sets
def table(data, header=True, delim='\n', cellspacing=None): #data[row][col]; 0th row contains header text
    # data is a list of lists; the left-side/outer list contains the rows; the right-side lists contain the per-column values for that row
    tableattribs = ''
    if cellspacing is not None:
        tableattribs += ' cellspacing="%s"' % cellspacing
    s = '<table%s>' % tableattribs + delim
    if header:
        headerrow = data[0]
        s += '<tr>' + delim
        for colvalue in headerrow:
            s += '<th> '+str(colvalue)+' </th>' + delim
        s += '</tr>' + delim
    for row in data: #TODO data[1:] ?
        if header and row is headerrow:
            continue # skip header row since already done above
        s += '<tr>' + delim
        for colvalue in row:
            tdattribs = ''
            if isinstance(colvalue,type({})):
                hash = colvalue
                colvalue = hash[table.valuekey]#'_value']
                for k in hash:
                    if k == table.valuekey:
                        continue
                    tdattribs += ' ' + str(k) + '="' + str(hash[k]) + '"'
            #else: #it's just a value object (usually a string or number)
            s += '<td'+tdattribs+'> ' + str(colvalue) + ' </td>' + delim
        s += '</tr>' + delim
    s += '</table>' + delim
    return s
table.valuekey = '_value'

def and_many(vals):
    for v in vals:
        if not v: return False
    else: return True

class Klass: pass #NOTE: USED BY isclass(c) function; yes, feels hacky, but I don't know of a way in Python to determine that with a built-in mechanism.

def isclass(c):
    return type(c) is type(Klass)

def in_range(v, min, max):
    return v >= min and v <= max 

def get_object(obj_name, namespace=None, default=None):
    if namespace is None:
        namespace = globals()
    return (obj_name in namespace.keys() and namespace[obj_name]) or default

def cycle_increment(i, seq):
    i = i + 1
    if i >= len(seq):
        i = 0
    return i

def get_next_with_cycle(cur_item, seq):
    i = seq.index(cur_item)
    new_i = cycle_increment(i,seq)
    return seq[new_i]

def fontcolorize(str, color):
    return '<font color="' + color + '">' + str + '</font>'

def get_doc(obj, attrname):
    return getattr(obj,attrname).__doc__

def bare_class_name(klass):
    toks = klass.__name__.split('.')
    return toks[len(toks)-1]

def tostr(obj):
    s = ''
    for a in dir(obj):
        if a.startswith('__'):
            continue
        attr = getattr(obj,a)
        if callable(attr): continue
        ss = '%s=%s' % (a, attr)
        s = stradd(s,', ',ss)
    return s

def play_synthesized_speech_on_mac(text):
    commands.getoutput('/usr/bin/say '+text)

def dump(obj):
	for a in dir(obj):
		v = getattr(obj,a)
		if not callable(v): print a+' = '+str(v)

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

def read_data(datagroupname):
    return read_file('data/'+datagroupname+'.txt')

def read_data_lines(datagroupname):
    return read_file_lines('data/'+datagroupname+'.txt')    

def load_data_as_python_to_dict(datagroupname):
    fname = 'data/' + datagroupname + '.txt'
    return load_file_as_python_to_dict(fname)

def get_keys_for_value(dicty, value):
    keys = []
    for key in dicty:
        if dicty[key] == value:
            keys.append(key)
    return keys

class State(object):
    def __init__(self): pass
    def enter(self, params={}): pass
    def exit(self): pass

def imagefn(img_fname_base):
    return 'images/' + img_fname_base
		
def get1stKeyWithValue(map,value):
    for i in map.items():
        (k,v) = i
        if v == value: return k
    return None

def equals_any(val, seq):
    for i in seq:
        if val == i:
            return True
    return False

def import_as_dict(modulename):
    mod = __import__(modulename)
    dd = {}
    for k in dir(mod):
        if k.startswith('_'): continue
        dd[k] = getattr(mod,k)
    return dd

def strip_comment_lines(lines):
    return [ln for ln in lines if not ln.startswith('#')]

def file2lines(filename):
    f = file(filename,'r')
    lines = f.readlines()
    f.close()
    return lines

def rstriplines(stringlines):
    lines2 = []
    for line in stringlines:
        line2 = line.rstrip()
        lines2.append(line2)
    return lines2

def safe_getattr_as_bool(o, attrname):
    if hasattr(o,attrname):
        return getattr(o,attrname)
    else:
        return False

class LazyStrWrapper:
    def __init__(self, callee):
        self.callee = callee

    def __str__(self):
        return str(self.callee())

def lazy_str_eval(callee):
    #TODO add support for curried callables (having call params frozen with the callable reference)
    return LazyStrWrapper(callee)
lazy_str_eval.__doc__ = '''
# usage in application:
def expensive_fn():
    # some cpu/memory/latency-expensive task
    # that we only want to do if it's truly needed to render a log msg

logger.debug('some msg: %s', lazy_str_eval(expensive_fn))
# we're not at debug log level currently, therefore the above log msg will NOT be rendered, and expensive_fn will not be called...this is a perf improvement over the following case:

logger.debug('some msg: %s', expensive_fn())
# which is what you would have to do if you JUST used the python logging facility "as designed"
# since 'lazy_str_eval' is a verbose name to have everywhere you could alias it in your application to something like 'lstr' 
'''

def cap_to_len(seq, maxlen):
    if len(seq) > maxlen:
        seq = seq[:maxlen]
    return seq

def getsafe(key, ddict, defaultval=''):
    if key in ddict:
        return ddict[key]
    else:
        return defaultval

def is_item_in_seq_based_on_id(item, seq):
    for s in seq:
        if id(item) == id(s): return True
    else: return False

def get_set_with_class_and_all_super_classes(klass, allset=None):
    if allset is None:
        allset = set()
    if klass not in allset:
        allset.add(klass)
    for cl in klass.__bases__:
        get_set_with_class_and_all_super_classes(cl,allset)
    return allset

def nbsp(num_of_spaces):
    return '&nbsp;' * num_of_spaces

def nameoffn(fn):
    globs = globals()
    for k,v in globs.items():
        if v == fn: return k #TODO use 'is' instead of '=='
    return None #TODO instead throw ex?

def countify(word,qty,trailingphrase=None):
    #TODO get specialwords data from db or file, and load only once at site startup into a cache, read from cache when using here
    s = ''
    if qty == 1:
        s += word
    else:
        specialwords = {'goose':'geese'}
        if word in specialwords:
            s += specialwords[word]
        else:
            s += word + 's'
    if trailingphrase != None:
        s += ' ' + trailingphrase
    return s

def is_alnum(string):
    for c in string:
        if not c.isalnum(): return False
    return True

def is_alnum_or_underscores(string):
    for c in string:
        if not c.isalnum() and c != '_': return False
    return True

def strlist2str(strlist):
    return ''.join(strlist)

def setattr_unless_attrval_not_none(obj, attrname, initvalue):
    if not hasattr(obj,attrname) or obj.attrname is None:
        setattr(obj,attrname,initvalue)

def rnd_using_rpg_die_notation(s):
    # s must be a str in old RPG die roll notation like:
    #     '1d6+2', '2d8', '9d1' or '0d1-1' (the last always yields -1, btw)
    # the letter 'd' can be upper or lower case
    # the modifier portion may be omitted, and must be either a '+' or '-'
    # this will parse that, generate a random number within the specified range
    s = s.lstrip().rstrip().lower()
    pre, post = s.split('d')
    dieqty = int(pre)
    diesidecount = None
    mod = None
    if post.count('+') > 0:
        diesidecount, mod = post.split('+')
        diesidecount = int(diesidecount)
        mod = int(mod)
    elif post.count('-') > 0:
        diesidecount, mod = post.split('-')
        diesidecount = int(diesidecount)
        mod = int(mod) * -1
    else:
        diesidecount = int(post)
        mod = 0
    val = 0
    for roll in range(dieqty):
        val += 1 + random.randrange(diesidecount)
    val += mod
    return val
#TODO write automated test suite for above function. Below is example code for human-readable tests. But should be prog assertions of correctness like unit tests
#        tests = ('1d6+2', '2d8', '9d1', '0d1-1')
#        for t in tests:
#            results = ''
#            for i in range(5):
#                results += str(lib.rnd_using_rpg_die_notation(t)) + ','
#            self.feedback(t + ': ' + results)

def sign(val): #TODO in std lib? and is used by this app?
    if float(val) == 0.0: return 1.0
    else: return val / abs(val)

