
from konsultant.base.gui import MainWindow
from konsultant.db import BaseDatabase
from konsultant.db.gui import BaseManager, ViewBrowser
from konsultant.db.xmlgen import TicketInfoDoc

class TicketView(ViewBrowser):
    def __init__(self, db, parent):
        ViewBrowser.__init__(self, db, parent, TicketInfoDoc)
        self.dialogs = {}
        


class TicketManager(BaseManager):
    def __init__(self, parent, db, *args):
        BaseManager.__init__(self, parent, db, TicketView, 'TicketManager')
        self.db = db
        

    def initlistView(self):
        self.listView.setRootIsDecorated(True)

    def initActions(self):
        print 'fill me in'

    def initMenus(self):
        print 'fill me in'


    def selectionChanged(self):
        current = self.listView.currentItem()
        print current
