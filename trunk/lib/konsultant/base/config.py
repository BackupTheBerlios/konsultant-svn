import os
from ConfigParser import RawConfigParser as ConfigParser

from konsultant.pdb.midlevel import Environment

from kdecore import KConfigBackEnd
from kdecore import KConfig, KConfigBase       
from kdecore import KSimpleConfig
from kdecore import KConfigSkeleton

class BaseSkel(ConfigParser):
    def __init__(self):
        ConfigParser.__init__(self)
        s = 'database'
        items = [
            ['dbhost', 'localhost'],
            ['dbname', 'konsultant'],
            ['dbuser', os.environ['USER']],
            ['dbpass', ''],
            ['dbport', '5432']
            ]
        self.add_section(s)
        self._additems(s, items)

        s = 'pgpool'
        items = [
            ['usepgpool', 'false'],
            ['port', '5434'],
            ['command', '/usr/sbin/pgpool'],
            ['num_init_children', '32'],
            ['max_pool', '4'],
            ['connection_life_time', '0']
            ]
        self.add_section(s)
        self._additems(s, items)
        
    def _additems(self, section, items):
        for k,v in items:
            self.set(section, k, v)
            
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
        skel = BaseSkel()
        data = skel.getdata()
        for section in skel.sections():
            self.setGroup(section)
            for opt in skel.options(section):
                if not self.hasKey(opt):
                    self.writeEntry(opt, data[section][opt])
        self.sync()

class DefaultSkeleton(KConfigSkeleton):
    def __init__(self, cfg):
        print cfg
        for group in cfg.groupList():
            #self.setCurrentGroup(group)
            for k,v in cfg.entryMap(group).items():
                print k, '-->', v
        KConfigSkeleton.__init__(self, 'konsultantrc')
