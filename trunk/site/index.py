import cherrypy


import os
import md5

from useless.base.forgethtml import Anchor, Form, Input
from useless.base.forgethtml import TableHeader, TableCell
from useless.base.forgethtml import TableRow, Table
from useless.base.forgethtml import Inline, Link, Paragraph
from useless.base.forgethtml import SimpleDocument
from useless.base.forgethtml import Stylesheet
from useless.base.forgethtml import Header, Pre
from useless.base.forgethtml import Break

from useless.base.util import strfile

from common import DocPage

from common import RecordTable

from client import ClientPage

class RootPage(DocPage):
    h2 = 'Home Page'
    foot = 'This is the top page.'
    def __init__(self):
        DocPage.__init__(self)
        self.clients = ClientPage()
        
    def index(self):
        doc = self.get_docobject()
        #db = self.get_dbconn()
        #m = ClientManager(db)

        p = Paragraph(align='left')
        p.append(Anchor('clients', href='clients'))
        doc.body.set(p)
        return str(doc)
    index.exposed = True


if __name__ == '__main__':
    print "Running server in dev mode"
    cherrypy.root = RootPage()
    cherrypy.config.update(file='k-server.ini')
    cherrypy.server.start()
