import os
from operator import and_

from useless.kbase import NoExistError
from useless.sqlgen.clause import Eq, In
from useless.sqlgen.statement import Statement
from useless.db.lowlevel import BasicConnection
from useless.db.midlevel import StatementCursor


class KonsultantConnection(BasicConnection):
    def __init__(self):
        dsn = dict(user='umeboshi', host='bard', dbname='konsultant')
        BasicConnection.__init__(self, **dsn)
        

# this class will eventually disappear        
class BaseDatabase(object):
    def __init__(self, conn=None):
        if conn is None:
            self.conn = KonsultantConnection()
        else:
            self.conn = conn
        self.stmt = Statement()
        self.mcursor = StatementCursor(self.conn)
        
    def set_table(self, table):
        self.stmt.table = table

    def set_clause(self, items, cmp='=', join='and'):
        self.stmt.set_clause(items, cmp=cmp, join=join)

    def set_data(self, data):
        self.stmt.set(data)

    def set_fields(self, fields):
        self.stmt.fields = fields

    def delete(self, table=None, clause=None):
        query = self.stmt.delete(table=table, clause=clause)
        return self.mcursor.execute(query)

    def insert(self, table=None, data=None):
        query = self.stmt.insert(table=table, data=data)
        return self.mcursor.execute(query)

    def update(self, table=None, data=None, clause=None):
        query = self.stmt.update(table=table, data=data, clause=clause)
        return self.mcursor.execute(query)

    def select(self, fields=None, table=None, clause=None,
               group=None, having=None, order=None):
        query = self.stmt.select(fields=fields, table=table, clause=clause,
                                 group=group, having=having, order=order)
        self.mcursor.execute(query)
        return self.mcursor.fetchall()

    def select_row(self, fields=None, table=None, clause=None,
               group=None, having=None, order=None):
        query = self.stmt.select(fields=fields, table=table, clause=clause,
                                 group=group, having=having, order=order)
        self.mcursor.execute(query)
        rows = len(self.mcursor)
        if rows == 1:
            return self.mcursor.next()
        elif rows == 0:
            raise NoExistError
        else:
            raise Error, 'bad row count %s' % rows

    def clear(self, **args):
        self.stmt.clear(**args)

    def stdclause(self, data):
        return reduce(and_, [Eq(k, v) for k,v in data.items()])

    def insertData(self, idcol, table, data, commit=True):
        clause = self.stdclause(data)
        try:
            self.mcursor.select_row(fields=[idcol], table=table, clause=clause)
        except NoExistError:
            self.mcursor.insert(table=table, data=data)
            if commit:
                self.conn.commit()
            
    def identifyData(self, idcol, table, data, commit=True):
        clause = self.stdclause(data)
        self.insertData(idcol, table, data, commit=commit)
        return self.mcursor.select_row(fields=['*'], table=table, clause=clause)
        
