from kdecore import KConfig        

class BaseConfig(KConfig):
    def __init__(self):
        KConfig.__init__(self, 'konsultantrc')
        self.setCurrentGroup('database')
        
