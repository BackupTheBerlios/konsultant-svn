
from konsultant.base.gui import MainWindow
from konsultant.db import BaseDatabase
from konsultant.db.gui import BaseManagerWidget, ViewBrowser
from konsultant.db.xmlgen import TicketInfoDoc

TICKETSTATUS = ['open', 'closed']

class TProto(object):
    def create_ticket(self, title, data):
        return ticketid


class TicketManager(object):
    def __init__(self, db):
        self.db = db

    def create_ticket(self, title, data):
        return ticketid

    def append_action(self, ticketid, action, parent=None):
        return actionid

    def assign_ticket(self, ticketid, clients):
        pass

    def get_tickets(self, clause):
        return rows
    

class TicketView(ViewBrowser):
    def __init__(self, db, parent):
        ViewBrowser.__init__(self, db, parent, TicketInfoDoc)
        self.dialogs = {}
        


class TicketManagerWidget(BaseManagerWidget):
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
