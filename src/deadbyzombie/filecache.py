#!/usr/bin/env python2.4

import linecache

#TODO groglib.read_file_lines() has stupid impl; refactor with file.readlines()

#TODO add functionality whereby it can give pre-cached alternate renderings/parsings of the file contents, like:
#    line array with each line split on whitespace
#    line array with each line split on commas

def read_file_as_string(filename, delim=''):
    linecache.checkcache()
    lines = linecache.getlines(filename)
    return delim.join(lines)

def read_file_as_lines(filename):
    linecache.checkcache()
    return linecache.getlines(filename)

#TODO move into groglib.py:
def make_dummy_file(filename, size=1024, char='.'):
    #TODO use random unused filename if none given, and return it so caller knows it
    #TODO the way I build up the string below is probably hugely inefficient; also, look in the python standard library or core/builtins to see if there's already a function that does what I need and/or more efficiently
    f = file(filename,'w')
    s = []
    for i in xrange(size):
        s.append(char)
    s = ''.join(s)
    f.write(s)
    f.close()
    return 'made dummy file %s filled to %s bytes' % (filename,size)

def _file_read_each_time(filename):
    f = file(filename,'r')
    s = f.read()
    f.close()
    return s

def _use_linecache(filename):
    linecache.checkcache()
    lines = linecache.getlines(filename)
    return ''.join(lines)

def _test(testfn, testfilename):
    watch = StopWatch('%s: ' % testfn.__name__)
    ssize = len(testfn(testfilename))
    print '%s -- filesize %s' % (watch.stop(), ssize)

if __name__ == '__main__':
    import lib #from grogdjango lib.py -- though that should go in groglib.py
    from lib import StopWatch

    testfilename = 'dummyfile'

    if False:#notexist(testfilename):
        print make_dummy_file(testfilename,size=1024*1024*4)

    for i in range(5):
        _test(_file_read_each_time, testfilename)

    for i in range(5):
        _test(_use_linecache, testfilename)
