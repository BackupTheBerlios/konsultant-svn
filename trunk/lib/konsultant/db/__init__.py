from operator import and_

from qtsql import QSqlDatabase, QSqlDriver

from paella.base import NoExistError
from paella.sqlgen.clause import Eq, In
from paella.sqlgen.statement import Statement
from paella.db.lowlevel import BasicConnection
from paella.db.midlevel import StatementCursor

from konsultant.base import Config

class BaseDriver(QSqlDriver):
    def __init__(self, parent=None, name=None):
        self.stmt = Statement()
        QSqlDriver.__init__(self, parent=parent, name=name)


class BaseDatabase(QSqlDatabase):
    def __init__(self, name, parent=None, objname=None):
        self.cfg = Config()
        self.cfg.change('database')
        QSqlDatabase.__init__(self, 'QPSQL7', name, parent, objname)
        dbname = self.cfg['dbname']
        dbhost = self.cfg['dbhost']
        dbuser = self.cfg['dbusername']
        self.conn = BasicConnection(dbuser, dbhost, dbname)
        self.setDatabaseName(dbname)
        self.setHostName(dbhost)
        self.setUserName(dbuser)
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

    def qdelete(self, table=None, clause=None):
        query = self.stmt.delete(table=table, clause=clause)
        return self.execStatement(query)

    def qinsert(self, table=None, data=None):
        query = self.stmt.insert(table=table, data=data)
        return self.execStatement(query)

    def qupdate(self, table=None, data=None, clause=None):
        query = self.stmt.update(table=table, data=data, clause=clause)
        return self.execStatement(query)

    def qselect(self, fields=None, table=None, clause=None,
               group=None, having=None, order=None):
        query = self.stmt.select(fields=fields, table=table, clause=clause,
                                 group=group, having=having, order=order)
        return self.execStatement(query)

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

    def identifyData(self, idcol, table, data):
        clause = self.stdclause(data)
        try:
            self.mcursor.select_row(fields=[idcol], table=table, clause=clause)
        except NoExistError:
            self.mcursor.insert(table=table, data=data)
            self.conn.commit()
        return self.mcursor.select_row(fields=['*'], table=table, clause=clause)
        
