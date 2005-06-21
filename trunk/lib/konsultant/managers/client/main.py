from operator import and_
from xml.dom.minidom import Element, Text

from qt import QListViewItem, QSplitter, QString
from qt import QStringList, QListView, QLabel
from qt import QVariant, QPixmap
from qt import QSize
from qt import SIGNAL, SLOT, Qt
from qt import PYSIGNAL

from qt import QMimeSourceFactory, QGridLayout
from qt import QFrame, QPushButton
from qt import QStyleSheet, QStyleSheetItem

from qtsql import QDataTable, QSqlCursor, QSqlFieldInfo
from qtsql import QSqlPropertyMap

from kdecore import KShortcut, KMimeSourceFactory
from kdeui import KDialogBase, KLineEdit, KLed
from kdeui import KTextBrowser, KPopupMenu
from kdeui import KStdAction, KMessageBox
from kdeui import KJanusWidget, KListViewItem
from kdeui import KListView, KStatusBar
from kdeui import KAction, KGuiItem

from useless.base import NoExistError, Error
from useless.kbase.refdata import RefData
from useless.sqlgen.clause import Eq, In
from useless.kbase.gui import MainWindow
from useless.db.record import EmptyRefRecord
from useless.xmlgen.base import TextElement, Anchor, TableElement
from useless.kdb import BaseDatabase
from useless.kdb.gui import BaseManagerWidget, RecordSelector
from useless.kdb.gui import ViewBrowser, SimpleRecordDialog
from useless.kdb.admin import AdminWidget
from useless.kbase.actions import AdministerDatabase

from konsultant.base.actions import EditAddresses, ConfigureKonsultant
from konsultant.base.actions import ManageTickets
from konsultant.base.actions import ManageTasks
from konsultant.base.gui import ConfigureDialog

from konsultant.db.gui import AddressSelectView, AddressSelector
from konsultant.db.xmlgen import AddressLink
from konsultant.managers.ticket import TicketManagerWidget

from xmlgen import ClientInfoDoc
from contact import ContactEditorWin
from location import LocationEditorWin
from tagedit import ClientTagEditorWin
from db import ClientManager
from gui import ClientDialog, ContactDialog, LocationDialog
from gui import ClientEditDialog

class AddressData(RefData):
    def __init__(self):
        RefData.__init__(self, dict(address='addressid'))
        
class ClientStyleSheet(QStyleSheet):
    def __init__(self, parent=None, name='ClientStyleSheet'):
        QStyleSheet.__init__(self, parent, name)
        
class ClientView(ViewBrowser):
    def __init__(self, app, parent):
        doc = ClientInfoDoc(app)
        ViewBrowser.__init__(self, app, parent, ClientInfoDoc)
        self.dialogs = {}
        self.manager = ClientManager(self.app)
        self.resize(600, 800)
        
    def setSource(self, url):
        action, context, id = str(url).split('.')
        if context == 'contact':
            if action == 'new':
                dlg = ContactDialog(self.app, self)
                dlg.connect(dlg, SIGNAL('okClicked()'), self.insertContact)
                dlg.clientid = self.doc.current
                self.dialogs['new-contact'] = dlg
            elif action == 'edit':
                dlg = ContactEditorWin(self.app, self, self.doc.records['contacts'])
                self.connect(dlg, PYSIGNAL('updated()'), self.set_client)
        elif context == 'location':
            if action == 'new':
                dlg = LocationDialog(self.app, self)
                dlg.connect(dlg, SIGNAL('okClicked()'), self.insertLocation)
                dlg.clientid = self.doc.current
                self.dialogs['new-location'] = dlg
            elif action == 'edit':
                dlg = LocationEditorWin(self.app, self, self.doc.records['locations'])
                self.connect(dlg, PYSIGNAL('updated()'), self.set_client)
        elif context == 'client':
            print url
            if action == 'edit':
                record = dict(client=self.doc.records['client'],
                              clientid=self.doc.current)
                print record, 'record'
                dlg = ClientEditDialog(self.app, self, record)
                dlg.connect(dlg, SIGNAL('okClicked()'), self.updateClient)
                dlg.connect(dlg, PYSIGNAL('updated()'), self.set_client)
                self.dialogs['edit-client'] = dlg
        elif context == 'tags':
            clientid = int(id)
            ClientTagEditorWin(self.app, self, int(id))
        else:
            KMessageBox.error(self, 'bad call %s' % url)

    def set_client(self, clientid=None):
        if clientid is None:
            clientid = self.doc.current
        clause = Eq('clientid', clientid)
        self.doc.setID(clientid)
        self.setText(self.doc.toxml())
        
    def insertContact(self):
        dlg = self.dialogs['new-contact']
        data = dlg.grid.getRecordData()
        contactid = self.manager.insertContact(dlg.clientid, dlg.addressid, data)
        self.set_client(dlg.clientid)

    def insertLocation(self):
        dlg = self.dialogs['new-location']
        data = dlg.grid.getRecordData()
        locationid = self.manager.insertLocation(dlg.clientid, dlg.addressid, data)
        self.set_client(dlg.clientid)

    def updateClient(self):
        dlg = self.dialogs['edit-client']
        data = dlg.grid.getRecordData()
        clientid = dlg.clientid
        self.manager.updateClient(clientid, data['client'])
        self.set_client(clientid)
        
