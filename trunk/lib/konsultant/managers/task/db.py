from konsultant.sqlgen.clause import Eq, In, NotIn


class TaskManager(object):
    def __init__(self, app):
        self.app = app
        self.db = app.db
        
    def _setup_insdata(self, fields, data):
        return dict([(f, data[f]) for f in fields])

    def create_task(self, name, description):
        fields = ['name', 'description']
        insdata = dict(name=name, description=description)
        row = self.db.identifyData('taskid', 'tasks', insdata)
        taskid = row.taskid
        self.db.conn.commit()
        return taskid
        

    def assign_clients(self, taskid, clients):
        fields = ['clientid', 'taskid']
        clause = Eq('taskid', taskid) & In('clientid', clients)
        table = 'clienttask'
        rows = self.db.select(fields=['clientid'], table=table, clause=clause)
        already = [row.clientid for row in rows]
        new = [c for c in clients if c not in already]
        data = dict(taskid=taskid)
        for clientid in new:
            data['clientid'] = clientid
            self.db.insert(table=table, data=data)
        self.db.foobar()
        return new
    
    def update_client_assignment(self, taskid, assigned):
        tdata = dict(taskid=taskid)
        self.db.delete(table='clienttask', clause=Eq('taskid', taskid))
        for clientid in assigned:
            tdata['clientid'] = clientid
            self.db.insert(table='clienttask', data=tdata)
        self.db.conn.commit()
        
    
    def get_tasks(self, clause=None):
        fields = ['taskid', 'name', 'description']
        rows = self.db.select(fields=fields, table='tasks', clause=clause)
        return rows

    def get_task(self, taskid, description=False):
        fields = ['name']
        if description:
            fields.append('description')
        return self.db.select_row(fields=fields,
                                  table='tasks', clause=Eq('taskid', taskid))


    def get_clients(self, taskid, assigned=False):
        tclause = Eq('taskid', taskid)
        cfields = ['clientid', 'client']
        sub = self.db.stmt.select(fields=['clientid'], table='clienttask',
                                  clause=tclause)
        if assigned:
            clause = In('clientid', sub)
            return self.db.select(fields=fields, table='clients', clause=clause)
        else:
            afields = cfields + ['TRUE as assigned']
            ufields = cfields + ['FALSE as assigned']
            clause = In('clientid', sub)
            fields = cfields + ['%s as assigned' % clause]
            return self.db.select(fields=fields, table='clients')
                    
    
