class App:
    def feedback(self, msg):
        pass

class Mode:
    def __init__(self, app):
        'we assume app is App interface compatible'
        self.app = app

    def process_user_command(self, input):
        cmd = input[0]
        cmdmap = self.get_cmdmap()
        if cmd in cmdmap:
            fn = cmdmap[cmd]
            self.dispatch_and_post(fn,input)
        else:
            self.unrecognized_input()

    def dispatch_and_post(self, fn, input):
        retval = fn(input)
        self.post_command_task(retval)

    def post_command_task(self, cmd_handler_retval):
        pass

    def get_cmdmap(self):
        cmdmap = {}
        for attrname in dir(self):
            attr = getattr(self,attrname)
            if Command.is_command(attr):
                if self.should_include_attr(attr):
                    cmdmap[attr.key] = attr
        return cmdmap

    def should_include_attr(self, attr):
        return True

    def render_avail_commands(self):
        s = ''
        cmdmap = self.get_cmdmap()
        if len(cmdmap.keys()) > 0:
            s += 'cmds:\n'
        for cmd in cmdmap:
            s += '%s' % cmd
            fn = cmdmap[cmd]
            for p in fn.params:
                t = '<%s:%s>' % (p['name'],p['type'])
                optional = 'optional' in p and p['optional']
                if optional:
                    t = '[%s]' % t
                s += ' %s' % t
            s += ' : %s' % fn.__doc__
            s += '\n'
        return s

    def render_ui(self):
        pass

    def feedback(self, msg):
        self.app.feedback(msg)

    def unrecognized_input(self):
        self.feedback('unrecognized input, no action taken')

class Command:
    def __init__(self, key, paramsdef=[]):
        self.key = key
        self.paramsdef = paramsdef

    def __call__(self, methdef):
        methdef.command = True
        methdef.key = self.key
        methdef.params = self.paramsdef
        return methdef

    @staticmethod
    def is_command(attr):
        return hasattr(attr,'command') and getattr(attr,'command')

