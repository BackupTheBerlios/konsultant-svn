from paella.sqlgen.classes import Table, Sequence, ColumnType, Column
from paella.sqlgen.defaults import Pk, Text, DefaultNamed, Bool, PkNum
from paella.sqlgen.defaults import PkBigname, Bigname, Name, Num
from paella.sqlgen.statement import Statement

ZipName = ColumnType('varchar', 5)
StateName = ColumnType('varchar', 2)
sequences = ['address_ident', 'contact_ident', 'ticket_ident',
             'location_ident', 'client_ident']

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
        idcol = PkNum('addressid')
        idcol.set_auto_increment('address_ident')
        s1 = Bigname('street1')
        s2 = Bigname('street2')
        city = Name('city')
        state = Column('state', StateName)
        zip_ = Column('zip', ZipName)
        cols = [idcol, s1, s2, city, state, zip_]
        Table.__init__(self, 'addresses', cols)

class ContactTable(Table):
    def __init__(self):
        idcol = PkNum('contactid')
        idcol.set_auto_increment('contact_ident')
        name = Name('name')
        address = Num('addressid')
        address.set_fk('addresses')
        email = Bigname('email')
        desc = Text('description')
        Table.__init__(self, 'contacts', [idcol, name, address, email, desc])

class TicketTable(Table):
    def __init__(self):
        idcol = PkNum('ticketid')
        idcol.set_auto_increment('ticket_ident')
        title = Name('title')
        data = Text('data')
        cols = [idcol, title, data]
        Table.__init__(self, 'tickets', cols)
        
class TicketActionTable(Table):
    def __init__(self):
        ticket = Num('ticketid')
        ticket.set_fk('tickets')
        actionid = PkNum('actionid')
        action = Text('action')
        cols = [ticket, actionid, action]
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
        idcol = PkNum('locationid')
        idcol.set_auto_increment('location_ident')
        addressid = Num('addressid')
        addressid.set_fk('addresses')
        isp = Name('isp')
        conn = Name('connection')
        ip = Name('ip')
        static = Bool('static')
        serviced = Bool('serviced')
        cols = [idcol, addressid, isp, conn, ip, static, serviced]
        Table.__init__(self, 'locations', cols)
        
class ClientTable(Table):
    def __init__(self):
        idcol = PkNum('clientid')
        idcol.set_auto_increment('client_ident')
        client = Name('client')
        Table.__init__(self, 'clients', [idcol, client])
        
class ClientInfoTable(Table):
    def __init__(self):
        clientid = Num('clientid')
        clientid.set_fk('clients')
        locationid = Num('locationid')
        locationid.set_fk('locations')
        ticketid = Num('ticketid')
        ticketid.set_fk('tickets')
        contactid = Num('contactid')
        contactid.set_fk('contacts')
        cols = [clientid, locationid, ticketid, contactid]
        Table.__init__(self, 'clientinfo', cols)
        
        
MAINTABLES = [AddressTable, ContactTable, TicketTable,
              TicketStatusTable, TicketActionTable, TicketActionParentTable,
              LocationTable, ClientTable, ClientInfoTable
              ]

def create_schema(cursor):
    for s in sequences:
        cursor.create_sequence(Sequence(s))
    for t in MAINTABLES:
        cursor.create_table(t())

if __name__ == '__main__':
    from paella.base.config import Configuration
    from paella.db.lowlevel import BasicConnection
    from paella.db.midlevel import StatementCursor
    import os
    rcfile = os.path.expanduser('~/.konsultantrc')
    cfg = Configuration(files=[rcfile])
    host = cfg.get('database', 'dbhost')
    user = cfg.get('database', 'dbusername')
    dbname = cfg.get('database', 'dbname')
    conn = BasicConnection(user, host, dbname, None)
    c = StatementCursor(conn)
    if not len(c.tables()):
        create_schema(c)
        conn.commit()

