#from operator import and_
from xml.dom.minidom import Element, Text

from useless.base import NoExistError
from useless.sqlgen.clause import Eq, In

from useless.xmlgen.base import Html, Body, Anchor
from useless.xmlgen.base import TextElement
from useless.xmlgen.base import TableElement
from useless.xmlgen.base import BaseElement
from useless.xmlgen.base import UnorderedList, ListItem
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

class CommandBar(BaseElement):
    def __init__(self, troubleid):
        BaseElement.__init__(self, 'table')
        row = BaseElement('tr')
        self.anchor = Anchor('show.ticket.%d' % troubleid, 'show')
        self.assign = Anchor('assign.ticket.%d' % troubleid, 'assign')
        
class SubjectTable(BaseElement):
    def __init__(self, subject, action, author, posted):
        BaseElement.__init__(self, 'table')
        #self.app  = app
        self.setAttribute('border', '0')
        self.setAttribute('width', '100%')
        self.setAttribute('cellpadding', '2')
        self.setAttribute('cellspacing', '0')
        self.setAttribute('bgcolor', 'cornsilk4')
        row = BaseElement('tr')
        self.appendChild(row)
        td = self._subjectdata(subject, action)
        row.appendChild(td)
        
        row = BaseElement('tr')
        self.appendChild(row)
        row.setAttribute('bgcolor', 'bisque4')
        td = self._subjectdata(author, posted)
        row.appendChild(td)
        

    def _subjectdata(self, subject, action):
        td = BaseElement('td')

        font = BaseElement('font')
        font.setAttribute('color', 'gold')
        element = TextElement('b', subject)
        font.appendChild(element)
        td.appendChild(font)

        font = BaseElement('font')
        font.setAttribute('color', 'yellow')
        element = Text()
        font.appendChild(element)
        element.data = '(%s)' % action
        td.appendChild(font)
        return td
    
class TroubleTable(BaseElement):
    def __init__(self, problem, worktodo, status, posted):
        BaseElement.__init__(self, 'table')
        #self.app  = app
        self.setAttribute('border', '0')
        self.setAttribute('width', '100%')
        self.setAttribute('cellpadding', '2')
        self.setAttribute('cellspacing', '0')
        self.setAttribute('bgcolor', 'cornsilk4')
        row = BaseElement('tr')
        self.appendChild(row)
        td = self._subjectdata(subject, action)
        row.appendChild(td)
        
        row = BaseElement('tr')
        self.appendChild(row)
        row.setAttribute('bgcolor', 'bisque4')
        td = self._subjectdata(author, posted)
        row.appendChild(td)
        

    def _subjectdata(self, subject, action):
        td = BaseElement('td')

        font = BaseElement('font')
        font.setAttribute('color', 'gold')
        element = TextElement('b', subject)
        font.appendChild(element)
        td.appendChild(font)

        font = BaseElement('font')
        font.setAttribute('color', 'yellow')
        element = Text()
        font.appendChild(element)
        element.data = '(%s)' % action
        td.appendChild(font)
        return td
    
class TroubleHeader(BaseElement):
    def __init__(self, troubleid, info):
        BaseElement.__init__(self, 'p')
        #self.author = TextElement('h5', 'Author: %s' % row.author)
        self.created = TextElement('h4', 'Created: %s' % info['posted'])
        #node = TextElement('h2', row.title)
        #self.appendChild(node)
        self.appendChild(self.created)
        #self.appendChild(self.author)
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
            
class ActionItem(BaseElement):
    def __init__(self, row):
        BaseElement.__init__(self, 'li')
        self.actionid = row.actionid
        action = TextElement('h3', row.action)
        posted = TextElement('h2', 'Posted: %s' % row.posted)
        workdone = TextElement('p', row.workdone)
        l = 'in: %s' % row.instatus
        r = 'out: %s' % row.outstatus
        status = self._lrtable(l, r)
        actpost = self._lrtable(row.action, 'Posted: %s' % row.posted)
        #self.appendChild(posted)
        #self.appendChild(action)
        self.appendChild(actpost)
        self.appendChild(workdone)
        self.appendChild(status)
        

    def _lrtable(self, left, right):
        table = BaseElement('table')
        tr = BaseElement('tr')
        table.appendChild(tr)
        tdl = BaseElement('td', align='left')
        tr.appendChild(tdl)
        tdr = BaseElement('td', align='right')
        tr.appendChild(tdr)
        left_part = Text()
        left_part.data = left
        right_part = Text()
        right_part.data = right
        tdl.appendChild(left_part)
        tdr.appendChild(right_part)
        return table
        
    def show_data(self, data):
        anchor = self.anchor
        child = self.lastChild
        anchor.setAttribute('href', 'hide.action.%d' % self.actionid)
        self.data = data
        self.insertBefore(TextElement('p', data), child)

    def hide_data(self):
        self.anchor.setAttribute('href', 'show.action.%d' % self.actionid)
        del self.childNodes[1]

class ActionTable(BaseElement):
    def __init__(self, actionrows):
        BaseElement.__init__(self, 'table')
        for row in actionrows:
            self.appendChild(ActionTableRow(row))
            
class TroubleInfoElement(BaseElement):
    def __init__(self, troubleid, problem, worktodo,
                 status, posted):
        BaseElement.__init__(self, 'div')
        self.setAttribute('id', 'trouble-%d' % troubleid)
        self.setAttribute('class', 'troubleinfo')
        self.title = TitleTable(problem)
        #self.title = TextElement('h4', title)
        #self.author = TextElement('h5', 'Author: %s' % author)
        self.posted = TextElement('h4', 'Created: %s' % posted)
        self.worktodo = TextElement('p', worktodo)
        self.appendChild(self.title)
        #self.appendChild(self.author)
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
            element = TroubleInfoElement(row.troubleid, row.problem,
                                         row.worktodo, row.status, row.posted)
            self.body.appendChild(element)

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
        
