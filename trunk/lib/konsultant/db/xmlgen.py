#from operator import and_
from xml.dom.minidom import Element, Text

from konsultant.base import NoExistError
from konsultant.sqlgen.clause import Eq, In

from konsultant.base.xmlgen import Html, Body, Anchor
from konsultant.base.xmlgen import TableElement
from konsultant.base.xmlgen import BaseElement


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

