
from konsultant.base.gui import MainWindow
from konsultant.db import BaseDatabase
from konsultant.db.gui import BaseManager

class TicketView(KTextBrowser):
    pass


class TicketManager(BaseManager):
    def __init__(self, parent, db, *args):
        BaseManager.__init__(self, parent, db, TicketView, 'TicketManager')
        self.db = db
        
