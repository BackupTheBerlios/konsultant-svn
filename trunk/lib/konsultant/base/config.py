import os

from paella.db.midlevel import Environment

from kdecore import KConfigBackEnd
from kdecore import KConfig, KConfigBase       
from kdecore import KSimpleConfig

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
        
