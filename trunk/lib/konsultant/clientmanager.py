from operator import and_
from xml.dom.minidom import Element, Text

from qt import QListViewItem, QSplitter, QString
from qt import QStringList, QListView, QLabel
from qt import QVariant, QPixmap
from qt import SIGNAL, SLOT, Qt

from qt import QMimeSourceFactory, QGridLayout
from qt import QFrame, QPushButton

from qtsql import QDataTable, QSqlCursor, QSqlFieldInfo
from qtsql import QSqlPropertyMap

from kdecore import KShortcut, KMimeSourceFactory
from kdeui import KDialogBase, KLineEdit, KLed
from kdeui import KTextBrowser, KPopupMenu
from kdeui import KStdAction, KMessageBox
from kdeui import KJanusWidget, KListViewItem
from kdeui import KListView, KStatusBar
from kdeui import KAction, KGuiItem

from paella.base import NoExistError, Error
from paella.sqlgen.clause import Eq, In

from konsultant.base.actions import EditAddresses, ConfigureKonsultant
from konsultant.base.gui import MainWindow
from konsultant.base.gui import ConfigureDialog

from konsultant.base.xmlgen import TextElement, Anchor, TableElement
from konsultant.db import BaseDatabase
from konsultant.db.gui import AddressSelectView, RecordSelector
from konsultant.db.gui import SimpleRecordDialog, AddressSelector
from konsultant.db.gui import WithAddressIdRecDialog, BaseManagerWidget
from konsultant.db.gui import ViewBrowser

from konsultant.db.xmlgen import ClientInfoDoc
        
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
        Element.__init__(self, 'h3')
        self.client = client
        anchor = Anchor('foo.bar.-1', client)
        self.appendChild(anchor)
        
class LocationTableElement(TableElement):
    def __init__(self, db=None):
        cols = ['address', 'isp', 'connection', 'ip', 'static', 'serviced']
        TableElement.__init__(self, cols)
        
class ContactTableElement(TableElement):
    def __init__(self, db=None):
        cols = ['name', 'address', 'email', 'description']
        TableElement.__init__(self, cols)
        
class ClientView(ViewBrowser):
    def __init__(self, db, parent):
        doc = ClientInfoDoc(db)
        ViewBrowser.__init__(self, db, parent, ClientInfoDoc)
        self.dialogs = {}

    def setSource(self, url):
        action, context, id = str(url).split('.')
        #print 'action, context, id', action, context, id, url
        if context == 'contact':
            if action == 'new':
                dlg = ContactDialog(self, self.db)
                dlg.connect(dlg, SIGNAL('okClicked()'), self.insertContact)
                dlg.clientid = self.doc.current
                self.dialogs['new-contact'] = dlg
        elif context == 'location':
            if action == 'new':
                dlg = LocationDialog(self, self.db)
                dlg.connect(dlg, SIGNAL('okClicked()'), self.insertLocation)
                dlg.clientid = self.doc.current
                self.dialogs['new-location'] = dlg
        else:
            KMessageBox.error(self, 'bad call %s' % url)

    def _check_address(self, data):
        addressfields = ['street1', 'street2', 'city', 'state', 'zip']
        a_data = dict([(f, data[f]) for f in addressfields])
        table = 'addresses'
        row = self.db.identifyData('addressid', table, a_data)
        return row.addressid

    def _update_clientinfo(self, cldata):
        table = 'clientinfo'
        row = self.db.identifyData('*', table, cldata)

    def set_client(self, clientid):
        clause = Eq('clientid', clientid)
        self.doc.setID(clientid)
        self.setText(self.doc.toxml())
        
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


class ClientManagerWidget(BaseManagerWidget):
    def __init__(self, parent, db, *args):
        BaseManagerWidget.__init__(self, parent, db, ClientView, 'ClientManager')

    def initActions(self):
        collection = self.actionCollection()
        self.newAction = KStdAction.openNew(self.slotNew, collection)
        self.editaddressAction = EditAddresses(self.slotEditAddresses, collection)
        self.configureAction = ConfigureKonsultant(self.slotConfigure, collection)
        
        print self.editaddressAction

    def initMenus(self):
        mainMenu = KPopupMenu(self)
        self.newAction.plug(mainMenu)
        self.editaddressAction.plug(mainMenu)
        self.configureAction.plug(mainMenu)
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

    def slotConfigure(self):
        ConfigureDialog(self)
    
    def slotNew(self):
        self.testAction('new')

    def slotEditAddresses(self):
        print 'hello'
        AddressSelector(self, self.db)

    def testAction(self, action):
        KMessageBox.error(self, QString('<html>action <b>%s</b> not ready</html>' % action))

    def selectionChanged(self):
        current = self.listView.currentItem()
        if hasattr(current, 'clientid'):
            self.setClientView(current.clientid)
        else:
            self.view.setText('<b>clients</b>')

        
    def setClientView(self, clientid):
        self.view.set_client(clientid)



