from qt import SIGNAL, SLOT
from qt import QVBoxLayout, QHBoxLayout, QFrame

from kdeui import KStdAction, KPopupMenu
from kdeui import KListViewItem
from kdeui import KMessageBox

from kdeui import KDialogBase, KLineEdit
from kdeui import KTextEdit, KMainWindow

from konsultant.base.gui import MainWindow
from konsultant.db import BaseDatabase
from konsultant.db.gui import BaseManagerWidget, ViewBrowser
from konsultant.sqlgen.clause import Eq, In

from xmlgen import TicketInfoDoc
from xmlgen import TicketDocument

from db import TicketManager

TICKETSTATUS = ['new', 'open', 'closed']
class VboxDialog(KDialogBase):
    def __init__(self, parent, name='VboxDialog'):
        KDialogBase.__init__(self, parent, name)
        self.page = QFrame(self)
        self.setMainWidget(self.page)
        self.vbox = QVBoxLayout(self.page, 5, 7)
        


class TicketDialog(VboxDialog):
    def __init__(self, parent, name='TicketDialog'):
        VboxDialog.__init__(self, parent, name)
        self.titleEdit = KLineEdit('', self.page)
        self.dataEdit = KTextEdit(self.page)
        self.vbox.addWidget(self.titleEdit)
        self.vbox.addWidget(self.dataEdit)
        self.showButtonApply(False)
        self.setButtonOKText('insert', 'insert')
        self.show()
        
class ActionDialog(VboxDialog):
    def __init__(self, parent, name='ActionDialog'):
        VboxDialog.__init__(self, parent, name)
        self.subjEdit = KLineEdit('', self.page)
        self.actionEdit = KLineEdit('comment', self.page)
        self.dataEdit = KTextEdit(self.page)
        self.vbox.addWidget(self.subjEdit)
        self.vbox.addWidget(self.actionEdit)
        self.vbox.addWidget(self.dataEdit)
        self.showButtonApply(False)
        self.setButtonOKText('insert', 'insert')
        self.show()

class TicketActionView(ViewBrowser):
    def __init__(self, db, parent, ticketid):
        ViewBrowser.__init__(self, db, parent, TicketInfoDoc)
        self.dialogs = {}
        self.manager = TicketManager(self.db)

    def setSource(self, url):
        action, context, id = str(url).split('.')
        print action, context, id
        if context == 'action':
            if action == 'new':
                dlg = ActionDialog(self, 'ActionDialog')
                dlg.connect(dlg, SIGNAL('okClicked()'), self.insertAction)
                dlg.ticketid = self.doc.current
                if id == 'none':
                    dlg.actionid = None
                else:
                    dlg.actionid = int(id)
                self.dialogs['new-action'] = dlg
            elif action == 'show':
                element = self.doc.threads.actions[int(id)]
                self.doc.showActionData(int(id))
                self.setText(self.doc.toxml())
            elif action == 'hide':
                self.doc.hideActionData(int(id))
                self.setText(self.doc.toxml())
        elif context == 'page':
            if action == 'refresh':
                self.setID(self.current)
                print 'fresh page'
                
    def setID(self, ticketid):
        self.current = ticketid
        self.doc.setID(ticketid)
        self.setText(self.doc.toxml())

    def insertAction(self):
        dlg = self.dialogs['new-action']
        subject = str(dlg.subjEdit.text())
        action = str(dlg.actionEdit.text())
        data = str(dlg.dataEdit.text())
        ticketid = dlg.ticketid
        actionid = self.manager.append_action(ticketid, subject, action,
                                              data, parent=dlg.actionid)
        self.setID(ticketid)
        
        
        
class TicketView(ViewBrowser):
    def __init__(self, db, parent):
        ViewBrowser.__init__(self, db, parent, TicketDocument)
        self.dialogs = {}
        self.manager = TicketManager(self.db)

    def setID(self, ticketid=None, clause=None):
        self.doc.setID(clause=clause)
        self.setText(self.doc.toxml())

    def insertAction(self):
        dlg = self.dialogs['new-action']
        subject = str(dlg.subjEdit.text())
        action = str(dlg.actionEdit.text())
        data = str(dlg.dataEdit.text())
        ticketid = dlg.ticketid
        actionid = self.manager.append_action(ticketid, subject, action,
                                              data, parent=dlg.actionid)
        self.setID(ticketid)
        
    def setSource(self, url):
        action, context, id = str(url).split('.')
        print action, context, id
        if context == 'ticket':
            if action == 'show':
                print 'showing ticket %s' % id
                win = KMainWindow(self)
                v = TicketActionView(self.db, win, int(id))
                v.setID(int(id))
                v.resize(400, 600)
                win.setCentralWidget(v)
                win.resize(400, 600)
                win.show()
                
