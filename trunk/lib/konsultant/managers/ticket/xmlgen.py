#from operator import and_
from xml.dom.minidom import Element, Text

from paella.base import NoExistError
from paella.sqlgen.clause import Eq, In

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
        
class TicketTableElement(TableElement):
    def __init__(self, db=None):
        cols = ['title', 'status']
        TableElement.__init__(self, cols)

class TicketData(TextElement):
    def __init__(self, data):
        TextElement.__init__(self, 'p', data)

        
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
