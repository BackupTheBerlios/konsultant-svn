from paella.sqlgen.classes import Table, Sequence, ColumnType, Column
from paella.sqlgen.defaults import Pk, Text, DefaultNamed, Bool, PkNum
from paella.sqlgen.defaults import PkBigname, Bigname, Name, Num, PkName
from paella.sqlgen.defaults import DateTime
from paella.sqlgen.statement import Statement

ZipName = ColumnType('varchar', 5)
StateName = ColumnType('varchar', 2)
sequences = ['address_ident', 'contact_ident', 'ticket_ident',
             'location_ident', 'client_ident', 'action_ident']

def AutoId(name, seqname, pk=False):
    column = Num(name)
    c = column.constraint
    c.unique = True
    c.null = False
    c.pk = pk
    column.set_auto_increment(seqname)
    return column

def Now(name):
    column = DateTime(name)
    column.constraint.default_raw = True
    column.constraint.default = 'now()'
    return column

class ConfigTable(Table):
    def __init__(self):
        uname = PkName('username')
        section = PkName('section')
        option = PkBigname('option')
        value = Text('value')
        cols = [uname, section, option, value]
        Table.__init__(self, 'config', cols)
        
class AddressTable(Table):
    def __init__(self):
        idcol = AutoId('addressid', 'address_ident')
        s1 = PkBigname('street1')
        s2 = PkBigname('street2')
        s2.constraint.default = ('')
        city = PkName('city')
        state = Column('state', StateName)
        state.constraint.pk = True
        zip_ = Column('zip', ZipName)
        zip_.constraint.pk = True
        cols = [idcol, s1, s2, city, state, zip_]
        Table.__init__(self, 'addresses', cols)

class ContactTable(Table):
    def __init__(self):
        idcol = AutoId('contactid', 'contact_ident')
        name = PkName('name')
        address = Num('addressid')
        address.set_fk('addresses', 'addressid')
        email = PkBigname('email')
        desc = Text('description')
        Table.__init__(self, 'contacts', [idcol, name, address, email, desc])

class TicketTable(Table):
    def __init__(self):
        idcol = AutoId('ticketid', 'ticket_ident', pk=True)
        title = Name('title')
        title.constraint.null = False
        author = Name('author')
        created = Now('created')
        data = Text('data')
        cols = [idcol, title, author, created, data]
        Table.__init__(self, 'tickets', cols)
        
class TicketActionTable(Table):
    def __init__(self):
        ticket = Num('ticketid')
        ticket.set_fk('tickets')
        actionid = AutoId('actionid', 'action_ident', pk=True)
        subject = Bigname('subject')
        action = Text('action')
        author = Name('author')
        posted = Now('posted')
        cols = [ticket, actionid, subject, action, author, posted]
        Table.__init__(self, 'ticketactions', cols)
        
class TicketActionParentTable(Table):
    def __init__(self):
        actionid = PkNum('actionid')
        actionid.set_fk('ticketactions', 'actionid')
        parent = PkNum('parent')
        parent.set_fk('ticketactions')
        Table.__init__(self, 'ticketactionparent', [actionid, parent])
        
class TicketStatusTable(Table):
    def __init__(self):
        ticketid = PkNum('ticketid')
        ticketid.set_fk('tickets')
        status = Name('status')
        Table.__init__(self, 'ticketstatus', [ticketid, status])

class LocationTable(Table):
    def __init__(self):
        idcol = AutoId('locationid', 'location_ident')
        name = PkName('name')
        name.constraint.default = 'main office'
        addressid = PkNum('addressid')
        addressid.set_fk('addresses', 'addressid')
        isp = PkName('isp')
        conn = PkName('connection')
        ip = PkName('ip')
        static = Bool('static')
        static.constraint.pk = True
        serviced = Bool('serviced')
        serviced.constraint.pk = True
        cols = [idcol, name, addressid, isp, conn, ip, static, serviced]
        Table.__init__(self, 'locations', cols)
        
class ClientTable(Table):
    def __init__(self):
        idcol = PkNum('clientid')
        idcol.set_auto_increment('client_ident')
        client = Name('client')
        Table.__init__(self, 'clients', [idcol, client])
        
class ClientTicketTable(Table):
    def __init__(self):
        clientid = PkNum('clientid')
        clientid.set_fk('clients')
        ticketid = PkNum('ticketid')
        ticketid.set_fk('tickets')
        status = Name('status')
        Table.__init__(self, 'client_tickets', [clientid, ticketid, status])
        
class ClientInfoTable(Table):
    def __init__(self):
        clientid = Num('clientid')
        clientid.set_fk('clients')
        locationid = Num('locationid')
        locationid.set_fk('locations', 'locationid')
        contactid = Num('contactid')
        contactid.set_fk('contacts', 'contactid')
        cols = [clientid, locationid, contactid]
        Table.__init__(self, 'clientinfo', cols)
        
        
MAINTABLES = [AddressTable, ContactTable, TicketTable,
              TicketStatusTable, TicketActionTable, TicketActionParentTable,
              LocationTable, ClientTable, ClientTicketTable, ClientInfoTable
              ]

def create_schema(cursor):
    for s in sequences:
        cursor.create_sequence(Sequence(s))
    for t in MAINTABLES:
        cursor.create_table(t())

if __name__ == '__main__':
    import os
    from paella.base.config import Configuration
    from paella.db.lowlevel import BasicConnection
    from paella.db.midlevel import StatementCursor
    from konsultant.base.config import BaseConfig
    from konsultant.db import BaseDatabase
    cfg = Configuration('database', os.path.expanduser('~/.kde/share/config/konsultantrc'))
    dbname = cfg['dbname']
    dbhost = cfg['dbhost']
    dbuser = cfg['dbuser']
    conn = BasicConnection(dbuser, dbhost, dbname)
    #fg = BaseConfig()
    #b = BaseDatabase( cfg , 'schema maker')
    c = StatementCursor(conn)
    if not len(c.tables()):
        create_schema(c)
        conn.commit()

