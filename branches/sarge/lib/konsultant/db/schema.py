from useless.sqlgen.classes import Table, Sequence, ColumnType, Column
from useless.sqlgen.defaults import Pk, Text, DefaultNamed, Bool, PkNum
from useless.sqlgen.defaults import PkBigname, Bigname, Name, Num, PkName
from useless.sqlgen.defaults import DateTime
from useless.sqlgen.statement import Statement
from useless.sqlgen.admin import grant_public, grant_group


ZipName = ColumnType('varchar', 5)
StateName = ColumnType('varchar', 2)
sequences = ['address_ident', 'contact_ident', 'ticket_ident',
             'location_ident', 'client_ident', 'action_ident', 'task_ident',
             'trouble_ident', 'troubleaction_ident']

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

class TagNameTable(Table):
    def __init__(self):
        tag = PkName('tag')
        Table.__init__(self, 'tagnames', [tag])
        
class BasicTagTable(Table):
    def __init__(self, idcol, idtable, name):
        id_ = PkNum(idcol)
        id_.set_fk(idtable)
        tagname = PkName('tag')
        tagname.set_fk('tagnames')
        tagval = Text('value')
        cols = [id_, tagname, tagval]
        Table.__init__(self, name, cols)
        
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
        atype = Name('addresstype')
        atype.constraint.default = 'office'
        cols = [idcol, s1, s2, city, state, zip_, atype]
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
        action = Name('action')
        author = Name('author')
        posted = Now('posted')
        data = Text('data')
        cols = [ticket, actionid, subject, action, author, posted, data]
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

class TicketTagTable(BasicTagTable):
    def __init__(self):
        BasicTagTable.__init__(self, 'ticketid', 'tickets', 'ticket_tags')
        
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
        client.constraint.unique = True
        Table.__init__(self, 'clients', [idcol, client])
        
class ClientTicketTable(Table):
    def __init__(self):
        clientid = PkNum('clientid')
        clientid.set_fk('clients')
        ticketid = PkNum('ticketid')
        ticketid.set_fk('tickets')
        status = Name('status')
        Table.__init__(self, 'client_tickets', [clientid, ticketid, status])

class ClientTagTable(BasicTagTable):
    def __init__(self):
        BasicTagTable.__init__(self, 'clientid', 'clients', 'client_tags')

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
        
class ClientDataTable(Table):
    def __init__(self):
        clientid = PkNum('clientid')
        clientid.set_fk('clients')
        name = PkName('name')
        value = Text('value')
        cols = [clientid, name, value]
        Table.__init__(self, 'clientdata', cols)

class TaskTable(Table):
    def __init__(self):
        taskid = PkNum('taskid')
        taskid.set_auto_increment('task_ident')
        name = Name('name')
        desc = Text('description')
        cols = [taskid, name, desc]
        Table.__init__(self, 'tasks', cols)

class ClientTaskTable(Table):
    def __init__(self):
        taskid = PkNum('taskid')
        taskid.set_fk('tasks')
        clientid = PkNum('clientid')
        clientid.set_fk('clients')
        Table.__init__(self, 'clienttask', [taskid, clientid])

class LocationTaskTable(Table):
    def __init__(self):
        taskid = PkNum('taskid')
        taskid.set_fk('tasks')
        locationid = PkNum('locationid')
        locationid.set_fk('locations', 'locationid')
        Table.__init__(self, 'locationtask', [taskid, locationid])

class TroubleStatusTable(Table):
    def __init__(self):
        status = PkName('status')
        Table.__init__(self, 'trouble_status', [status])
        

class TroubleTable(Table):
    def __init__(self):
        troubleid = AutoId('troubleid', 'trouble_ident', pk=True)
        clientid = Num('clientid')
        clientid.set_fk('clients')
        problem = Name('problem')
        worktodo= Text('worktodo')
        posted = Now('posted')
        status = Name('status')
        status.set_fk('trouble_status')
        cols = [troubleid, clientid, problem, worktodo, posted, status]
        Table.__init__(self, 'troubles', cols)

class TroubleActionTable(Table):
    def __init__(self):
        troubleid = PkNum('troubleid')
        troubleid.set_fk('troubles')
        actionid = AutoId('actionid', 'troubleaction_ident', pk=True)
        instatus = Name('instatus')
        outstatus = Name('outstatus')
        action = Name('action')
        workdone = Text('workdone')
        posted = Now('posted')
        cols = [troubleid, actionid, instatus, outstatus, action, workdone, posted]
        Table.__init__(self, 'troubleaction', cols)

class MagnetTable(Table):
    def __init__(self):
        magnet = PkName('magnet')
        Table.__init__(self, 'magnets', [magnet])

class MagnetTroubleTable(Table):
    def __init__(self):
        magnet = PkName('magnet')
        magnet.set_fk('magnets')
        troubleid = Num('troubleid')
        troubleid.set_fk('troubles')
        Table.__init__(self, 'trouble_magnets', [magnet, troubleid])


        
    
        
MAINTABLES = [AddressTable, ContactTable, TicketTable,
              TicketStatusTable, TicketActionTable, TicketActionParentTable,
              LocationTable, ClientTable, ClientTicketTable, ClientInfoTable,
              ClientDataTable, TaskTable, ClientTaskTable, LocationTaskTable,
              TagNameTable, TicketTagTable, ClientTagTable, TroubleStatusTable,
              TroubleTable, TroubleActionTable, MagnetTable, MagnetTroubleTable
              ]

TR_STATUS = ['untouched', 'diagnosed', 'in_repair', 'waiting_for_parts',
             'ready_for_pickup', 'done']

def create_schema(cursor, group):
    newseqs = [s for s in sequences if  s not in cursor.sequences()]
    for s in newseqs:
        cursor.create_sequence(Sequence(s))
    for t in MAINTABLES:
        cursor.create_table(t())

    tables = [t().name for t in MAINTABLES]
    full = [ClientInfoTable, ClientTicketTable, ClientTaskTable, LocationTaskTable,
            MagnetTroubleTable]
    insup = [AddressTable, ContactTable, TicketStatusTable, 
             LocationTable, ClientTable, TaskTable,
             ClientTagTable, TicketTagTable, TroubleTable]
    ins = [TicketTable, TicketActionTable, TicketActionParentTable, TagNameTable,
           TroubleActionTable, MagnetTable]
    
    execute = cursor.execute
    execute(grant_public(tables))
    execute(grant_group('ALL', sequences, group))
    execute(grant_group('ALL', [t().name for t in full], group))
    execute(grant_group('INSERT', [t().name for t in ins + insup], group))
    execute(grant_group('UPDATE', [t().name for t in insup], group))
    for status in TR_STATUS:
        cursor.insert(table='trouble_status', data=dict(status=status))
        
    
    
    
if __name__ == '__main__':
    import os
    from useless.db.lowlevel import BasicConnection
    from useless.db.midlevel import StatementCursor
    from useless.base.config import Configuration
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
        create_schema(c, 'konsultant')
        conn.commit()

