from operator import and_
from xml.dom.minidom import Element, Text

from qt import QListViewItem, QSplitter, QString
from qt import QStringList, QListView, QLabel
from qt import QVariant, QPopupMenu, QPixmap
from qt import SIGNAL, SLOT

from qt import QMimeSourceFactory, QGridLayout
from qt import QFrame, QPushButton

from qtsql import QDataTable, QSqlCursor, QSqlFieldInfo
from qtsql import QSqlPropertyMap

from kdecore import KShortcut, KMimeSourceFactory
from kdeui import KDialogBase, KLineEdit
from kdeui import KMainWindow, KTextBrowser
from kdeui import KStdAction, KMessageBox
from kdeui import KJanusWidget, KListViewItem
from kdeui import KListView
from kdeui import KAction, KGuiItem

from paella.base import NoExistError, Error
from paella.sqlgen.clause import Eq, In

from konsultant.base.gui import MainWindow
from konsultant.base.xmlgen import TextElement, Anchor, TableElement
from konsultant.db import BaseDatabase
from konsultant.db.gui import AddressSelectView, RecordSelector
from konsultant.db.gui import SimpleRecordDialog, AddressSelector
from konsultant.db.gui import WithAddressIdRecDialog

from konsultant.db.xmlgen import ClientInfoDoc

class EditAddressesItem(KGuiItem):
    def __init__(self):
        text = QString('Edit addresses')
        icon = QString('edit')
        ttip = QString('Edit addresses')
        wtf = QString('edit or browse addresses')
        KGuiItem.__init__(self, text, icon, ttip, wtf)
        
class EditAddresses(KAction):
    def __init__(self, slot, parent):
        item = EditAddressesItem()
        name = 'EditAddresses'
        cut = KShortcut()
        KAction.__init__(self, item, cut, slot, parent, name)
        
class ClientCursor(QSqlCursor):
    def __init__(self, db):
        QSqlCursor.__init__(self, 'clients', True, db)
        self.append(QSqlFieldInfo('clientid'))
        
class ClientsTable(QDataTable):
    def __init__(self, db, cursor, autoPopulate=False, parent=None):
        QDataTable.__init__(self, cursor)
        self.propMap = QSqlPropertyMap()
        self.installPropertyMap(self.propMap)
        self.setSort(QStringList('client'))
        self.addColumn('client', 'Client')
        self.refresh()

class ClientHeaderElement(Element):
    def __init__(self, client):
        print client
        Element.__init__(self, 'h3')
        self.client = client
        anchor = Anchor('foo.bar.-1', client)
        headerd = Text()
        headerd.data = '%s:' % self.client
        #anchor.appendChild(headerd)
        self.appendChild(anchor)
        
class LocationTableElement(TableElement):
    def __init__(self, db=None):
        cols = ['address', 'isp', 'connection', 'ip', 'static', 'serviced']
        TableElement.__init__(self, cols)
        
class ContactTableElement(TableElement):
    def __init__(self, db=None):
        cols = ['name', 'address', 'email', 'description']
        TableElement.__init__(self, cols)
        
