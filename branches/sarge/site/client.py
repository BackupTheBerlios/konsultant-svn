from useless.base.forgethtml import Paragraph, Anchor, Break
from useless.base.util import strfile

from common import DocPage
from common import RecordTable
from common import SimpleTitleTable
from konsultant.newdb.managers.client import ClientManager

class ClientTable(RecordTable):
    def __init__(self, row, action, **args):
        fields = ['client']
        RecordTable.__init__(self, fields, 'clientid', action, row, **args)
        
class ContactTable(RecordTable):
    def __init__(self, row, action, **args):
        fields = ['name', 'email', 'description']
        RecordTable.__init__(self, fields, 'contactid', action, row, **args)

class LocationTable(RecordTable):
    def __init__(self, row, action, **args):
        fields = ['name', 'isp', 'connection', 'ip', 'static', 'serviced']
        RecordTable.__init__(self, fields, 'locationid', action, row, **args)
        

class ClientPage(DocPage):
    h2 = 'Home Page'
    foot = 'This is the top page.'
    def __init__(self):
        DocPage.__init__(self)

    def index(self):
        #doc = self.get_docobject()
        #db = self.get_dbconn()
        #m = ClientManager(db)
        doc, db, m = self._get_session_info()
        p = Paragraph('Clients:', align='left')
        doc.body.set(p)
        for row in m.getClientList():
            doc.body.append(ClientTable(row, 'clientInfo'))
            #p.append(Anchor(cname, href='clientInfo?clientid=%s' % cid))
            #p.append(Break())
        doc.setTitle('Clients')
        return str(doc)
    index.exposed = True

    def clientInfo(self, clientid):
        doc, db, m = self._get_session_info()
        data = strfile()
        info = m.getClientInfo(clientid)
        data.write(str(info))
        doc.body.set(Paragraph(data.getvalue()))
        doc.setTitle('Client Info for %s' % info['client'])
        doc.body.append(SimpleTitleTable('Contacts'))
        for contact in info['contacts']:
            doc.body.append(ContactTable(contact, None))
        doc.body.append(SimpleTitleTable('Locations'))
        for location in info['locations']:
            doc.body.append(LocationTable(location, None))
        doc.body.append(Anchor('back', href='index'))
        
        return str(doc)
    clientInfo.exposed = True

    def _get_session_info(self):
        doc, db = self.get_docobject(), self.get_dbconn()
        m = ClientManager(db)
        return doc, db, m

if __name__ == '__main__':
    print "Running server in dev mode"
    cherrypy.root = RootPage()
    cherrypy.config.update(file='k-server.ini')
    cherrypy.server.start()
