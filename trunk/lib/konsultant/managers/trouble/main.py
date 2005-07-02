from qt import SIGNAL, SLOT
from qt import QVBoxLayout, QHBoxLayout, QFrame
from qt import QListBoxItem, QListBoxText

from kdeui import KStdAction, KPopupMenu
from kdeui import KListViewItem
from kdeui import KMessageBox, KActionSelector

from kdeui import KDialogBase, KLineEdit
from kdeui import KTextEdit, KMainWindow
from kdeui import KComboBox

from useless.kbase.gui import MainWindow
from useless.kdb import BaseDatabase
from useless.kdb.gui import BaseManagerWidget, ViewBrowser

from useless.sqlgen.clause import Eq, In, NotIn
from useless.sqlgen.clause import Neq
#from xmlgen import TicketInfoDoc
#from xmlgen import TicketDocument
from xmlgen import TroubleDocument
from xmlgen import TroubleInfoDoc
from db import TroubleManager

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
        self.actionEdit = KLineEdit('', self.page)
        self.statusEdit = KComboBox(self.page)
        self.workdoneEdit = KTextEdit(self.page)
        self.vbox.addWidget(self.actionEdit)
        self.vbox.addWidget(self.statusEdit)
        self.vbox.addWidget(self.workdoneEdit)
        self.showButtonApply(False)
        self.setButtonOKText('insert', 'insert')
        self.show()

class TicketAssigner(VboxDialog):
    def __init__(self, app, parent, ticketid):
        KMainWindow.__init__(self, parent, 'TicketAssigner')
        self.resize(400, 300)
        self.listBox = KActionSelector(self)
        self.listBox.setShowUpDownButtons(False)
        self.setMainWidget(self.listBox)
        self.app = app
        self.db = app.db
        self.manager = TicketManager(self.app)
        self.ticketid = ticketid
        self.initlistView()
        self.show()
        self.connect(self, SIGNAL('okClicked()'), self.update_clients)
        
    def initlistView(self):
        rows = self.manager.get_clients(self.ticketid, assigned=False)
        ubox = self.listBox.availableListBox()
        abox = self.listBox.selectedListBox()
        for row in rows:
            if row.assigned:
                c = QListBoxText(abox, row.client)
            else:
                c = QListBoxText(ubox, row.client)
            c.clientid = row.clientid
        #lbox.show()

    def update_clients(self):
        print 'updating clients'
        ubox = self.listBox.availableListBox()
        abox = self.listBox.selectedListBox()
        ids = [abox.item(a).clientid for a in range(abox.numRows())]
        self.manager.update_ticket_assignment(self.ticketid, ids)
        
        
class TroubleActionView(ViewBrowser):
    def __init__(self, app, parent, troubleid):
        ViewBrowser.__init__(self, app, parent, TroubleInfoDoc)
        self.dialogs = {}
        self.manager = TroubleManager(self.app)

    def setSource(self, url):
        action, context, id = str(url).split('.')
        print action, context, id
        if context == 'action':
            if action == 'new':
                dlg = ActionDialog(self, 'ActionDialog')
                dlg.connect(dlg, SIGNAL('okClicked()'), self.insertAction)
                dlg.troubleid = self.doc.current
                statustypes = [r.status for r in self.manager.db.select(table='trouble_status')]
                for idx in range(len(statustypes)):
                    dlg.statusEdit.setCurrentItem(statustypes[idx], True, idx)
                status = self.manager.getTroubleStatus(self.doc.current)
                dlg.statusEdit.setCurrentItem(status)
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
        elif context == 'ticket':
            if action == 'assign':
                print 'assign in TicketActionView'
                TicketAssigner(self.app, self, id)
                
    def setID(self, troubleid):
        self.current = troubleid
        self.doc.setID(troubleid)
        self.setText(self.doc.toxml())

    def insertAction(self):
        dlg = self.dialogs['new-action']
        action = str(dlg.actionEdit.text())
        status = str(dlg.statusEdit.currentText())
        workdone = str(dlg.workdoneEdit.text())
        troubleid = dlg.troubleid
        self.manager.updateTrouble(troubleid, action, workdone, status)
        self.setID(troubleid)
        
        
        
