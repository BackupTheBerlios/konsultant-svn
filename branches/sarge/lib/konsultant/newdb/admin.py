from useless.db.midlevel import StatementCursor
from useless.sqlgen.clause import Eq, In
from useless.sqlgen.admin import create_user, create_schema

from konsultant.db import schema as kschema

class AdminDb(object):
    def __init__(self, app):
        object.__init__(self)
        self.app = app
        self.db = app.db

    def create_user(self, name, passwd=None, createdb=False,
                    createuser=False, groups=None):
        stmt = create_user(name, passwd=passwd, createdb=createdb,
                          createuser=createuser, groups=groups)
        self.db.mcursor.execute(stmt)

    def create_group(self, name):
        stmt = 'create group %s' % name
        self.db.mcursor.execute(stmt)

    def get_users(self, group=None):
        clause = None
        if group is not None:
            clause = Eq('groname', group)
            row = self.db.select_row(fields=['grolist'], table='pg_group',
                                     clause=clause)
            clause = In('usesysid', row.grolist)
        fields = ['usename', 'usesysid']
        return self.db.select(fields=fields, table='pg_user',
                              clause=clause)
    
    def get_groups(self):
        fields = ['groname as group', 'grosysid']
        return self.db.select(fields=fields, table='pg_group')
    
    def _altergroup(self, users, group, alter):
        u = ','.join(users)
        cmd = 'alter group %s %s user %s' % (group, u, alter)
        self.db.mcursor.execute(cmd)
        
    def adduser(self, users, group):
        self._altergroup(users, group, 'add')
        
    def deluser(self, users, group=None):
        if group is not None:
            self._altergroup(users, group, 'drop')
        else:
            cmd = 'drop user %s' % users[0]
            self.db.mcursor.execute(cmd)
            
    def create_schema(self, name):
        cmd = create_schema(name)
        self.db.mcursor.execute(cmd)
        self.db.conn.commit()
        
