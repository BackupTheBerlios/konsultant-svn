from useless.sqlgen.clause import Eq, In, NotIn
from useless.sqlgen.clause import Neq


class TroubleManager(object):
    def __init__(self, db):
        self.db = db
        
    def _setup_insdata(self, fields, data):
        return dict([(f, data[f]) for f in fields])

    def getClientTroubles(self, clientid, done=False):
        if not done:
            clause = Eq('clientid', clientid) & Neq('status', 'done')
        else:
            clause = Eq('clientid', clientid)
        rows = self.db.select(table='troubles', clause=clause, order=['posted'])
        return rows

    def addTrouble(self, clientid, problem, worktodo, magnet=None):
        data = dict(clientid=clientid, problem=problem,
                    worktodo=worktodo, status='untouched')
        troubleid = self.db.select_row(fields=["nextval('trouble_ident')"], table=None)[0]
        data['troubleid'] = troubleid
        self.db.insert(table='troubles', data=data)
        if magnet is not None:
            self.db.insert(table='trouble_magnets',
                           data=dict(troubleid=troubleid, magnet=magnet))
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
        if outstatus == 'done':
            clause = Eq('troubleid', troubleid)
            self.db.delete(table='trouble_magnets', clause=clause)
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

    def getMagnetTroubles(self):
        magtroubles_query = self.db.stmt.select(fields=['troubleid'],
                                                table='trouble_magnets')
        clause = In('troubleid', magtroubles_query)
        return self.getTroubles(clause=clause)

    def getUsedMagnets(self):
        rows = self.db.select(fields=['magnet'], table='trouble_magnets')
        return [row.magnet for row in rows]

    def getTroubleIdByMagnet(self, magnet):
        clause = Eq('magnet', magnet)
        row = self.db.select_row(table='trouble_magnets', clause=clause)
        return row.troubleid
    def getAvailableMagnets(self):
        magtroubles_query = self.db.stmt.select(fields=['magnet'],
                                                table='trouble_magnets')
        clause = NotIn('magnet', magtroubles_query)
        rows = self.db.select(table='magnets', clause=clause)
        return [row.magnet for row in rows]
    
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

