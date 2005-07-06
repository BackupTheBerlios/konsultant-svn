from useless.sqlgen.clause import Eq, In, NotIn
from useless.sqlgen.clause import Neq


class TroubleManager(object):
    def __init__(self, app):
        self.app = app
        self.db = app.db
        
    def _setup_insdata(self, fields, data):
        return dict([(f, data[f]) for f in fields])

    def getClientTroubles(self, clientid, done=False):
        if not done:
            clause = Eq('clientid', clientid) & Neq('status', 'done')
        else:
            clause = Eq('clientid', clientid)
        rows = self.db.select(table='troubles', clause=clause, order=['posted'])
        return rows

    def addTrouble(self, clientid, problem, worktodo):
        data = dict(clientid=clientid, problem=problem,
                    worktodo=worktodo, status='untouched')
        self.db.insert(table='troubles', data=data)
        self.db.conn.commit()

    def getTroubleStatus(self, troubleid):
        clause = Eq('troubleid', troubleid)
        row = self.db.select_row(table='troubles', clause=clause)
        return row.status
        
    def updateTrouble(self, troubleid, action, workdone, newstatus):
        instatus = self.getTroubleStatus(troubleid)
        outstatus = newstatus
        if outstatus == 'untouched':
            raise Error, 'unable to update this action without changing status'
        data = dict(troubleid=troubleid, action=action, workdone=workdone,
                    instatus=instatus, outstatus=outstatus)
        self.db.insert(table='troubleaction', data=data)
        if outstatus != instatus and instatus != 'done':
            self.db.update(table='troubles', data={'status' : outstatus},
                           clause=Eq('troubleid', troubleid))
        self.db.conn.commit()
        
    def getTroubles(self, clause=None, done=False):
        if done and clause is None:
            clause = None
        elif clause is None:
            clause = Neq('status', 'done')
        else:
            clause = clause
        rows = self.db.select(table='troubles', clause=clause, order=['posted'])
        return rows

    def getTroubleActions(self, troubleid):
        clause = Eq('troubleid', troubleid)
        rows = self.db.select(table='troubleaction', clause=clause)
        return rows

    def getTroubleInfo(self, troubleid):
        row = self.db.select_row(table='troubles', clause=Eq('troubleid', troubleid))
        info = dict(row)
        row = self.db.select_row(table='clients', clause=Eq('clientid', row.clientid))
        info['client'] = row.client
        info['actions'] = self.getTroubleActions(troubleid)
        return info

    def getStatusCounts(self):
        statustypes = [r.status for r in self.db.select(table='trouble_status')]
        field = 'count(troubleid) as number'
        counts = {}
        for status in statustypes:
            clause = Eq('status', status)
            row = self.db.select_row(fields=[field], table='troubles', clause=clause)
            counts[status] = row.number
        return counts

