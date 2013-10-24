'''
language_helper.py
by Mike Kramlich
'''


class LanguageHelper:
    def __init__(self):
        self.init_verbmatrix()

    def init_verbmatrix(self):
        self.verbmatrix = None

        #TODO these defs should come from a file:

        self.add_vm_entry('to be','singular','present','is')
        self.add_vm_entry('to be','singular','past','was')
        self.add_vm_entry('to be','plural','present','are')
        self.add_vm_entry('to be','plural','past','were')

        self.add_vm_entry('to have','singular','present','has')
        self.add_vm_entry('to have','singular','past','had')
        self.add_vm_entry('to have','plural','present','have')
        self.add_vm_entry('to have','plural','past','had')

        self.add_vm_entry('to say','singular','present','says')
        self.add_vm_entry('to say','singular','past','said')
        self.add_vm_entry('to say','plural','present','say')
        self.add_vm_entry('to say','plural','past','said')

        self.add_vm_entry('to attack','singular','present','attacks')
        self.add_vm_entry('to attack','singular','past','attacked')
        self.add_vm_entry('to attack','plural','present','attack')
        self.add_vm_entry('to attack','plural','past','attacked')

        self.add_vm_entry('to hit','singular','present','hits')
        self.add_vm_entry('to hit','singular','past','hit')
        self.add_vm_entry('to hit','plural','present','hit')
        self.add_vm_entry('to hit','plural','past','hit')

        self.add_vm_entry('to miss','singular','present','misses')
        self.add_vm_entry('to miss','singular','past','missed')
        self.add_vm_entry('to miss','plural','present','miss')
        self.add_vm_entry('to miss','plural','past','missed')

        self.add_vm_entry('to die','singular','present','dies')
        self.add_vm_entry('to die','singular','past','died')
        self.add_vm_entry('to die','plural','present','die')
        self.add_vm_entry('to die','plural','past','died')

        self.add_vm_entry('to try','singular','present','tries')
        self.add_vm_entry('to try','singular','past','tried')
        self.add_vm_entry('to try','plural','present','try')
        self.add_vm_entry('to try','plural','past','tried')

        self.add_vm_entry('to pickup','singular','present','picks up')
        self.add_vm_entry('to pickup','singular','past','picked up')
        self.add_vm_entry('to pickup','plural','present','pickup')
        self.add_vm_entry('to pickup','plural','past','picked up')

        self.add_vm_entry('to drop','singular','present','drops')
        self.add_vm_entry('to drop','singular','past','dropped')
        self.add_vm_entry('to drop','plural','present','drop')
        self.add_vm_entry('to drop','plural','past','dropped')

        self.add_vm_entry('to carry','singular','present','carries')
        self.add_vm_entry('to carry','singular','past','carried')
        self.add_vm_entry('to carry','plural','present','carry')
        self.add_vm_entry('to carry','plural','past','carried')

        self.add_vm_entry('to digest','singular','present','digests')
        self.add_vm_entry('to digest','singular','past','digested')
        self.add_vm_entry('to digest','plural','present','digest')
        self.add_vm_entry('to digest','plural','past','digested')

    def add_vm_entry(self, verb, plurality, tense, word, verbmatrix=None):
        if verbmatrix is None:
            if self.verbmatrix is None:
                self.verbmatrix = {}
            verbmatrix = self.verbmatrix
        vm = verbmatrix
        if verb not in vm:
            vm[verb] = {}
        if plurality not in vm[verb]:
            vm[verb][plurality] = {}
        vm[verb][plurality][tense] = word

    def itverbify(self, it, verb, plurality='singular', tense='present', verbmatrix=None):
        #TODO add other common verbs I use: move, attack, etc.
        #TODO extract to class, and make it generic (no WH-specific code in it)
        #TODO accumulate records of what request param combos 'missed' the matrix, because they had no definition, and make a way for me to easily and frequently find out what all the misses were so I can go and manually populate them
        #TODO the defintions/entries should come from a file
        #TODO the API should allow the app to prog register entries with it

        if verbmatrix is None:
            verbmatrix = self.verbmatrix
        vm = verbmatrix

        self.debug('LH.itverbify: %s  %s  %s' % (verb, plurality, tense))
        self.debug('LH.itverbify: my entries for the verb: %s' % str(vm[verb]))
        verbportion = vm[verb][plurality][tense]
        self.debug('LH.iterviby: rendered verb: %s\n' % verbportion)
        return '%s %s' % (it.describe(), verbportion)

    def possessivify(self, it):
        return "%s's" % it.describe() 

    def debug(self, msg):
        pass

#EOF
