from qt import SIGNAL, SLOT, Qt
from qt import QMimeSourceFactory, QSplitter
from qt import QGridLayout
from qt import QFrame, QPushButton
from qt import QLabel, QString

from kdeui import KDialogBase, KLineEdit
from kdeui import KMainWindow, KTextBrowser
from kdeui import KStdAction, KMessageBox
from kdeui import KListViewItem
from kdeui import KListView, KStdGuiItem
from kdeui import KPushButton, KStatusBar

from konsultant.base import NoExistError
from konsultant.sqlgen.clause import Eq, In

from konsultant.base.gui import MainWindow, MimeSources
from konsultant.base.gui import SimpleRecord, SimpleRecordDialog
from konsultant.db.xmlgen import AddressSelectDoc, AddressLink

class BaseManagerWidget(MainWindow):
    def __init__(self, parent, app, view, name):
        MainWindow.__init__(self, parent, name)
        self.app = app
        self.db = app.db
        self.mainView = QSplitter(self, 'main view')
        self.listView = KListView(self.mainView)
        #view is some sort of display widget that requires db
        self.view = view(self.app, self.mainView)
        self.setCentralWidget(self.mainView)
        self.initlistView()
        self.initActions()
        self.initMenus()
        self.connect(self.listView,
                     SIGNAL('selectionChanged()'), self.selectionChanged)
        self.statusbar = KStatusBar(self, 'statusbar')
        self.statusbar.insertItem(QString('status'), 0, False)
        self.show()
        
    def initMenus(self):
        mainmenu = QPopupMenu(self)
        
class EditableRecord(QGridLayout):
    def __init__(self, parent, fields, text=None, name='EditableRecord'):
        QGridLayout.__init__(self, parent, len(fields) + 2, 2, 1, -1, name)
        self.fields = fields
        self.entries = {}
        self._setupfields(parent)
        self.setSpacing(7)
        self.setMargin(10)
        self.addMultiCellWidget(QLabel(text, parent), 0, 0, 0, 1)

    def _setupfields(self, parent):
        for f in range(len(self.fields)):
            entry = KLineEdit('', parent)
            self.entries[self.fields[f]] = entry
            self.addWidget(entry, f + 1, 1)
            label = QLabel(entry, self.fields[f], parent, self.fields[f])
            self.addWidget(label, f + 1, 0)
        self.insButton = KPushButton('insert/new', parent)
        self.updButton = KPushButton('update', parent)
        self.addWidget(self.insButton, len(self.fields), 0)
        self.addWidget(self.updButton, len(self.fields), 1)
        
    def get_data(self):
        return dict([(k, v.text()) for k,v in self.entries.items()])

        
class currentobject(object):
    def __init__(self):
      self.group = None
      self.id = None
      
class RecordSelector(QSplitter):
    def __init__(self, parent, app, table, fields, idcol, groupfields, view, name='RecordSelector'):
        QSplitter.__init__(self, parent, name)
        self.current = currentobject()
        self.app = app
        self.db = app.db
        self.table = table
        self.fields = fields
        self.idcol = idcol
        self.groupfields = groupfields
        self.listView = KListView(self)
        self.vsplit = QSplitter(self)
        self.vsplit.setOrientation(Qt.Vertical)
        self.recView = view(self.app, self.vsplit)
        frame = QFrame(self.vsplit)
        self.recForm = EditableRecord(frame, fields)
        self.connect(self.listView, SIGNAL('selectionChanged()'), self.groupChanged)
        self.connect(self.recForm.insButton, SIGNAL('clicked()'), self.insertRecord)
        self.connect(self.recForm.updButton, SIGNAL('clicked()'), self.updateRecord)
        self.initlistView()
        self.setSource(self.handleURL)
    
    def initlistView(self):
        self.listView.addColumn('group')
        self.listView.setRootIsDecorated(True)
        all = KListViewItem(self.listView, 'all')
        groups = [KListViewItem(self.listView, g) for g in self.groupfields]
        for g, parent in zip(self.groupfields, groups):
            fields = ['distinct %s' % g]
            rows = self.db.mcursor.select(fields=fields, table=self.table, order=g)
            for row in rows:
                item = KListViewItem(parent, row[g])
                item.groupfield = g
                

    def groupChanged(self):
        item = self.listView.currentItem()
        self.current.group = item.text(0)
        if hasattr(item, 'groupfield'):
            clause = Eq(item.groupfield, self.current.group)
            self.recView.set_clause(clause)
        elif self.current.group == 'all':
            self.recView.set_clause(None)
        else:
            self.recView.set_clause('NULL')

    def handleURL(self, url):
        action, obj, ident = str(url).split('.')
        row = self.db.mcursor.select_row(fields=self.fields,
                                         table=self.table, clause=Eq(self.idcol, ident))
        entries = self.recForm.entries
        for field in entries:
            entries[field].setText(row[field])
        self.current.id = ident
        

    def setSource(self, handler):
        self.recView.setSource = handler

    def insertRecord(self):
        data = self.recForm.get_data()
        self.db.insertData(self.idcol, self.table, data)
        self.groupChanged()

    def updateRecord(self):
        if self.current.id is not None:
            data = self.recForm.get_data()
            clause = Eq(self.idcol, self.current.id)
            row = self.db.mcursor.select_row(table=self.table, clause=clause)
            updict = {}
            for k, v in data.items():
                if str(row[k]) != str(v) and str(v):
                    print v
                    updict[k] = v
            print updict
        if updict:
            self.db.mcursor.update(table=self.table, data=updict, clause=clause)
            self.groupChanged()
            
    
        

#db is BaseDatabase from konsultant.maindb
#doc is Element from xml.dom.minidom
class ViewBrowser(KTextBrowser):
    def __init__(self, app, parent, doc):
        KTextBrowser.__init__(self, parent)
        self.setMimeSourceFactory(MimeSources())
        self.app = app
        self.db = app.db
        self.doc = doc(self.app)
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
    def __init__(self, app, parent):
        doc = AddressSelectDoc
        ViewBrowser.__init__(self, app, parent, doc)

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
                label = QLabel(self.selButton, 'address', parent, self.fields[f])
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
        dlg = AddressSelector(self, self.db.app, modal=True)
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
    def __init__(self, parent, app, name='AddressSelector', modal=True):
        KDialogBase.__init__(self, parent, name, modal)
        self.app = app
        self.db = app.db
        self.fields = ['street1', 'street2', 'city', 'state', 'zip']
        self.mainView = RecordSelector(self, self.app, 'addresses', self.fields,
                                       'addressid', ['state', 'city'], AddressSelectView, name=name)
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
        

class AdminWidget(BaseManagerWidget):
    def __init__(self, parent, app):
        BaseManagerWidget
        
class AdminWidget(KMainWindow):
    def __init__(self, parent, app):
        KMainWindow.__init__(self, parent, 'AdminWidget')
        