class TicketManagerWidgetNew(BaseManagerWidget):
    def __init__(self, parent, db, *args):
        self.db = db
        self.manager = TicketManager(self.db)
        BaseManagerWidget.__init__(self, parent, db, TicketView, 'TicketManager')
        self.dialogs = {}

    def initActions(self):
        collection = self.actionCollection()
        self.newAction = KStdAction.openNew(self.slotNew, collection)

    def initMenus(self):
        menu = KPopupMenu(self)
        self.newAction.plug(menu)
        self.menuBar().insertItem('&Main', menu)
        self.menuBar().insertItem('&Help', self.helpMenu(''))

    def initlistView(self):
        self.listView.setRootIsDecorated(True)
        self.listView.addColumn('ticket group')
        self.refreshlistView()

    def refreshlistView(self):
        self.listView.clear()
        all = KListViewItem(self.listView, 'all')
        client = KListViewItem(self.listView, 'client')
        rows = self.db.select(fields=['clientid', 'client'], table='clients')
        for row in rows:
            c = KListViewItem(client, row.client)
            c.clientid = row.clientid
        unassigned = KListViewItem(self.listView, 'unassigned')
        
    def slotNew(self, title='', data=''):
        dlg = TicketDialog(self)
        dlg.titleEdit.setText(title)
        dlg.dataEdit.setText(data)
        self.connect(dlg, SIGNAL('okClicked()'), self.create_ticket)
        self.dialogs['new-ticket'] = dlg

    def create_ticket(self):
        dlg = self.dialogs['new-ticket']
        title = str(dlg.titleEdit.text())
        data = str(dlg.dataEdit.text())
        if data and title:
            self.manager.create_ticket(title, data)
            self.refreshlistView()
        elif title:
            KMessageBox.error(self, "just a title won't do.")
            self.slotNew(title=title)
        elif data:
            KMessageBox.error(self, "You also need a title.")
            self.slotNew(data=data)
        else:
            KMessageBox.information(self, 'Nothing Done.')
        
            
    def selectionChanged(self):
        current = self.listView.currentItem()
        print current
        if hasattr(current, 'ticketid'):
            self.view.setID(current.ticketid)
        elif hasattr(current, 'clientid'):
            clientid = current.clientid
            sel = self.db.stmt.select(fields=['ticketid'], table='client_tickets',
                                   clause=Eq('clientid', clientid))
            
            clause = In('ticketid', sel)
            self.view.setID(clause=clause)
        else:
            self.view.setID(None)

            
#################################################
        
class TicketViewOrig(ViewBrowser):
    def __init__(self, db, parent):
        ViewBrowser.__init__(self, db, parent, TicketInfoDoc)
        self.dialogs = {}
        self.manager = TicketManager(self.db)

    def setSource(self, url):
        action, context, id = str(url).split('.')
        print action, context, id
        if context == 'action':
            if action == 'new':
                dlg = ActionDialog(self, 'ActionDialog')
                dlg.connect(dlg, SIGNAL('okClicked()'), self.insertAction)
                dlg.ticketid = self.doc.current
                if id == 'none':
                    dlg.actionid = None
                else:
                    dlg.actionid = int(id)
                self.dialogs['new-action'] = dlg
            elif action == 'show':
                element = self.doc.threads.actions[int(id)]
                self.doc.showActionData(int(id))
                self.setText(self.doc.toxml())
            elif action == 'hide':
                self.doc.hideActionData(int(id))
                self.setText(self.doc.toxml())
                
    def setID(self, ticketid):
        self.doc.setID(ticketid)
        self.setText(self.doc.toxml())

    def insertAction(self):
        dlg = self.dialogs['new-action']
        subject = str(dlg.subjEdit.text())
        action = str(dlg.actionEdit.text())
        data = str(dlg.dataEdit.text())
        ticketid = dlg.ticketid
        actionid = self.manager.append_action(ticketid, subject, action,
                                              data, parent=dlg.actionid)
        self.setID(ticketid)
        
        

class TicketManagerWidgetOrig(BaseManagerWidget):
    def __init__(self, parent, db, *args):
        self.db = db
        self.manager = TicketManager(self.db)
        BaseManagerWidget.__init__(self, parent, db, TicketViewOrig, 'TicketManager')
        self.initToolbar()
        self.dialogs = {}
        
    def initlistView(self):
        self.listView.setRootIsDecorated(True)
        fields = ['title', 'author', 'created']
        for field in fields:
            self.listView.addColumn(field)
        self.refreshlistView()
        
    def refreshlistView(self):
        self.listView.clear()
        fields = ['title', 'author', 'created']
        rows = self.manager.get_tickets()
        for row in rows:
            drow = [str(row[field]) for field in fields]
            item = KListViewItem(self.listView, *drow)
            item.ticketid = row.ticketid
                

    def initActions(self):
        collection = self.actionCollection()
        self.newAction = KStdAction.openNew(self.slotNew, collection)

    def initMenus(self):
        menu = KPopupMenu(self)
        self.newAction.plug(menu)
        self.menuBar().insertItem('&Main', menu)
        self.menuBar().insertItem('&Help', self.helpMenu(''))
        
    def initToolbar(self):
        toolbar = self.toolBar()
        actions = [self.newAction]
        for action in actions:
            action.plug(toolbar)
            
    def selectionChanged(self):
        current = self.listView.currentItem()
        if hasattr(current, 'ticketid'):
            self.view.setID(current.ticketid)
        else:
            self.view.setID(None)
        
        
    def slotNew(self):
        dlg = TicketDialog(self)
        self.connect(dlg, SIGNAL('okClicked()'), self.create_ticket)
        self.dialogs['new-ticket'] = dlg
        
    def create_ticket(self):
        dlg = self.dialogs['new-ticket']
        title = str(dlg.titleEdit.text())
        data = str(dlg.dataEdit.text())
        if data:
            self.manager.create_ticket(title, data)
            self.refreshlistView()
        else:
            KMessageBox.error(self, "just a title won't do.")
    


