from paella.base.config import list_rcfiles
from paella.base.config import Configuration

class Config(Configuration):
    def __init__(self):
        files = list_rcfiles('konsultantrc')
        Configuration.__init__(self, files=files)
        
    
