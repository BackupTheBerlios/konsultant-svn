from useless.sqlgen.clause import Eq, In, NotIn


class TicketManager(object):
    def __init__(self, app):
        self.app = app
        self.db = app.db
        self.atable = 'ticketactions'
        self.aptable = 'ticketactionparent'
        self.apfields = ['actionid', 'parent'] 
        self.afields = ['actionid', 'subject', 'action', 'author', 'posted']
        
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
        

    def append_action(self, ticketid, subject, action, data, parent=None):
        insdata = dict(ticketid=ticketid, subject=subject, action=action,
                       data=data)
        insdata['author'] = self.db.dbuser
        actionid = self.db.select_row(fields=["nextval('action_ident')"]).nextval
        insdata['actionid'] = actionid
        self.db.insert(table='ticketactions', data=insdata)
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
        self.db.foobar()
        return new
    
    def update_ticket_assignment(self, ticketid, assigned):
        tdata = dict(ticketid=ticketid)
        self.db.delete(table='client_tickets', clause=Eq('ticketid', ticketid))
        for clientid in assigned:
            tdata['clientid'] = clientid
            self.db.insert(table='client_tickets', data=tdata)
        self.db.conn.commit()
        
    
    def get_tickets(self, clause=None):
        fields = ['ticketid', 'title', 'author', 'created']
        print clause, type(clause)
        if clause is None:
            tquery = self.db.stmt.select(fields=['ticketid'], table='ticketstatus',
                                         clause=In('status', ['new', 'open']))
            clause = 'ticketid IN (%s)' % tquery
        rows = self.db.select(fields=fields, table='tickets', clause=clause,
                              order='created')
        return rows

    def get_ticket(self, ticketid, data=False):
        fields = ['title', 'author', 'created']
        if data:
            fields.append('data')
        return self.db.select_row(fields=fields,
                                  table='tickets', clause=Eq('ticketid', ticketid))

    def get_actionids(self, ticketid):
        #this should be placed on the server
        fields = ['actionid']
        bclause = Eq('ticketid', ticketid)
        parentquery = 'select actionid from ticketactionparent'
        allquery = self.db.stmt.select(fields=fields, table='ticketactions', clause=bclause)
        allrows = self.db.select(fields=fields, table='ticketactions', clause=bclause)
        tclause = bclause & NotIn('actionid', parentquery)
        cclause = In('actionid', allquery)
        toprows = self.db.select(fields=fields, table='ticketactions', clause=tclause)
        fields.append('parent')
        table = 'ticketactionparent'
        childrows = self.db.select(fields=fields, table=table, clause=cclause)
        return allrows, toprows, childrows
    
    def get_actions(self, ticketid, actionids=False):
        allrows, toprows, childrows = self.get_actionids(ticketid)
        clause = Eq('ticketid', ticketid)
        actions = self.db.select(fields=self.afields, table=self.atable, clause=clause)
        if not actionids:
            return actions
        else:
            return actions, allrows, toprows, childrows

    def _get_childrows(self, rows):
        clause = In('parent', [r.actionid for r in rows])
        return self.db.select(fields=self.apfields, table=self.aptable, clause=clause)
        
    def get_actiondata(self, ticketid, actionid):
        clause = Eq('ticketid', ticketid) & Eq('actionid', actionid)
        table = 'ticketactions'
        fields = ['data']
        row = self.db.select_row(fields=fields, table=table, clause=clause)
        return row.data

    def get_clients(self, ticketid, assigned=False):
        tclause = Eq('ticketid', ticketid)
        cfields = ['clientid', 'client']
        sub = self.db.stmt.select(fields=['clientid'], table='client_tickets',
                                  clause=tclause)
        if assigned:
            clause = In('clientid', sub)
            return self.db.select(fields=fields, table='clients', clause=clause)
        else:
            clause = In('clientid', sub)
            fields = cfields + ['%s as assigned' % clause]
            return self.db.select(fields=fields, table='clients')