class TroubleView(ViewBrowser):
    def __init__(self, app, parent):
        ViewBrowser.__init__(self, app, parent, TroubleDocument)
        self.dialogs = {}
        self.manager = TroubleManager(self.app)

    def setID(self, troubleid=None, clause=None):
        self.doc.setID(clause=clause)
        self.setText(self.doc.toxml())

    def insertAction(self):
        raise Error, "don't call me yet"
        
    def setSource(self, url):
        action, context, id = str(url).split('.')
        id = int(id)
        print action, context, id
        if context == 'trouble':
            if action == 'show':
                print 'showing ticket %d' % id
                win = KMainWindow(self)
                v = TroubleActionView(self.app, win, id)
                v.setID(id)
                v.resize(700, 900)
                win.setCentralWidget(v)
                win.setCaption('TroubleView')
                win.resize(700, 900)
                win.show()
            elif action == 'assign':
                print 'need to assign ticket'
                TicketAssigner(self.app, self, id)
                
class TroubleManagerWidget(BaseManagerWidget):
    def __init__(self, app, parent, *args):
        BaseManagerWidget.__init__(self, app, parent, TroubleView, 'TroubleManager')
        self.setCaption('TroubleManager')
        self.manager = TroubleManager(self.app)
        self.dialogs = {}
        print 'trouble app', app, self.app
        self.resize(400, 600)
        
    def initActions(self):
        collection = self.actionCollection()
        self.newAction = KStdAction.openNew(self.slotNew, collection)
        self.quitAction = KStdAction.quit(self.close, collection)
        
    def initMenus(self):
        menu = KPopupMenu(self)
        self.newAction.plug(menu)
        self.quitAction.plug(menu)
        self.menuBar().insertItem('&Main', menu)
        self.menuBar().insertItem('&Help', self.helpMenu(''))

    def initlistView(self):
        self.listView.setRootIsDecorated(True)
        self.listView.addColumn('trouble group')
        self.refreshlistView()

    def initToolbar(self):
        toolbar = self.toolBar()
        actions = [self.newAction, self.quitAction]
        for action in actions:
            action.plug(toolbar)
            
    def refreshlistView(self):
        self.listView.clear()
        all = KListViewItem(self.listView, 'all')
        status = KListViewItem(self.listView, 'status')
        rows = self.db.select(table='trouble_status')
        for row in rows:
            s = KListViewItem(status, row.status)
            s.status = row.status
        client = KListViewItem(self.listView, 'client')
        sel = self.db.stmt.select(fields=['clientid'], table='troubles',
                             clause=Neq('status', 'done'))
        clause = In('clientid', sel)
        rows = self.db.select(fields=['clientid', 'client'], table='clients',
                              clause=clause)
        for row in rows:
            c = KListViewItem(client, row.client)
            c.clientid = row.clientid
        untouched = KListViewItem(self.listView, 'untouched')
        
    def slotNew(self, title='', data=''):
        dlg = TroubleDialog(self)
        dlg.titleEdit.setText(title)
        dlg.dataEdit.setText(data)
        self.connect(dlg, SIGNAL('okClicked()'), self.create_ticket)
        self.dialogs['new-trouble'] = dlg

    def create_trouble(self):
        dlg = self.dialogs['new-trouble']
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
        if hasattr(current, 'troubleid'):
            self.view.setID(current.troubleid)
        elif hasattr(current, 'clientid'):
            clientid = current.clientid
            self.view.setID(clause=Eq('clientid', clientid))
        elif hasattr(current, 'status'):
            self.view.setID(clause=Eq('status', current.status))
        elif str(current.text(0)) == 'all':
            self.view.setID(None)
        elif str(current.text(0)) == 'untouched':
            print 'hey hey hey, untouched'
            self.view.setID(clause=Eq('status', 'untouched'))
            
            
