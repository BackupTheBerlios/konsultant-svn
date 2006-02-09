import cherrypy

from useless.base.forgethtml import SimpleDocument

#from myHTML import Paragraph
import os
import md5

from useless.base.forgethtml import Anchor, Form, Input
from useless.base.forgethtml import TableHeader, TableCell
from useless.base.forgethtml import TableRow, Table
from useless.base.forgethtml import Inline, Link, Paragraph
from useless.base.forgethtml import SimpleDocument
from useless.base.forgethtml import Stylesheet
from useless.base.forgethtml import Header, Pre
from useless.base.forgethtml import Favicon, Bold
from useless.base.util import strfile

from konsultant.newdb import BaseDatabase
from konsultant.newdb.managers.client import ClientManager

# to replace SimpleTitleElement
class SimpleTitleTable(Table):
    def __init__(self, title, **args):
        Table.__init__(self, **args)
        self.row = TableRow()
        self.td = TableCell()
        self.append(self.row)
        self.row.append(self.td)
        self.set_title(title)
        
    def set_title(self, title):
        self._title = title
        self.td.set(Header(title, 1))

# to replace RecordElement
class RecordTableOrig(Table):
    def __init__(self, fields, idcol, action, record, **args):
        Table.__init__(self, **args)
        self.record = record
        refdata = None
        if hasattr(record, '_refdata'):
            refdata = record._refdata
        for field in fields:
            row = TableRow()
            row.append(TableCell(Bold(field)))
            val = TableCell()
            data = str(record[field])
            if refdata is not None and field in refdata.cols:
                print 'hello there - fix me'
            elif action:
                val.append(Anchor(data, href=action))
            else:
                val.append(data)
            row.append(val)
            self.append(row)

class RecordTable(Table):
    def __init__(self, fields, idcol, action, record, **args):
        Table.__init__(self, **args)
        self.record = record
        for field in fields:
            row = TableRow()
            row.append(TableCell(Bold(field)))
            val = TableCell()
            data = str(record[field])
            if action:
                href = '%s?%s=%s' % (action, idcol, record[idcol])
                a = Anchor(data, href=href)
                val.append(a)
            else:
                val.append(data)
            row.append(val)
            self.append(row)
                
############################
############################
# this small set of functions were
# created to test with and should
# be replaced
def string2rows(strdata, class_=None):
    lines = strdata.split('\n')
    if class_ is None:
        return [TableRow(TableCell(line)) for line in lines]
    else:
        atts = dict(class_=class_)
        return [TableRow(TableCell(line, **atts), **atts) for line in lines]
    
def cmd2table(cmd):
    i, o = os.popen2(cmd)
    rows = string2rows(o.read())
    head = TableRow(TableHeader(cmd))
    allrows = [head] + rows
    t = Table()
    t.extend(allrows)
    return t

def cmd2pre(cmd):
    i, o = os.popen2(cmd)
    return Pre(o.read())

def simplelink(name):
    return Anchor(name, href=name)

#############################
#############################

class BasePage(SimpleDocument):
    def __init__(self, title='BasePage', stylesheet='/css/default.css', **args):
        SimpleDocument.__init__(self, title=title, stylesheet=stylesheet)
        self.set_stylesheet()
        self.favicon = Favicon()
        self.head.append(self.favicon)
        #body.set will overwrite the self.header h1 tag
        #self.body.set(self.maintable)
        # always start with login
        #self.maintable.set_mainrow(BaseLoginForm('/doLogin'))
            

    def set_stylesheet(self, sheet=None):
        if sheet is None:
            sheet = '/css/default.css'
        self.setStylesheet('/css/%s' % sheet)
        
class DocPage(object):
    h1 = 'konsultant database'
    h2 = 'Doc Page'
    foot = 'Doc Page'
    menu_entries = []
    menu_head = 'Basic Menu'

    def prepare_doc(self, doc):
        pass
        
    def get_docobject(self, docobject='DocumentObject'):
        if docobject not in cherrypy.session:
            doc = BasePage()
            cherrypy.session[docobject] = doc
        doc = cherrypy.session[docobject]
        self.prepare_doc(doc)
        return doc
    
    def get_username(self):
        username = ''
        if 'username' in cherrypy.session:
            username  = cherrypy.session['username']
        return username

    def get_session(self):
        return cherrypy.session

    def get_dbconn(self, conn='MainDBConn'):
        if conn not in cherrypy.session:
            db = BaseDatabase()
            cherrypy.session[conn] = db
        db = cherrypy.session[conn]
        return db
    
