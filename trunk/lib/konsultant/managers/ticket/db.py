from paella.sqlgen.clause import Eq, In


class TicketManager(object):
    def __init__(self, db):
        self.db = db

    def _setup_insdata(self, fields, data):
        return dict([(f, data[f]) for f in fields])

    def create_ticket(self, title, data):
        fields = ['title', 'data']
        insdata = dict(title=title, data=data, author=self.db.dbuser)
        row = self.db.identifyData('ticketid', 'tickets', insdata)
        ticketid = row.ticketid
        status = dict(ticketid=ticketid, status='new')
        self.db.insert(table='ticketstatus', data=status)
        self.db.conn.commit()
        return ticketid
        

    def append_action(self, ticketid, action, parent=None):
        fields = ['ticketid', 'action', 'posted']
        insdata = self._setup_insdata(fields, data)
        insdata['author'] = self.db.dbuser
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
    

    def get_tickets(self, clause=None):
        fields = ['ticketid', 'title', 'author', 'created']
        if clause is None:
            tquery = self.db.stmt.select(fields=['ticketid'], table='ticketstatus',
                                         clause=In('status', ['new', 'open']), order='created')
            clause = 'ticketid IN (%s)' % tquery
        rows = self.db.select(fields=fields, table='tickets', clause=clause)
        return rows

    def get_ticket(self, ticketid, data=False):
        fields = ['title', 'author', 'created']
        if data:
            fields.append('data')
        return self.db.select_row(fields=fields, table='tickets', clause=Eq('ticketid', ticketid))
    
