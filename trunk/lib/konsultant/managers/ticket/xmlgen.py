#from operator import and_
from xml.dom.minidom import Element, Text

from konsultant.base import NoExistError
from konsultant.sqlgen.clause import Eq, In

from konsultant.base.xmlgen import Html, Body, Anchor
from konsultant.base.xmlgen import TextElement
from konsultant.base.xmlgen import TableElement
from konsultant.base.xmlgen import BaseElement
from konsultant.base.xmlgen import UnorderedList, ListItem
from konsultant.db.xmlgen import BaseDocument
from konsultant.db.xmlgen import BaseParagraph

from db import TicketManager

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
    
class TicketHeader(BaseElement):
    def __init__(self, ticketid, row):
        BaseElement.__init__(self, 'p')
        self.author = TextElement('h5', 'Author: %s' % row.author)
        self.created = TextElement('h5', 'Created: %s' % row.created)
        #node = TextElement('h2', row.title)
        #self.appendChild(node)
        self.appendChild(self.created)
        self.appendChild(self.author)
        p = BaseElement('p')
        refresh = Anchor('refresh.page.%d' % ticketid, 'refresh')
        p.appendChild(refresh)
        self.appendChild(p)

class TicketFooter(BaseElement):
    def __init__(self, ticketid):
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
        print self.anchor.getAttribute('href'), 'href'
        child = self.lastChild
        print anchor.toxml(), child.toxml()
        anchor.setAttribute('href', 'hide.action.%d' % self.actionid)
        self.data = data
        self.insertBefore(TextElement('p', data), child)

    def hide_data(self):
        self.anchor.setAttribute('href', 'show.action.%d' % self.actionid)
        print self.anchor.getAttribute('href'), 'href'
        print ['%s-----' % c for c in self.childNodes]
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
                print row.parent, 'is not there'
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
        
class TicketInfoElement(BaseElement):
    def __init__(self, ticketid, title, author, created):
        BaseElement.__init__(self, 'div')
        self.setAttribute('id', 'ticket-%d' % ticketid)
        self.setAttribute('class', 'ticketinfo')
        self.title = TitleTable(title)
        #self.title = TextElement('h4', title)
        self.author = TextElement('h5', 'Author: %s' % author)
        self.created = TextElement('h5', 'Created: %s' % created)
        self.appendChild(self.title)
        self.appendChild(self.author)
        self.appendChild(self.created)
        self.anchor = Anchor('show.ticket.%d' % ticketid, 'show')
        self.appendChild(self.anchor)
        
        
        
    

class TicketDocument(BaseDocument):
    def __init__(self, app):
        BaseDocument.__init__(self, app)
        #self.body.setAttribute('bgcolor', 'MistyRose4')
        #self.body.setAttribute('link', 'plum')
        #self.body.setAttribute('hover', 'green')
        self.manager = TicketManager(self.app)

    def setID(self, clause=None, ids=None):
        self.clear_body()
        rows = self.manager.get_tickets(clause)
        for row in rows:
            element = TicketInfoElement(row.ticketid, row.title,
                                        row.author, row.created)
            self.body.appendChild(element)

class TicketInfoDoc(BaseDocument):
    def __init__(self, app):
        BaseDocument.__init__(self, app)
        self.manager = TicketManager(self. app)

    def set_clause(self, clause):
        self.clear_body()
        rows = self.db.select(fields=['title'], table='tickets')

    def setID(self, ticketid):
        row = self.manager.get_ticket(ticketid, data=True)
        self.current = ticketid
        self.clear_body()
        #make header
        self.body.appendChild(TitleTable(row.title))
        self.header = TicketHeader(ticketid, row)
        self.body.appendChild(self.header)
        hr = BaseElement('hr')
        self.body.appendChild(hr)
        #append ticket data
        tdata = TicketData(row.data)
        self.body.appendChild(tdata)
        hr = BaseElement('hr')
        self.body.appendChild(hr)
        #append ticket footer
        self.tfooter = TicketFooter(ticketid)
        self.body.appendChild(self.tfooter)
        actions, rows, trows, crows = self.manager.get_actions(ticketid, True)
        athreads = ActionThreads(self.body, actions, trows, crows)
        self.body.appendChild(athreads)
        self.threads = athreads

    def showActionData(self, actionid):
        data = self.manager.get_actiondata(self.current, actionid)
        self.threads.show_data(actionid, data)

    def hideActionData(self, actionid):
        self.threads.hide_data(actionid)
        
