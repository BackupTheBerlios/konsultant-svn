#from operator import and_
from xml.dom.minidom import Element, Text

from konsultant.base import NoExistError
from konsultant.sqlgen.clause import Eq, In

from konsultant.base.xmlgen import Html, Body, Anchor
from konsultant.base.xmlgen import HR, BR, Bold, TR, TD
from konsultant.base.xmlgen import TableElement
from konsultant.base.xmlgen import BaseElement, TextElement
from konsultant.db.xmlgen import BaseDocument
from konsultant.db.xmlgen import AddressLink
from konsultant.db.xmlgen import RecordElement, RecordDoc
from db import ClientManager


class SimpleTitleElement(BaseElement):
    def __init__(self, title, **attributes):
        BaseElement.__init__(self, 'table')
        self._title = title
        for k,v in attributes.items():
            self.setAttribute(k, v)
        self.row = TR()
        td = TD()
        self.appendChild(self.row)
        self.row.appendChild(td)
        self._font = BaseElement('font')
        self._font.setAttribute('color', 'gold')
        td.appendChild(self._font)
        element = TextElement('h1', self._title)
        self._font.appendChild(element)

    def set_font(self, **attributes):
        for k,v in attributes.items():
            self._font.setAttribute(k, v)

    def set_title(self, title):
        self._title = title
        print 'i don nothing'
        

###########
##Contact Objects
###########

class ContactTitle(SimpleTitleElement):
    def __init__(self, **attributes):
        SimpleTitleElement.__init__(self, 'Contacts', **attributes)
        self.set_font(color='plum')

class ContactElement(RecordElement):
    def __init__(self, row, action):
        fields = ['name', 'email', 'description']
        RecordElement.__init__(self, fields, 'contactid', action, row)
        
class ContactDoc(RecordDoc):
    def __init__(self, app):
        RecordDoc.__init__(self, app, ClientManager)
        
    def set_ident(self, clientid, action='edit'):
        self.clientid = clientid
        self.clear_body()
        self.body.appendChild(ContactTitle(bgcolor='DarkSeaGreen4'))
        self.body.appendChild(HR())
        rows, ignore = self.manager.getContacts(self.clientid, False)
        for row in rows:
            element = ContactElement(row, action)
            self.body.appendChild(element)
            self.body.appendChild(HR())
            self.records[row.contactid] = element
            
##########
# Location Objects
##########


class LocationTitle(SimpleTitleElement):
    def __init__(self, **attributes):
        SimpleTitleElement.__init__(self, 'Locations', **attributes)
        self.set_font(color='plum')

class LocationElement(RecordElement):
    def __init__(self, row, action):
        fields = ['name', 'isp', 'connection', 'ip', 'static', 'serviced']
        RecordElement.__init__(self, fields, 'locationid', action, row)
        
class LocationDoc(RecordDoc):
    def __init__(self, app):
        RecordDoc.__init__(self, app, ClientManager)
        
    def set_ident(self, clientid, action='edit'):
        self.clientid = clientid
        self.clear_body()
        self.body.appendChild(LocationTitle(bgcolor='DarkSeaGreen4'))
        self.body.appendChild(HR())
        rows, ignore = self.manager.getLocations(self.clientid, False)
        for row in rows:
            element = LocationElement(row, action)
            self.body.appendChild(element)
            self.body.appendChild(HR())
            self.records[row.locationid] = element

#########
#Client Objects
#########

class ClientTitleElement(SimpleTitleElement):
    def __init__(self, title):
        atts = dict(border='0', cellpadding='5', bgcolor='cornsilk4',
                    width='100%')
        SimpleTitleElement.__init__(self, title, **atts)
        td = self.row.firstChild.firstChild
        td.appendChild(Anchor('edit.client.%s' % title, 'edit'))
        self.set_font(color='gold')
        
        #self.row.setAttributes(bgcolor='cornsilk4')
class ClientHeaderElement(BaseElement):
    def __init__(self, client):
        BaseElement.__init__(self, 'head')
        self.client = client
        node = TextElement('h1', client)
        self.appendChild(node)
        self.appendChild(BaseElement('hr'))

class ClientSectionHeader(BaseElement):
    def __init__(self, clientid, section, text):
        BaseElement.__init__(self, 'h4')
        node = Text()
        node.data = text
        self.appendChild(node)
        p = BaseElement('p')
        self.new = Anchor('new.%s.%s' % (section, clientid), 'new')
        self.edit = Anchor('edit.%s.%s' % (section, clientid), 'edit')
        p.appendChild(self.new)
        p.appendChild(BaseElement('br'))
        p.appendChild(self.edit)
        self.appendChild(p)
        
class LocationTableElement(TableElement):
    def __init__(self, db=None):
        cols = ['name', 'address', 'isp', 'connection', 'ip', 'static', 'serviced']
        TableElement.__init__(self, cols)
        row = self.firstChild
        row.setAttribute('bgcolor', 'DarkSeaGreen')
        
class ContactTableElement(TableElement):
    def __init__(self, db=None):
        cols = ['name', 'address', 'email', 'description']
        TableElement.__init__(self, cols)
        self.setAttribute('border', '0')
        row = self.firstChild
        row.setAttribute('bgcolor', 'cornsilk')
        
class ClientInfoDoc(BaseDocument):
    def __init__(self, app):
        BaseDocument.__init__(self, app)
        self.manager = ClientManager(self.app)
        self.body.setAttribute('text', '#000000')
        self.body.setAttribute('background', 'Time-For-Lunch-2.jpg')

    def setID(self, clientid):
        cdata = self.manager.getClientInfo(clientid)
        self.current = clientid
        self.clear_body()
        #make header
        #self.header = ClientHeaderElement(cdata['client'])
        self.header = ClientTitleElement(cdata['client'])
        self.body.appendChild(self.header)
        #make main table
        self.mtable = BaseElement('table')
        self.mtable.appendChild(BaseElement('tr'))
        self.body.appendChild(self.mtable)
        #append contacts header
        conheader = ClientSectionHeader(self.current, 'contact', 'Contacts:')
        self.mtable.firstChild.appendChild(TextElement('td', conheader))
        self.contacts = ContactDoc(self.app)
        self.mtable.firstChild.appendChild(TextElement('td', self.contacts))
        #append locations header
        row = BaseElement('tr')
        locheader = ClientSectionHeader(self.current, 'location', 'Locations:')
        row.appendChild(TextElement('td', locheader))
        self.locations = LocationDoc(self.app)
        self.mtable.appendChild(row)
        row.appendChild(TextElement('td', self.locations))
        #insert the contacts, locations and tickets
        self.contacts.set_ident(clientid, action=None)
        self.locations.set_ident(clientid, action=None)
        for node in self.contacts.records.values():
            node.setAttribute('bgcolor', 'DarkSeaGreen3')
        for node in self.locations.records.values():
            node.setAttribute('bgcolor', 'DarkSeaGreen3')

