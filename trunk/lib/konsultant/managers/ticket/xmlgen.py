#from operator import and_
from xml.dom.minidom import Element, Text

from konsultant.base import NoExistError
from konsultant.sqlgen.clause import Eq, In

from konsultant.base.xmlgen import Html, Body, Anchor
from konsultant.base.xmlgen import TextElement
from konsultant.base.xmlgen import TableElement
from konsultant.base.xmlgen import BaseElement
from konsultant.db.xmlgen import BaseDocument
from konsultant.db.xmlgen import BaseParagraph

from db import TicketManager

class TicketHeader(BaseElement):
    def __init__(self):
        BaseElement.__init__(self, 'h2')
        node = Text()
        node.data = 'All Tickets'
        self.appendChild(node)
        p = BaseElement('p')
        self.new = Anchor('new.ticket.noid', 'new')
        p.appendChild(self.new)
        self.appendChild(p)

class TicketFooter(BaseElement):
    def __init__(self, ticketid):
        BaseElement.__init__(self, 'h3')
        self.respond = Anchor('new.action.none', 'respond')
        self.appendChild(self.respond)
        
class TicketTableElement(TableElement):
    def __init__(self, db=None):
        cols = ['title', 'status']
        TableElement.__init__(self, cols)

class TicketData(TextElement):
    def __init__(self, data):
        TextElement.__init__(self, 'p', data)


class ListItem(TextElement):
    def __init__(self, data):
        TextElement.__init__(self, 'li', data)

class UnorderedList(BaseElement):
    def __init__(self):
        BaseElement.__init__(self, 'ul')

class ActionItem(ListItem):
    def __init__(self, row):
        url = 'new.action.%d' % row.actionid
        element = Anchor(url, row.subject)
        ListItem.__init__(self, element)

        
class ActionThreads(UnorderedList):
    def __init__(self, parent, actions, trows, crows):
        UnorderedList.__init__(self)
        self._actiondata = {}
        for a in actions:
            self._actiondata[a.actionid] = a
        self.actions = {}
        for row in trows:
            element = UnorderedList()
            #li = ListItem('action-%d' % row.actionid)
            li = ActionItem(self._actiondata[row.actionid])
            element.appendChild(li)
            self.actions[row.actionid] = element
            self.appendChild(element)
        self.make_threads(parent, crows)
        
    def make_threads(self, parent, rows):
        print rows
        while len(rows):
            row = rows[0]
            print 'row is', row.actionid, row.parent
            element = UnorderedList()
            #element = ListItem('actionid %d' % row.actionid)
            if not row.parent:
                parent.appendChild(element)
                #element.appendChild(ListItem('actionid--%d' % row.actionid))
            elif not self.actions.has_key(row.parent):
                print row.parent, 'is not there'
                rows.append(row)
            else:
                self.actions[row.parent].appendChild(element)
                print row.actionid, 'appended to ', row.parent
                element.appendChild(ActionItem(self._actiondata[row.actionid]))
            self.actions[row.actionid] = element
            del rows[0]
            
            
    
class TicketInfoDoc(BaseDocument):
    def __init__(self, db):
        BaseDocument.__init__(self, db)
        self.manager = TicketManager(self.db)

    def set_clause(self, clause):
        self.clear_body()
        rows = self.db.select(fields=['title'], table='tickets')

    def setID(self, ticketid):
        row = self.manager.get_ticket(ticketid, data=True)
        self.current = ticketid
        self.clear_body()
        #make header
        self.header = TicketHeader()
        self.body.appendChild(self.header)
        #append ticket data
        tdata = TicketData(row.data)
        self.body.appendChild(tdata)
        #append ticket footer
        self.tfooter = TicketFooter(ticketid)
        self.body.appendChild(self.tfooter)
        actions, rows, trows, crows = self.manager.get_actions(ticketid, True)
        athreads = ActionThreads(self.body, actions, trows, crows)
        self.body.appendChild(athreads)
        