class ClientView(KTextBrowser):
    def __init__(self, db, parent):
        KTextBrowser.__init__(self, parent)
        self.mimes = QMimeSourceFactory()
        self.mimes.addFilePath('/usr/share/wallpapers')
        self.setMimeSourceFactory(self.mimes)
        self.db = db
        #self.info = ClientInfoElement()
        self.info = ClientInfoDoc(self.db)
        self.setNotifyClick(True)
        self.setText('<html><h1>Hello There</h1></html>')
        self.dialogs = {}

    def set_client(self, clientid):
        self.info.set_client(clientid)
        self.setText(self.info.toxml())
        
    def setSource(self, url):
        action, context, id = str(url).split('.')
        print 'action, context, id', action, context, id, url
        if context == 'contact':
            if action == 'new':
                dlg = ContactDialog(self, self.db)
                dlg.connect(dlg, SIGNAL('okClicked()'), self.insertContact)
                dlg.clientid = self.info.current
                self.dialogs['new-contact'] = dlg
        elif context == 'location':
            if action == 'new':
                dlg = LocationDialog(self, self.db)
                dlg.connect(dlg, SIGNAL('okClicked()'), self.insertLocation)
                dlg.clientid = self.info.current
                self.dialogs['new-location'] = dlg
        else:
            raise Error, 'bad call %s' % url

    def _check_address(self, data):
        addressfields = ['street1', 'street2', 'city', 'state', 'zip']
        a_data = dict([(f, data[f]) for f in addressfields])
        table = 'addresses'
        row = self.db.identifyData('addressid', table, a_data)
        return row.addressid

    def _update_clientinfo(self, cldata):
        table = 'clientinfo'
        row = self.db.identifyData('*', table, cldata)
        
    def insertContact(self):
        dlg = self.dialogs['new-contact']
        data = dict([(k,v.text()) for k,v in dlg.grid.entries.items()])
        contactfields = ['name', 'email', 'description']
        c_data = dict([(f, data[f]) for f in contactfields])
        data['clientid'] = dlg.clientid
        addressid = dlg.addressid

        c_data['addressid'] = addressid
        table = 'contacts'
        row = self.db.identifyData('contactid', table, c_data)
        contactid = row.contactid

        cldata = {'clientid' : dlg.clientid, 'contactid' : contactid}
        self._update_clientinfo(cldata)
        self.set_client(dlg.clientid)

    def insertLocation(self):
        dlg = self.dialogs['new-location']
        data = dict([(k,v.text()) for k,v in dlg.grid.entries.items()])
        locfields = ['isp', 'connection', 'ip', 'static', 'serviced']
        ldata = dict([(f, data[f]) for f in locfields])
        addressid = dlg.addressid

        ldata['addressid'] = addressid
        row = self.db.identifyData('locationid', 'locations', ldata)
        locationid = row.locationid

        cldata = {'clientid' : dlg.clientid, 'locationid' : locationid}
        self._update_clientinfo(cldata)
        self.set_client(dlg.clientid)

class ContactDialog(WithAddressIdRecDialog):
    def __init__(self, parent, db, name='ContactDialog'):
        fields = ['name', 'addressid', 'email', 'description']
        WithAddressIdRecDialog.__init__(self, parent, db, fields, name=name)
        
class LocationDialog(WithAddressIdRecDialog):
    def __init__(self, parent, db, name='LocationDialog'):
        fields = ['addressid', 'isp', 'connection',
                  'ip', 'static', 'serviced']
        WithAddressIdRecDialog.__init__(self, parent, db, fields, name=name)

class ClientManager(KMainWindow):
    def __init__(self, *args):
        KMainWindow.__init__(self, *args)
        self.db = BaseDatabase('ClientManager', self)
        self.db.open()
        cursor = ClientCursor(self.db)
        self.setGeometry (0, 0, 600, 400)
        self.mainView = QSplitter(self, 'main view')
        self.listView = ClientsTable(self.db, cursor, False)
        self.listView = KListView(self.mainView)
        self.cview = ClientView(self.db, self.mainView)
        self.setCentralWidget (self.mainView)
        self.initlistView()
        self.initActions()
        self.initMenus()
        self.connect(self.listView, SIGNAL('selectionChanged()'), self.clientChanged)
        self.show()

    def initActions(self):
        collection = self.actionCollection()
        self.newAction = KStdAction.openNew(self.slotNew, collection)
        self.editaddressAction = EditAddresses(self.slotEditAddresses, collection)
        print self.editaddressAction

    def initMenus(self):
        mainMenu = QPopupMenu(self)
        self.newAction.plug(mainMenu)
        self.editaddressAction.plug(mainMenu)
        self.menuBar().insertItem('&Main', mainMenu)
        self.menuBar().insertItem('&Help', self.helpMenu(''))

    def initlistView(self):
        self.listView.addColumn('client')
        self.listView.setRootIsDecorated(True)
        clients = KListViewItem(self.listView, 'clients')
        rows = self.db.mcursor.select(fields=['clientid', 'client'], table='clients')
        for row in rows:
            c = KListViewItem(clients, row['client'])
            c.clientid = row.clientid

    def slotNew(self):
        self.testAction('new')

    def slotEditAddresses(self):
        print 'hello'
        AddressSelector(self, self.db)

    def testAction(self, action):
        KMessageBox.error(self, QString('<html>action <b>%s</b> not ready</html>' % action))

    def clientChanged(self):
        self.current = self.listView.currentItem().clientid
        self.setClientView(self.current)

    def setClientView(self, clientid):
        row = self.db.select_row(fields=['clientid'], table='clients', clause=Eq('clientid', clientid))
        self.cview.set_client(row.clientid)



