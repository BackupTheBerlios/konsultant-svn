from paella.sqlgen.statement import Statement

stmt = Statement()

addresses = [
    ['1313 Mockingbird Ln.', '', 'Sometown', 'US', '23455'],
    ['212b Baker St.', '', 'London', 'UK', '12323'],
    ['2 shelter rd', 'Chumpy Estates', 'Geeseboro', 'PU', '12345'],
    ['2a forgotten fairway', '', 'Whiffyville', 'PU', '12332']
    ]

default_desc = 'a default description'

contacts = [
    ['Nobody Special', 1, 'here@there', default_desc],
    ['Somebody Else', 1, 'where@there', default_desc],
    ['Nobody Important', 2, 'hey@there', default_desc],
    ['Bobby Generic', 2, 'bobby@world', 'in his own world.'],
    ['Don Quixote', 4, 'knight@woodland.valley', 'see the soldier with his gun...']
    ]

sp = 'SlowPipe'
bsp = 'Central Services'

locations = [
    [1, bsp, 'dsl', '1.2.3.4', True, True],
    [2, bsp, 'tincan', '2.4.5.6', True, True],
    [4, sp, 'dsl', '2.3.6.2', True, True]
    ]

clients = ['butcher', 'baker', 'candlestick maker']

clientinfo = [
    [1, 1, None, None],
    [1, None, None, 1],
    [1, None, None, 2],
    [2, 2, None, None],
    [2, None, None, 3],
    [2, None, None, 4],
    [3, 3, None, None],
    [3, None, None, 5]
    ]

address_cols = ['street1', 'street2', 'city', 'state', 'zip']
contact_cols = ['name', 'addressid', 'email', 'description']
location_cols = ['addressid', 'isp', 'connection', 'ip', 'static', 'serviced']
clientinfo_cols = ['clientid', 'locationid', 'ticketid', 'contactid']

def gen_inserts(table, cols, rows):
    statements = []
    for r in rows:
        s = stmt.insert(table=table, data=dict(zip(cols, r)))
        statements.append(s)
    return statements

def gen_all():
    statements = []
    statements += gen_inserts('clients', ['client'], [[c] for c in clients])
    statements += gen_inserts('addresses', address_cols, addresses)
    statements += gen_inserts('contacts', contact_cols, contacts)
    statements += gen_inserts('locations', location_cols, locations)
    statements += gen_inserts('clientinfo', clientinfo_cols, clientinfo)
    return statements

if __name__ == '__main__':
    import os
    from paella.base.config import Configuration
    from konsultant.db import BasicConnection
    from konsultant.db import StatementCursor
    from konsultant.db.schema import create_schema
    cfg = Configuration('database', [os.path.expanduser('~/.kde/share/config/konsultantrc')])
    dbname = cfg['dbname']
    dbhost = cfg['dbhost']
    dbuser = cfg['dbuser']
    conn = BasicConnection(dbuser, dbhost, dbname)
    sl = gen_all()
    cursor = StatementCursor(conn)
    if not len(cursor.tables()):
        create_schema(cursor)
        map(cursor.execute, sl)
        conn.commit()
    
