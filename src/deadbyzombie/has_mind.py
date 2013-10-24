'''
has_mind.py
by Mike Kramlich
'''

class HasMind:
    def __init__(self, mind2use=None):
        if mind2use is not None:
            self.mind = mind2use 
        else:
            from mind import Mind
            self.mind = Mind()

#EOF
