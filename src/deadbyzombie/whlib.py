
def extract_info_from_filename(filename):
    #filename pattern: 'gamestate-g%s-u%s-t%s-%s-%s.dat' % (gameid, userid, tock, date, time)
    pieces = filename.split('-')
    gameid = int( pieces[1][1:] )
    userid = int( pieces[2][1:] )
    tock   = int( pieces[3][1:] )
    date   =      pieces[4] # NOTE just a string
    time   =      pieces[5].split('.')[0] # NOTE just a string
    return gameid, userid, tock, date, time
