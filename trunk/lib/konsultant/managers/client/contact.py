from qt import SIGNAL, SLOT, Qt
from qt import PYSIGNAL
from qt import QSplitter
from kdeui import KStdAction, KPopupMenu

from kommon.base.gui import EditRecordDialog
from kommon.db.gui import ViewBrowser, RecordSelector
from kommon.db.gui import SimpleWindow, RecordView

from xmlgen import ContactDoc
from db import ClientManager
from gui import WithAddressIdEditDialog

CONFIELDS = ['name', 'address', 'email', 'description']

class EditContactDialog(WithAddressIdEditDialog):
    def __init__(self, app, parent, record):
        fields = CONFIELDS
        WithAddressIdEditDialog.__init__(self, app, parent, fields, record, 'EditContact')
        

class ContactView(RecordView):
    def __init__(self, app, parent, records):
        RecordView.__init__(self, app, parent, records, ContactDoc,
                            'edit')
        self.manager = ClientManager(self.app)
        
    def setSource(self, url):
        action, context, id = str(url).split('.')
        dlg = EditContactDialog(self.app, self, self.doc.records[int(id)].record)
        dlg.connect(dlg, SIGNAL('okClicked()'), self.updateRecord)
        self.dialogs['edit-contact'] = dlg

    def updateRecord(self):
        dlg = self.dialogs['edit-contact']
        data = dlg.getRecordData()
        contactid = dlg.record.contactid
        data['addressid'] = dlg.addressid
        print 'updateRecord', contactid
        print 'data', data
        self.manager.updateContact(contactid, data)
        self.parent().emit(PYSIGNAL('updated()'), ())
        self.parent().close()
        

        

class ContactEditorWin(SimpleWindow):
    def __init__(self, app, parent, records):
        SimpleWindow.__init__(self, app, parent, 'ContactEditor')
        self.fields = CONFIELDS
        self.mainView = ContactView(self.app, self, records)
        self.setCentralWidget(self.mainView)
        self.setCaption('ContactEditor')
        self.resize(300, 500)
        self.show()
        
    def initActions(self):
        collection = self.actionCollection()
        self.quitAction = KStdAction.quit(self.close, collection)

    def initMenus(self):
        mainMenu = KPopupMenu(self)
        self.quitAction.plug(mainMenu)
        self.menuBar().insertItem('&Main', mainMenu)
        self.menuBar().insertItem('&Help', self.helpMenu(''))
        

