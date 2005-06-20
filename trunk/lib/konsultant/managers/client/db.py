from useless.kbase.refdata import RefData
from useless.db.record import RefRecord
from useless.sqlgen.clause import Eq, In

class ClientManager(object):
    def __init__(self, app):
        self.app = app
        self.db = app.db
        self.addressfields = ['street1', 'street2', 'city', 'state', 'zip']

    def _setup_insdata(self, fields, clientid, addressid, data):
        insdata = dict([(f, data[f]) for f in fields])
        insdata['addressid'] = addressid
        return insdata
    
    def _update_clientinfo(self, clientid, data):
        table = 'clientinfo'
        data['clientid'] = clientid
        return self.db.identifyData('*', table, data)

    def _check_address(self, data):
        addressfields = ['street1', 'street2', 'city', 'state', 'zip']
        a_data = dict([(f, data[f]) for f in addressfields])
        table = 'addresses'
        row = self.db.identifyData('addressid', table, a_data)
        return row.addressid

    
    def insertContact(self, clientid, addressid, data):
        fields = ['name', 'email', 'description']
        insdata = self._setup_insdata(fields, clientid, addressid, data)
        row = self.db.identifyData('contactid', 'contacts', insdata)
        contactid = row.contactid
        cldata = {'contactid' : contactid}
        row = self._update_clientinfo(clientid, cldata)
        return contactid

    def updateContact(self, contactid, data):
        table = 'contacts'
        clause = Eq('contactid', contactid)
        self.db.update(table=table, data=data, clause=clause)
        self.db.conn.commit()
        
    def insertLocation(self, clientid, addressid, data):
        fields = ['name', 'isp', 'connection', 'ip', 'static', 'serviced']
        insdata = self._setup_insdata(fields, clientid, addressid, data)
        row = self.db.identifyData('locationid', 'locations', insdata)
        locationid = row.locationid
        cldata = {'locationid' : locationid}
        row = self._update_clientinfo(clientid, cldata)
        return locationid

    def updateLocation(self, locationid, data):
        table = 'locations'
        clause = Eq('locationid', locationid)
        self.db.update(table=table, data=data, clause=clause)
        self.db.conn.commit()
        
    def getClientInfoIds(self, clientid):
        clause = Eq('clientid', clientid)
        client = self.db.select_row(fields=['client'], table='clients', clause=clause).client
        inforows = self.db.select(table='clientinfo', clause=clause)
        contacts = [r.contactid for r in inforows if r.contactid]
        locations = [r.locationid for r in inforows if r.locationid]
        return client, contacts, locations

    def getAddresses(self, clause):
        rows = self.db.select(fields=['addressid'] + self.addressfields,
                              table='addresses', clause=clause)
        return dict([(row.addressid, row) for row in rows])
    
    def getLocations(self, clientid, addresses=True):
        fields = ['locationid', 'name', 'addressid', 'isp', 'connection', 'ip', 'static', 'serviced']
        sclause = Eq('clientid', clientid)
        clause = 'locationid IN (select locationid from clientinfo where %s)' % sclause
        if addresses:
            aclause = 'addressid IN (%s)' % self.db.stmt.select(fields=['addressid'],
                                                                table='locations', clause=clause)
            addresses = self.getAddresses(aclause)
        locations = self.db.select(fields=fields, table='locations', clause=clause)
        return locations, addresses

    def getContacts(self, clientid, addresses=True):
        fields = ['contactid', 'name', 'addressid', 'email', 'description']
        sclause = Eq('clientid', clientid)
        clause = 'contactid IN (select contactid from clientinfo where %s)' % sclause
        if addresses:
            aclause = 'addressid IN (%s)' % self.db.stmt.select(fields=['addressid'],
                                                                table='contacts', clause=clause)
            addresses = self.getAddresses(aclause)
        contacts = self.db.select(fields=fields, table='contacts', clause=clause)
        return contacts, addresses

    def _preparequeries(self, clientid, idcol, fields, table):
        clientclause = Eq('clientid', clientid)
        stmt = self.db.stmt.select(fields=[idcol], table='clientinfo', clause=clientclause)
        clause = In(idcol, stmt)
        query = self.db.stmt.select(fields=['addressid'], table=table, clause=clause)
        return query, clause
    
    def getClientInfo(self, clientid):
        clause = Eq('clientid', clientid)
        client = self.db.select_row(fields=['client'], table='clients', clause=clause).client
        cfields = ['name', 'addressid', 'email', 'description']
        lfields = ['addressid', 'isp', 'connection', 'ip', 'static', 'serviced']
        lquery, lclause = self._preparequeries(clientid, 'locationid', lfields, 'locations')
        cquery, cclause = self._preparequeries(clientid, 'contactid', cfields, 'contacts')
        aclause = ' or '.join(['addressid IN (%s)' % q for q in [cquery, lquery]])
        addresses = self.getAddresses(aclause)
        adata = RefData(dict(address='addressid'))
        adata.set_refdata('address', addresses)
        contacts, ignore = self.getContacts(clientid, False)
        contacts = [RefRecord(c, adata) for c in contacts]
        locations, ignore = self.getLocations(clientid, False)
        locations = [RefRecord(l, adata) for l in locations]
        return dict(client=client, contacts=contacts,
                    locations=locations, addresses=adata)

    def insertClient(self, client):
        clientid = self.db.select_row(fields=["nextval('client_ident')"]).nextval
        data = dict(clientid=clientid, client=client)
        self.db.insert(table='clients', data=data)
        self.db.conn.commit()
        return clientid
    
        
    def updateClient(self, clientid, name):
        data = dict(client=name)
        self.db.update(table='clients', data=data, clause=Eq('clientid', clientid))
        
        
    def getTags(self, clientid):
        clause = Eq('clientid', clientid)
        tagrows = self.db.select(table='client_tags', clause=clause)
        tagdict = {}
        for row in tagrows:
            tagdict[row.tag] = row.value
        return tagdict
    
