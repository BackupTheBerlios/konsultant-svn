import tempfile

class PgPoolConfig(object):
    def __init__(self, cfg):
        object.__init__(self)
        data = {}
        cfg.setGroup('database')
        data['backend_host_name'] = cfg.readEntry('dbhost')
        data['backend_port'] = cfg.readEntry('dbport')
        cfg.setGroup('pgpool')
        data['port'] =cfg.readEntry('port')
        keys = ['num_init_children', 'max_pool',
                'connection_life_time']
        for key in keys:
            data[key] = cfg.readEntry(key)
        self.data = data

    def write(self):
        lines = ['%s = %s' % (k,v) for k,v in self.data.items()]
         return '\n'.join(lines) + '\n'

class PgPool(object):
    def __init__(self, cfg):
        object.__init__(self)
        self.cfg = PgPoolConfig(cfg)
        self.cfg.setGroup('pgpool')
        self.cmd = self.cfg.readEntry('command')
        
    def run(self):
        tmp, path = tempfile.mkstemp('konsultant', 'pgpoolconf')
        tmp = file(path, 'w')
        tmp.write(self.cfg.write())
        tmp.close()
        os.system('%s -f %s' % (self.cmd, path))
        
        
        
