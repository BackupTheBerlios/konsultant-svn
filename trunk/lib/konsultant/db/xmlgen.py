#from operator import and_
from xml.dom.minidom import Element, Text

from paella.base import NoExistError
from paella.sqlgen.clause import Eq, In

from konsultant.base.xmlgen import Html, Body, Anchor
from konsultant.base.xmlgen import TableElement
from konsultant.base.xmlgen import BaseElement

#db is BaseDatabase from konsultant.db
class BaseDbElement(BaseElement):
    def __init__(self, db, tagname):
        Element.__init__(self, tagname)
        self.db = db
        
class BaseDocument(BaseDbElement):
    def __init__(self, db):
        BaseDbElement.__init__(self, db, 'html')
        self.db = db
        self.body = Body()
        self.appendChild(self.body)
        
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
    def makeParagraph(self, addressid):
        fields = ['street1', 'street2', 'city', 'state', 'zip']
        table = 'addresses'
        clause = Eq('addressid', addressid)
        row = self.db.mcursor.select_row(fields=fields, table=table, clause=clause)
        lastline = '%s, %s  %s' % (row.city, row.state, row.zip)
        lines = [row.street1]
        if row.street2:
            lines.append(row.street2)
        lines.append(lastline)
        return '\n'.join(lines)

class AddressSelectDoc(BaseDocument):
    def set_clause(self, clause):
        while self.body.hasChildNodes():
            del self.body.childNodes[0]
        rows = self.db.mcursor.select(fields=['addressid'],
                                              table='addresses', clause=clause)
        for row in rows:
            a = row.addressid
            self.body.appendChild(AddressLink(self.db, a, 'select.address.%d' % a))


class ClientHeaderElement(BaseElement):
    def __init__(self, client):
        Element.__init__(self, 'h3')
        self.client = client
        #anchor = Anchor('foo.bar.-1', client)
        node = Text()
        node.data = '%s:' % client
        self.appendChild(node)

class LocationTableElement(TableElement):
    def __init__(self, db=None):
        cols = ['address', 'isp', 'connection', 'ip', 'static', 'serviced']
        TableElement.__init__(self, cols)
        
class ContactTableElement(TableElement):
    def __init__(self, db=None):
        cols = ['name', 'address', 'email', 'description']
        TableElement.__init__(self, cols)

class ClientInfoDoc(BaseDocument):
    def __init__(self, db):
        BaseDocument.__init__(self, db)
        self.body.setAttribute('text', '#000000')
        #self.body.setAttribute('background', 'vegetative_fog.jpg')
        self.body.setAttribute('background', 'Time-For-Lunch-2.jpg')

    def set_client(self, clientid):
        while self.body.hasChildNodes():
            del self.body.childNodes[0]
        clause = Eq('clientid', clientid)
        inforows = self.db.select(table='clientinfo', clause=clause)
        self.current = clientid

        #make header
        row = self.db.select_row(table='clients', clause=clause)
        self.header = ClientHeaderElement(row.client)
        self.body.appendChild(self.header)

        #append contacts header
        conheader = Element('h2')
        conheader.appendChild(Anchor('new.contact.%d' % clientid, 'Contacts:'))
        self.body.appendChild(conheader)
        self.contacts = ContactTableElement()
        self.body.appendChild(self.contacts)

        #append locations header
        locheader = Element('h2')
        locheader.appendChild(Anchor('new.location.%d' % clientid, 'Locations:'))
        self.body.appendChild(locheader)
        self.locations = LocationTableElement()
        self.body.appendChild(self.locations)

        #insert the contacts and locations
        locs = [r.locationid for r in inforows if r.locationid]
        contacts = [r.contactid for r in inforows if r.contactid]
        self.appendLocations(locs)
        self.appendContacts(contacts)
        
    def _appendRows(self, ids, fields, table, idcol, element):
        if len(ids):
            clause = In(idcol, ids)
            for row in self.db.mcursor.select(fields=fields, table=table, clause=clause):
                row.addressid = AddressLink(self.db, row.addressid)
                element.appendRowElement(element, row)
            
    def appendLocations(self, locations):
        if len(locations):
            fields = ['addressid', 'isp', 'connection', 'ip', 'static', 'serviced']
            table = 'locations'
            element = self.locations
            self._appendRows(locations, fields, table, 'locationid', element)

    def appendContacts(self, contacts):
        if len(contacts):
            fields = ['name', 'addressid', 'email', 'description']
            table = 'contacts'
            element = self.contacts
            self._appendRows(contacts, fields, table, 'contactid', element)
        
