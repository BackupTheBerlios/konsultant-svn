import os
from ConfigParser import RawConfigParser as ConfigParser

from paella.db.midlevel import Environment

from kdecore import KConfigBackEnd
from kdecore import KConfig, KConfigBase       
from kdecore import KSimpleConfig
from kdecore import KConfigSkeleton

class BaseSkel(ConfigParser):
    def __init__(self):
        ConfigParser.__init__(self)
        self.add_section('database')
        self.set('database', 'dbhost', 'localhost')
        self.set('database', 'dbname', 'konsultant')
        self.set('database', 'dbuser', os.environ['USER'])
        
    def getdata(self):
        return self._sections
    

class DefaultSkeleton(KConfigSkeleton):
    def __init__(self, name='DefaultSkeleton'):
        KConfigSkeleton.__init__(self, name)
        print 'hello there'
        cfg = BaseSkel()
        data = cfg.getdata()
        for section in cfg.sections():
            self.setCurrentGroup(section)
            print self.currentGroup()
            for opt in cfg.options(section):
                self.addItemString(opt, data[section][opt], cfg.get(section, opt))
                print opt
        self.setDefaults()
        
                

class DbConfigBackEnd(KConfigBackEnd):
    def __init__(self, db):
        base = KConfigBase()
        KConfigBackEnd.__init__(self, base, 'konsultant_dbconfig')
        self.uname = os.environ['USER']
        self.db = db
        self.env = Environment(self.db.conn, 'config', 'username')
        
    def parseConfigFiles(self):
        pass
    

    
class BaseConfig(KSimpleConfig):
    def __init__(self):
        KSimpleConfig.__init__(self, 'konsultantrc')

class DefaultSkeleton(KConfigSkeleton):
    def __init__(self, cfg):
        print cfg
        KConfigSkeleton.__init__(self, cfg)
        
