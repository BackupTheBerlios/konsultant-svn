from operator import and_
from xml.dom.minidom import Element, Text

from qt import QListViewItem, QSplitter, QString
from qt import QStringList, QListView, QLabel
from qt import QVariant, QPixmap
from qt import QSize
from qt import SIGNAL, SLOT, Qt

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

from konsultant.base import NoExistError, Error
from konsultant.sqlgen.clause import Eq, In
from konsultant.base.actions import EditAddresses, ConfigureKonsultant
from konsultant.base.actions import ManageTickets, AdministerDatabase
from konsultant.base.gui import MainWindow
from konsultant.base.gui import ConfigureDialog

from konsultant.base.xmlgen import TextElement, Anchor, TableElement
from konsultant.db import BaseDatabase
from konsultant.db.gui import AddressSelectView, RecordSelector
from konsultant.db.gui import SimpleRecordDialog, AddressSelector
from konsultant.db.gui import WithAddressIdRecDialog, BaseManagerWidget
from konsultant.db.gui import ViewBrowser
from konsultant.db.admin import AdminWidget

from konsultant.managers.ticket import TicketManagerWidget

from xmlgen import ClientInfoDoc
from contact import ContactEditorWin
from location import LocationEditorWin
from db import ClientManager

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
                dlg = ContactDialog(self, self.db)
                dlg.connect(dlg, SIGNAL('okClicked()'), self.insertContact)
                dlg.clientid = self.doc.current
                self.dialogs['new-contact'] = dlg
            elif action == 'edit':
                ContactEditorWin(self, self.app, self.doc.records['contacts'])
        elif context == 'location':
            if action == 'new':
                dlg = LocationDialog(self, self.db)
                dlg.connect(dlg, SIGNAL('okClicked()'), self.insertLocation)
                dlg.clientid = self.doc.current
                self.dialogs['new-location'] = dlg
            elif action == 'edit':
                LocationEditorWin(self, self.app, self.doc.records['locations'])
        else:
            KMessageBox.error(self, 'bad call %s' % url)

    def set_client(self, clientid):
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

class ClientDialog(SimpleRecordDialog):
    def __init__(self, parent, db, name='ClientDialog'):
        fields = ['client']
        SimpleRecordDialog.__init__(self, parent, fields, name='ClientDialog')
        
class ContactDialog(WithAddressIdRecDialog):
    def __init__(self, parent, db, name='ContactDialog'):
        fields = ['name', 'addressid', 'email', 'description']
        WithAddressIdRecDialog.__init__(self, parent, db, fields, name=name)
        
class LocationDialog(WithAddressIdRecDialog):
    def __init__(self, parent, db, name='LocationDialog'):
        fields = ['name', 'addressid', 'isp', 'connection',
                  'ip', 'static', 'serviced']
        WithAddressIdRecDialog.__init__(self, parent, db, fields, name=name)


class ClientManagerWidget(BaseManagerWidget):
    def __init__(self, parent, app, *args):
        BaseManagerWidget.__init__(self, parent, app, ClientView, 'ClientManager')
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
        self.admindbAction = AdministerDatabase(self.slotAdministerDatabase,
                                                collection)
        BaseManagerWidget.initActions(self, collection=collection)
        
    def initMenus(self):
        mainMenu = KPopupMenu(self)
        self.newAction.plug(mainMenu)
        self.manageTicketsAction.plug(mainMenu)
        self.editaddressAction.plug(mainMenu)
        self.admindbAction.plug(mainMenu)
        BaseManagerWidget.initMenus(self, mainmenu=mainMenu)
        
    def initlistView(self):
        self.listView.addColumn('client')
        self.listView.setRootIsDecorated(True)
        self.refreshlistView()
        
    def initToolbar(self):
        toolbar = self.toolBar()
        actions = [self.newAction, self.manageTicketsAction,
                   self.editaddressAction, self.admindbAction, self.quitAction]
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
        ConfigureDialog(self)
    
    def slotNew(self):
        dlg = ClientDialog(self, self.db)
        dlg.connect(dlg, SIGNAL('okClicked()'), self.insertClientok)
        self.dialogs['new-client'] = dlg
        
    def slotEditAddresses(self):
        AddressSelector(self, self.app)

    def slotAdministerDatabase(self):
        AdminWidget(self, self.app)
        
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
        TicketManagerWidget(self, self.app, self.db)
