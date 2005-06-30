#from operator import and_
from xml.dom.minidom import Element, Text

from useless.base import NoExistError
from useless.sqlgen.clause import Eq, In

from useless.xmlgen.base import Html, Body, Anchor
from useless.xmlgen.base import TextElement
from useless.xmlgen.base import TableElement
from useless.xmlgen.base import BaseElement
from useless.xmlgen.base import UnorderedList, ListItem, BR, HR
from useless.kdb.xmlgen import BaseDocument
from useless.kdb.xmlgen import BaseParagraph

from db import TroubleManager

class P(TextElement):
    def __init__(self, text):
        TextElement.__init__(self, 'p', text)
        
class TitleTable(BaseElement):
    def __init__(self, title):
        BaseElement.__init__(self, 'table')
        self.setAttribute('border', '1')
        #self.setAttribute('width', '100%')
        self.setAttribute('cellpadding', '2')
        self.setAttribute('cellspacing', '0')
        self.setAttribute('bgcolor', 'IndianRed')
        row = BaseElement('tr')
        td = BaseElement('td')
        self.appendChild(row)
        row.appendChild(td)
        font = BaseElement('font')
        font.setAttribute('color', 'gold')
        td.appendChild(font)
        element = TextElement('b', title)
        font.appendChild(element)

class TroubleHeader(BaseElement):
    def __init__(self, troubleid, info):
        BaseElement.__init__(self, 'p')
        self.created = TextElement('h4', 'Created: %s' % info['posted'])
        self.appendChild(self.created)
        p = BaseElement('p')
        refresh = Anchor('refresh.page.%d' % troubleid, 'refresh')
        p.appendChild(refresh)
        self.appendChild(p)

class TroubleFooter(BaseElement):
    def __init__(self, troubleid):
        BaseElement.__init__(self, 'h3')
        self.append = Anchor('new.action.none', 'append')
        self.appendChild(self.append)
        
class TicketTableElement(TableElement):
    def __init__(self, db=None):
        cols = ['title', 'status']
        TableElement.__init__(self, cols)

class TroubleData(TextElement):
    def __init__(self, data):
        TextElement.__init__(self, 'p', data)

class ActionTableRow(BaseElement):
    def __init__(self, row):
        BaseElement.__init__(self, 'tr')
        table = BaseElement('table')
        top = BaseElement('tr', bgcolor='DarkSeaGreen')
        table.appendChild(top)
        mid = BaseElement('tr', bgcolor='DarkSeaGreen3')
        table.appendChild(mid)
        bottom = BaseElement('tr', bgcolor='DarkSeaGreen2')
        table.appendChild(bottom)
        action = TextElement('td', row.action)
        action.setAttribute('align', 'left')
        posted = TextElement('td', row.posted)
        posted.setAttribute('align', 'right')
        top.appendChild(action)
        top.appendChild(posted)
        mid.appendChild(TextElement('td', row.workdone))
        instatus = TextElement('td', row.instatus)
        outstatus = TextElement('td', row.outstatus)
        instatus.setAttribute('align', 'left')
        outstatus.setAttribute('align', 'right')
        bottom.appendChild(instatus)
        bottom.appendChild(outstatus)
        self.appendChild(top)
        self.appendChild(mid)
        self.appendChild(bottom)
        if row.instatus != row.outstatus:
            bottom.setAttribute('bgcolor', 'GoldenRod')
            

class ActionTable(BaseElement):
    def __init__(self, actionrows):
        BaseElement.__init__(self, 'table')
        for row in actionrows:
            self.appendChild(ActionTableRow(row))
            
class TroubleInfoElement(BaseElement):
    def __init__(self, info):
        troubleid  = info['troubleid']
        problem = info['problem']
        worktodo = info['worktodo']
        status = info['status']
        posted = info['posted']
        BaseElement.__init__(self, 'div')
        self.setAttribute('id', 'trouble-%d' % troubleid)
        self.setAttribute('class', 'troubleinfo')
        self.title = TitleTable(problem)
        self.client = TextElement('h3', 'Client: %s' % info['client'])
        self.posted = TextElement('b', 'Created: %s' % posted)
        self.worktodo = TextElement('p', worktodo)
        self.appendChild(self.title)
        self.appendChild(self.client)
        self.appendChild(BR())
        self.appendChild(self.posted)
        self.appendChild(self.worktodo)
        self.anchor = Anchor('show.trouble.%d' % troubleid, 'show')
        self.assign = Anchor('assign.trouble.%d' % troubleid, 'assign')
        node = BaseElement('table')
        node.setAttribute('width', '100%')
        node.setAttribute('align', 'center')
        self.appendChild(node )
        row = BaseElement('tr')
        row.appendChild(TextElement('td', self.anchor))
        td  = TextElement('td', self.assign)
        td.setAttribute('align', 'right')
        row.appendChild(td)
        node.appendChild(row)
    

class TroubleDocument(BaseDocument):
    def __init__(self, app):
        BaseDocument.__init__(self, app)
        self.manager = TroubleManager(self.app)

    def setID(self, clause=None, ids=None):
        self.clear_body()
        rows = self.manager.getTroubles(clause=clause)
        for row in rows:
            info = dict(row)
            crow = self.db.select_row(table='clients', clause=Eq('clientid', row.clientid))
            info['client'] = crow.client
            element = TroubleInfoElement(info)
            self.body.appendChild(element)
            self.body.appendChild(HR())

class TroubleInfoDoc(BaseDocument):
    def __init__(self, app):
        BaseDocument.__init__(self, app)
        self.manager = TroubleManager(self. app)

    def set_clause(self, clause):
        self.clear_body()
        rows = self.db.select(fields=['title'], table='tickets')

    def setID(self, troubleid):
        #row = self.manager.get_ticket(troubleid, data=True)
        info = self.manager.getTroubleInfo(troubleid)
        self.current = troubleid
        self.clear_body()
        #make header
        self.body.appendChild(TitleTable(info['problem']))
        self.header = TroubleHeader(troubleid, info)
        self.body.appendChild(self.header)
        hr = BaseElement('hr')
        self.body.appendChild(hr)
        #append ticket data
        tdata = TroubleData(info['worktodo'])
        self.body.appendChild(tdata)
        hr = BaseElement('hr')
        self.body.appendChild(hr)
        #append ticket footer
        self.tfooter = TroubleFooter(troubleid)
        self.body.appendChild(self.tfooter)
        #actions, rows, trows, crows = self.manager.get_actions(troubleid, True)
        #athreads = ActionThreads(self.body, actions, trows, crows)
        #self.body.appendChild(athreads)
        #self.threads = athreads
        actionrows = info['actions']
        print actionrows
        self.body.appendChild(ActionTable(actionrows))
                                                                   
    def showActionData(self, actionid):
        data = self.manager.get_actiondata(self.current, actionid)
        self.threads.show_data(actionid, data)

    def hideActionData(self, actionid):
        self.threads.hide_data(actionid)
        
