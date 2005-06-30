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

class TitleTable(BaseElement):
    def __init__(self, title):
        BaseElement.__init__(self, 'table')
        self.setAttribute('border', '1')
        #self.setAttribute('width', '100%')
        self.setAttribute('cellpadding', '2')
        self.setAttribute('cellspacing', '0')
        self.setAttribute('bgcolor', 'cornsilk4')
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
    
class TicketHeader(BaseElement):
    def __init__(self, troubleid, row):
        BaseElement.__init__(self, 'p')
        self.author = TextElement('h5', 'Author: %s' % row.author)
        self.created = TextElement('h5', 'Created: %s' % row.created)
        #node = TextElement('h2', row.title)
        #self.appendChild(node)
        self.appendChild(self.created)
        self.appendChild(self.author)
        p = BaseElement('p')
        refresh = Anchor('refresh.page.%d' % troubleid, 'refresh')
        assign = Anchor('assign.ticket.%d' % troubleid, 'assign')
        p.appendChild(refresh)
        p.appendChild(BaseElement('br'))
        p.appendChild(assign)
        self.appendChild(p)

class TicketFooter(BaseElement):
    def __init__(self, troubleid):
        BaseElement.__init__(self, 'h3')
        self.respond = Anchor('new.action.none', 'respond')
        self.appendChild(self.respond)
        
class TicketTableElement(TableElement):
    def __init__(self, db=None):
        cols = ['title', 'status']
        TableElement.__init__(self, cols)

class TicketData(TextElement):
    def __init__(self, data):
        TextElement.__init__(self, 'p', data)

class ActionItem(ListItem):
    def __init__(self, row):
        self.actionid = row.actionid
        url = 'show.action.%d' % self.actionid
        self.anchor = Anchor(url, row.subject)
        #element = TitleTable(self.anchor)
        element = SubjectTable(self.anchor, row.action, row.author, row.posted)
        element.setAttribute('width', '100%')
        element.setAttribute('border', '0')
        url = 'new.action.%d' % self.actionid
        ListItem.__init__(self, element)
        self.appendChild(Anchor(url, ' (respond)'))

    def show_data(self, data):
        anchor = self.anchor
        child = self.lastChild
        anchor.setAttribute('href', 'hide.action.%d' % self.actionid)
        self.data = data
        self.insertBefore(TextElement('p', data), child)

    def hide_data(self):
        self.anchor.setAttribute('href', 'show.action.%d' % self.actionid)
        del self.childNodes[1]
        
        
class ActionThreads(UnorderedList):
    def __init__(self, parent, actions, trows, crows):
        UnorderedList.__init__(self)
        self._actiondata = {}
        for a in actions:
            self._actiondata[a.actionid] = a
        self.actions = {}
        for row in trows:
            element = UnorderedList()
            #li = ListItem('action-%d' % row.actionid)
            li = ActionItem(self._actiondata[row.actionid])
            element.appendChild(li)
            self.actions[row.actionid] = element
            self.appendChild(element)
        self.make_threads(parent, crows)
        
    def make_threads(self, parent, rows):
        while len(rows):
            row = rows[0]
            element = UnorderedList()
            #element = ListItem('actionid %d' % row.actionid)
            if not row.parent:
                parent.appendChild(element)
                #element.appendChild(ListItem('actionid--%d' % row.actionid))
            elif not self.actions.has_key(row.parent):
                rows.append(row)
            else:
                self.actions[row.parent].appendChild(element)
                element.appendChild(ActionItem(self._actiondata[row.actionid]))
            self.actions[row.actionid] = element
            del rows[0]

    def show_data(self, actionid, data):
        element = self.actions[actionid].firstChild
        element.show_data(data)

    def hide_data(self, actionid):
        element = self.actions[actionid].firstChild
        element.hide_data()
        
class TroubleInfoElement(BaseElement):
    def __init__(self, troubleid, problem, worktodo,
                 status, posted):
        BaseElement.__init__(self, 'div')
        self.setAttribute('id', 'trouble-%d' % troubleid)
        self.setAttribute('class', 'troubleinfo')
        self.title = TitleTable(problem)
        #self.title = TextElement('h4', title)
        #self.author = TextElement('h5', 'Author: %s' % author)
        self.posted = TextElement('h5', 'Created: %s' % posted)
        self.appendChild(self.title)
        #self.appendChild(self.author)
        self.appendChild(self.posted)
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
        row = self.manager.get_ticket(troubleid, data=True)
        self.current = troubleid
        self.clear_body()
        #make header
        self.body.appendChild(TitleTable(row.title))
        self.header = TicketHeader(troubleid, row)
        self.body.appendChild(self.header)
        hr = BaseElement('hr')
        self.body.appendChild(hr)
        #append ticket data
        tdata = TicketData(row.data)
        self.body.appendChild(tdata)
        hr = BaseElement('hr')
        self.body.appendChild(hr)
        #append ticket footer
        self.tfooter = TicketFooter(troubleid)
        self.body.appendChild(self.tfooter)
        actions, rows, trows, crows = self.manager.get_actions(troubleid, True)
        athreads = ActionThreads(self.body, actions, trows, crows)
        self.body.appendChild(athreads)
        self.threads = athreads

    def showActionData(self, actionid):
        data = self.manager.get_actiondata(self.current, actionid)
        self.threads.show_data(actionid, data)

    def hideActionData(self, actionid):
        self.threads.hide_data(actionid)
        
