#from operator import and_
from xml.dom.minidom import Element, Text

from paella.base import NoExistError
from paella.sqlgen.clause import Eq, In

from konsultant.base.xmlgen import Html, Body, Anchor
from konsultant.base.xmlgen import TableElement
from konsultant.base.xmlgen import BaseElement
from konsultant.db.client import ClientManager

#db is BaseDatabase from konsultant.db
class BaseDbElement(BaseElement):
    def __init__(self, db, tagname):
        BaseElement.__init__(self, tagname)
        self.db = db
        
class BaseDocument(BaseDbElement):
    def __init__(self, db):
        BaseDbElement.__init__(self, db, 'html')
        self.db = db
        self.body = Body()
        self.appendChild(self.body)

    def clear_body(self):
        while self.body.hasChildNodes():
            del self.body.childNodes[0]
        
class BaseParagraph(BaseDbElement):
    def __init__(self, db, key, href=None):
        BaseDbElement.__init__(self, db, 'p')
        data = self.makeParagraph(key)
        if href is not None:
            node = Anchor(href, data)
        else:
            node = Text()
            node.data = data
        self.appendChild(node)

    def makeParagraph(self, key):
        #all subclasses must define this member
        raise Exception, 'makeParagraph not overidden'
    
    
class AddressLink(BaseParagraph):
    def makeParagraph(self, address):
        #this is ugly and will be removed soon
        if type(address) is not dict and not hasattr(address, 'items'):
            fields = ['street1', 'street2', 'city', 'state', 'zip']
            table = 'addresses'
            clause = Eq('addressid', address)
            row = self.db.mcursor.select_row(fields=fields, table=table, clause=clause)
        else:
            row = address
        lastline = '%s, %s  %s' % (row['city'], row['state'], row['zip'])
        lines = [row['street1']]
        if row['street2']:
            lines.append(row['street2'])
        lines.append(lastline)
        return '\n'.join(lines)

class AddressSelectDoc(BaseDocument):
    def set_clause(self, clause):
        self.clear_body()
        rows = self.db.mcursor.select(fields=['addressid'],
                                              table='addresses', clause=clause)
        for row in rows:
            a = row.addressid
            self.body.appendChild(AddressLink(self.db, a, 'select.address.%d' % a))


class ClientHeaderElement(BaseElement):
    def __init__(self, client):
        BaseElement.__init__(self, 'h3')
        self.client = client
        node = Text()
        node.data = '%s:' % client
        self.appendChild(node)

class ClientSectionHeader(BaseElement):
    def __init__(self, clientid, section, text):
        BaseElement.__init__(self, 'h2')
        node = Text()
        node.data = text
        self.appendChild(node)
        p = BaseElement('p')
        self.new = Anchor('new.%s.%s' % (section, clientid), 'new')
        p.appendChild(self.new)
        self.appendChild(p)
        
class TicketHeader(BaseElement):
    def __init__(self):
        BaseElement.__init__(self, 'h2')
        node = Text()
        node.data = 'All Tickets'
        self.appendChild(node)
        p = BaseElement('p')
        self.new = Anchor('new.ticket.noid')
        p.appendChild(self.new)
        self.appendChild(p)
        
        
        
class LocationTableElement(TableElement):
    def __init__(self, db=None):
        cols = ['address', 'isp', 'connection', 'ip', 'static', 'serviced']
        TableElement.__init__(self, cols)
        
class ContactTableElement(TableElement):
    def __init__(self, db=None):
        cols = ['name', 'address', 'email', 'description']
        TableElement.__init__(self, cols)

class TicketTableElement(TableElement):
    def __init__(self, db=None):
        cols = ['title', 'status']
        TableElement.__init__(self, cols)

class TicketInfoDoc(BaseDocument):
    def __init__(self, db):
        BaseDocument.__init__(self, db)

    def set_clause(self, clause):
        self.clear_body()
        rows = self.db.select(fields=['title'], table='tickets')
        
        
class ClientInfoDoc(BaseDocument):
    def __init__(self, db):
        BaseDocument.__init__(self, db)
        self.manager = ClientManager(self.db)
        self.body.setAttribute('text', '#000000')
        self.body.setAttribute('background', 'Time-For-Lunch-2.jpg')

    def setID(self, clientid):
        cdata = self.manager.getClientInfo(clientid)
        self.current = clientid
        self.clear_body()
        #make header
        self.header = ClientHeaderElement(cdata['client'])
        self.body.appendChild(self.header)
        #append contacts header
        conheader = ClientSectionHeader(self.current, 'contact', 'Contacts:')
        self.body.appendChild(conheader)
        self.contacts = ContactTableElement()
        self.body.appendChild(self.contacts)
        #append locations header
        locheader = ClientSectionHeader(self.current, 'location', 'Locations:')
        self.body.appendChild(locheader)
        self.locations = LocationTableElement()
        self.body.appendChild(self.locations)
        #insert the contacts, locations and tickets
        self.appendLocations(cdata)
        self.appendContacts(cdata)

    def _appendRows(self, rows, element, addresses):
        for row in rows:
            row.addressid = AddressLink(self.db, addresses[row.addressid])
            element.appendRowElement(element, row)
            
    def _appendRowsOrig(self, ids, fields, table, idcol, element):
        if len(ids):
            clause = In(idcol, ids)
            for row in self.db.mcursor.select(fields=fields, table=table, clause=clause):
                row.addressid = AddressLink(self.db, row.addressid)
                element.appendRowElement(element, row)
            
    def appendLocations(self, data):
        self._appendRows(data['locations'], self.locations, data['addresses'])

    def appendContacts(self, data):
        self._appendRows(data['contacts'], self.contacts, data['addresses'])