class ClientManagerWidget(BaseManagerWidget):
    def __init__(self, app, parent, *args):
        BaseManagerWidget.__init__(self, app, parent, ClientView, 'ClientManager')
        self.setCaption('ClientManager')
        self.cfg = self.app.cfg
        self.cfg.setGroup('client-gui')
        size = self.cfg.readEntry('mainwinsize')
        w, h = [int(x.strip()) for x in str(size).split(',')]
        #self.resize(QSize(w, h))
        self.dialogs  = {}
        self.manager = ClientManager(self.app)
        self.resize(w, h)
        self.initlistView()
        
    def initActions(self):
        collection = self.actionCollection()
        self.newAction = KStdAction.openNew(self.slotNew, collection)
        self.editaddressAction = EditAddresses(self.slotEditAddresses, collection)
        self.configureAction = ConfigureKonsultant(self.slotConfigure, collection)
        self.manageTicketsAction = ManageTickets(self.slotManageTickets, collection)
        self.manageTasksAction = ManageTasks(self.slotManageTasks, collection)
        self.admindbAction = AdministerDatabase(self.slotAdministerDatabase,
                                                collection)
        BaseManagerWidget.initActions(self, collection=collection)
        
    def initMenus(self):
        mainMenu = KPopupMenu(self)
        self.newAction.plug(mainMenu)
        self.manageTicketsAction.plug(mainMenu)
        self.manageTasksAction.plug(mainMenu)
        self.editaddressAction.plug(mainMenu)
        self.admindbAction.plug(mainMenu)
        self.configureAction.plug(mainMenu)
        BaseManagerWidget.initMenus(self, mainmenu=mainMenu)
        
    def initlistView(self):
        self.listView.addColumn('client')
        self.listView.setRootIsDecorated(True)
        self.refreshlistView()
        
    def initToolbar(self):
        toolbar = self.toolBar()
        actions = [self.newAction, self.manageTicketsAction,
                   self.manageTasksAction,
                   self.editaddressAction, self.admindbAction,
                   self.configureAction, self.quitAction]
        for action in actions:
            action.plug(toolbar)
        
    def refreshlistView(self):
        self.listView.clear()
        clients = KListViewItem(self.listView, 'clients')
        rows = self.db.mcursor.select(fields=['clientid', 'client'], table='clients')
        for row in rows:
            c = KListViewItem(clients, row['client'])
            c.clientid = row.clientid

    def slotConfigure(self):
        ConfigureDialog(self.app, self)
    
    def slotNew(self):
        dlg = ClientDialog(self.app, self)
        dlg.connect(dlg, SIGNAL('okClicked()'), self.insertClientok)
        self.dialogs['new-client'] = dlg
        
    def slotEditAddresses(self):
        AddressSelector(self.app, self)

    def slotAdministerDatabase(self):
        AdminWidget(self.app, self)
        
    def testAction(self, action):
        KMessageBox.error(self, QString('<html>action <b>%s</b> not ready</html>' % action))

    def selectionChanged(self):
        current = self.listView.currentItem()
        if hasattr(current, 'clientid'):
            self.setClientView(current.clientid)
        else:
            self.view.setText('<b>clients</b>')


    def insertClientok(self):
        dlg = self.dialogs['new-client']
        data = dict([(k,v.text()) for k,v in dlg.grid.entries.items()])
        client = str(dlg.grid.getRecordData()['client'])
        clientid = self.manager.insertClient(client)
        self.setClientView(clientid)
        self.refreshlistView()
        
    def setClientView(self, clientid):
        self.view.set_client(clientid)


    def slotManageTickets(self):
        TicketManagerWidget(self.app, self, self.db)

    def slotManageTasks(self):
        print 'Manage Tasks'
        
