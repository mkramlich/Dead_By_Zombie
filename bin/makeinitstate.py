#!/usr/bin/env python2.7

'''
makeinitstate.py
by Mike Kramlich

a cmdline tool for generating WebHack game init states and saving to disk
'''

if __name__ == '__main__':
    print '\nmakeinitstate'
    import os
    import sys
    import time
    import deadbyzombie.webhack as webhack

    assert len(sys.argv) >= 3, 'Usage: makeinitstate.py <gameclass> [demo|full] <fname>'

    game = sys.argv[1]
    games = ('ZombieHack','WolfenHack') # ZombieHack was my original internal name for Dead By Zombie; WH is another game I wanted to implement using the same shared core engine (webhack) used by DBZ/ZH
    assert game in games, 'game was %s but must be in %s' % (game,games)
    game_class = getattr(webhack,game)

    mode = sys.argv[2]
    modemap = {
        'demo' : 'demo_game_mode_class',
        'full' : 'full_game_mode_class'}
    assert mode in modemap, 'mode was %s but must be in %s' % (mode,modemap.keys())
    mode_class_attr = modemap[mode]
    mode_class = getattr(game_class,mode_class_attr)

    devmode_allowed = False

    fpath = None
    base = 'data/webhack/initstates/'
    if len(sys.argv) > 3:
        fname = sys.argv[3]
        fpath = base + fname
    else:
        unique = str(time.time())
        game_indicator = getattr(game_class,'init_state_file_indicator')
        mode_indicator = mode
        fname = 'state%s.%s.%s.gamestate' % (unique, game_indicator, mode_indicator)
        app_root = os.environ['DBZ'] + '/'
        fpath = app_root + base + fname
    print 'gen new initstate and saving to file: ' + fpath
    webhack.gen_new_gamestate_and_save_to_file(game_class, mode_class, fpath, devmode_allowed)
    print 'success'
