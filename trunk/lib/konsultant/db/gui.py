from qt import SIGNAL, SLOT
from qt import QMimeSourceFactory, QSplitter
from qt import QGridLayout
from qt import QFrame, QPushButton
from qt import QLabel
from qt import Qt
#from qtsql import QDataTable, QSqlCursor, QSqlFieldInfo
#from qtsql import QSqlPropertyMap

from kdeui import KDialogBase, KLineEdit
from kdeui import KMainWindow, KTextBrowser
#from kdeui import KStdAction, KMessageBox
from kdeui import KListViewItem
from kdeui import KListView, KStdGuiItem
from kdeui import KPushButton

from paella.base import NoExistError
from paella.sqlgen.clause import Eq, In

#from konsultant.maindb import BaseDatabase
#from konsultant.gui import MainWindow
#from konsultant.xmlgen import TextElement, Anchor, TableElement
from konsultant.base.gui import SimpleRecord, SimpleRecordDialog
from konsultant.db.xmlgen import AddressSelectDoc, AddressLink

class RecordSelector(QSplitter):
    def __init__(self, parent, db, table, fields, idcol, groupfield, view, name='RecordSelector'):
        QSplitter.__init__(self, parent, name)
        self.db = db
        self.table = table
        self.fields = fields
        self.idcol = idcol
        self.groupfield = groupfield
        self.listView = KListView(self)
        self.vsplit = QSplitter(self)
        self.vsplit.setOrientation(Qt.Vertical)
        self.recView = view(db, self.vsplit)
        frame = QFrame(self.vsplit)
        #self.recForm = SimpleRecord(self.vsplit, ['a', 'b', 'c'])
        self.recForm = SimpleRecord(frame, fields)
        self.connect(self.listView, SIGNAL('selectionChanged()'), self.groupChanged)
        self.initlistView()
        self.setSource(self.handleURL)
    
    def initlistView(self):
        self.listView.addColumn('group')
        self.listView.setRootIsDecorated(True)
        all = KListViewItem(self.listView, 'all')
        groups = KListViewItem(self.listView, self.groupfield)
        q = self.db.qselect(fields=['distinct %s' % self.groupfield], table=self.table)
        while q.next():
            KListViewItem(groups, q.value(0).toString())
            

    def groupChanged(self):
        self.current = self.listView.currentItem().text(0)
        self.setRecView(self.current)
        
    def setRecView(self, current):
        if current == 'all':
            clause=None
        else:
            clause = Eq(self.groupfield, current)
        self.recView.set_clause(clause)

    def handleURL(self, url):
        action, obj, ident = str(url).split('.')
        row = self.db.mcursor.select_row(fields=self.fields,
                                         table=self.table, clause=Eq(self.idcol, ident))
        entries = self.recForm.entries
        for field in entries:
            entries[field].setText(row[field])

    def setSource(self, handler):
        self.recView.setSource = handler
        
        

#db is BaseDatabase from konsultant.maindb
#doc is Element from xml.dom.minidom
class ViewBrowser(KTextBrowser):
    def __init__(self, db, parent, doc):
        KTextBrowser.__init__(self, parent)
        self.setMimeSourceFactory()
        self.db = db
        self.doc = doc
        self.setNotifyClick(True)
        

    def setMimeSourceFactory(self, factory=None):
        if factory is None:
            self.mimes = QMimeSourceFactory()
            self.mimes.addFilePath('/usr/share/wallpapers')
        else:
            self.mimes = factory
        KTextBrowser.setMimeSourceFactory(self, self.mimes)

    def set_clause(self, clause):
        self.doc.set_clause(clause)
        self.setText(self.doc.toxml())
        
class AddressSelectView(ViewBrowser):
    def __init__(self, db, parent):
        doc = AddressSelectDoc(db)
        ViewBrowser.__init__(self, db, parent, doc)

    def set_city(self, city):
        clause = Eq('city', city)
        self.set_clause(clause)
        
class AddressRecord(SimpleRecord):
    def __init__(self, parent, name='AddressRecord'):
        fields = ['street1', 'street2', 'city', 'state', 'zip']
        text = 'insert a new address'
        SimpleRecord.__init__(self, parent, fields, text, name)
        
class WithAddressIdRecord(SimpleRecord):
    def _setupfields(self, parent):
        for f in range(len(self.fields)):
            if self.fields[f] == 'addressid':
                self.selButton = KPushButton('select/create', parent)
                self.addWidget(self.selButton, f + 1, 1)
                label = QLabel(entry, 'address', parent, self.fields[f])
                self.addWidget(label, f + 1, 0)
            else:
                entry = KLineEdit('', parent)
                self.entries[self.fields[f]] = entry
                self.addWidget(entry, f + 1, 1)
                label = QLabel(entry, self.fields[f], parent, self.fields[f])
                self.addWidget(label, f + 1, 0)
        
class WithAddressIdRecDialog(KDialogBase):
    def __init__(self, parent, db, fields, name='WithAddressIdRecDialog'):
        KDialogBase.__init__(self, parent, name)
        self.db = db
        self.page = QFrame(self)
        self.setMainWidget(self.page)
        text = 'this is a <em>simple</em> record dialog'
        self.grid = WithAddressIdRecord(self.page, fields, text, name=name)
        self.connect(self.grid.selButton, SIGNAL('clicked()'), self.selButtonClicked)
        self.showButtonApply(False)
        self.setButtonOKText('insert', 'insert')
        self.enableButtonOK(False)
        self.dialogs = {}
        self.show()
        
    def selButtonClicked(self):
        dlg = AddressSelector(self, self.db)
        dlg.setSource(self.addressidSelected)
        self.dialogs['address'] = dlg

    def addressidSelected(self, url):
        addressid = int(str(url).split('.')[2])
        self.enableButtonOK(True)
        self.dialogs['address'].done(0)
        self.grid.selButton.close()
        n = self.grid.fields.index('addressid') + 1
        text = AddressLink(self.db, addressid).toxml()
        lbl = QLabel(text, self.page)
        lbl.show()
        self.grid.addMultiCellWidget(lbl, n, n, 1, 1)
        self.addressid = addressid
        
class AddressSelector(KDialogBase):
    def __init__(self, parent, db, name='AddressSelector'):
        KDialogBase.__init__(self, parent, name)
        self.db = db
        self.fields = ['street1', 'street2', 'city', 'state', 'zip']
        self.mainView = RecordSelector(self, self.db, 'addresses', self.fields,
                                       'addressid', 'city', AddressSelectView, name=name)
        self.setMainWidget(self.mainView)
        self.showButtonApply(False)
        self.showButtonOK(False)
        self.show()

    def handleURL(self, url):
        action, obj, ident = str(url).split('.')
        self.selected_id = ident
        print self.selected_id

    def setSource(self, handler):
        self.mainView.setSource(handler)
        

