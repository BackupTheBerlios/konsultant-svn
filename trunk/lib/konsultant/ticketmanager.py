from qt import SIGNAL, SLOT
from qt import QVBoxLayout, QHBoxLayout, QFrame

from kdeui import KStdAction, KPopupMenu
from kdeui import KListViewItem
from kdeui import KMessageBox

from kdeui import KDialogBase, KLineEdit
from kdeui import KTextEdit

from konsultant.base.gui import MainWindow
from konsultant.db import BaseDatabase
from konsultant.db.gui import BaseManagerWidget, ViewBrowser
from konsultant.db.xmlgen import TicketInfoDoc
from konsultant.db.ticket import TicketManager

TICKETSTATUS = ['new', 'open', 'closed']

class TicketDialog(KDialogBase):
    def __init__(self, parent, name='TicketDialog'):
        KDialogBase.__init__(self, parent, name)
        self.page = QFrame(self)
        self.setMainWidget(self.page)
        self.vbox = QVBoxLayout(self.page, 5, 7)
        self.titleEdit = KLineEdit('new ticket', self.page)
        self.dataEdit = KTextEdit(self.page)
        self.vbox.addWidget(self.titleEdit)
        self.vbox.addWidget(self.dataEdit)
        self.showButtonApply(False)
        self.setButtonOKText('insert', 'insert')
        self.show()
        
class TicketView(ViewBrowser):
    def __init__(self, db, parent):
        ViewBrowser.__init__(self, db, parent, TicketInfoDoc)
        self.dialogs = {}
        self.manager = TicketManager(self.db)

    def setSource(self, url):
        print url
        


class TicketManagerWidget(BaseManagerWidget):
    def __init__(self, parent, db, *args):
        self.db = db
        self.manager = TicketManager(self.db)
        BaseManagerWidget.__init__(self, parent, db, TicketView, 'TicketManager')
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
        print len(rows)
        for row in rows:
            drow = [str(row[field]) for field in fields]
            KListViewItem(self.listView, *drow)
        
                

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
        print current

    def slotNew(self):
        dlg = TicketDialog(self)
        self.connect(dlg, SIGNAL('okClicked()'), self.create_ticket)
        self.dialogs['new-ticket'] = dlg
        
    def create_ticket(self):
        dlg = self.dialogs['new-ticket']
        title = str(dlg.titleEdit.text())
        data = str(dlg.dataEdit.text())
        self.manager.create_ticket(title, data)
        self.refreshlistView()
    
