
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

    def _setup_insdata(self, fields, data):
        return dict([(f, data[f]) for f in fields])

    def create_ticket(self, title, data):
        fields = ['title', 'data']
        insdata = self._setup_insdata(fields, data)
        row = self.db.identifyData('ticketid', 'tickets', insdata)
        return row.ticketid

    def append_action(self, ticketid, action, parent=None):
        fields = ['ticketid', 'action', 'time']
        insdata = self._setup_insdata(fields, data)
        row = self.db.identifyData('actionid', 'ticketactions', data)
        actionid = row.actionid
        if parent is not None:
            self.db.insert(table='ticketactionparent',
                           data=dict(actionid=actionid, parent=parent))
        self.db.conn.commit()
        return actionid

    def assign_ticket(self, ticketid, clients):
        fields = ['clientid', 'ticketid']
        clause = Eq('ticketid', ticketid) & In('clientid', clients)
        table = 'client_tickets'
        rows = self.db.select(fields=['clientid'], table=table, clause=clause)
        already = [row.clientid for row in rows]
        new = [c for c in clients if c not in already]
        data = dict(ticketid=ticketid)
        for clientid in new:
            data['clientid'] = clientid
            self.db.insert(table=table, data=data)
        self.db.commit
        return new
    

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
