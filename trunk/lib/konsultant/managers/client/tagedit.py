from qt import SIGNAL, SLOT, Qt
from qt import PYSIGNAL

from kdeui import KStdAction, KPopupMenu
from kdeui import KListView, KListViewItem

from useless.kbase.gui import SimpleRecordDialog
from useless.kbase.gui import EditRecordDialog
from useless.kdb.gui import ViewBrowser, RecordSelector
from useless.kdb.gui import SimpleWindow, RecordView

#from xmlgen import LocationDoc
from xmlgen import ClientTagDoc
from db import ClientManager

from gui import WithAddressIdEditDialog
LOCFIELDS = ['name', 'address', 'isp', 'connection', 'ip', 'static', 'serviced']


class EditLocationDialog(EditRecordDialog):
    def __init__(self, parent, record):
        fields = LOCFIELDS
        EditRecordDialog.__init__(self, parent, fields, record=record, name='EditLocation')
        
class EditLocationDialog(WithAddressIdEditDialog):
    def __init__(self, app, parent, record):
        fields = LOCFIELDS
        WithAddressIdEditDialog.__init__(self, app, parent, fields, record, 'EditLocation')
        
class TagView(RecordView):
    def __init__(self, app, parent, clientid, records):
        RecordView.__init__(self, app, parent, records, ClientTagDoc,
                            'edit')
        self.manager = ClientManager(self.app)

class LocationView(RecordView):
    def __init__(self, app, parent, records):
        RecordView.__init__(self, app, parent, records, LocationDoc,
                            'edit')
        self.manager = ClientManager(self.app)
        
    def setSource(self, url):
        action, context, id = str(url).split('.')
        dlg = EditLocationDialog(self.app, self, self.doc.records[int(id)].record)
        dlg.connect(dlg, SIGNAL('okClicked()'), self.updateRecord)
        self.dialogs['edit-location'] = dlg

    def updateRecord(self):
        dlg = self.dialogs['edit-location']
        data = dlg.getRecordData()
        locationid = dlg.record.locationid
        data['addressid'] = dlg.addressid
        print 'updateRecord', locationid
        self.manager.updateLocation(locationid, data)
        self.parent().emit(PYSIGNAL('updated()'), ())
        self.parent().close()
        
class TagRowView(KListView):
    def __init__(self, app, parent, clientid):
        KListView.__init__(self, parent)
        self.app = app
        self.manager = ClientManager(self.app)
        self.clientid = clientid
        self.addColumn('tag')
        self.addColumn('value')
        self.setRootIsDecorated(True)
        self.connect(self, SIGNAL('rightButtonClicked()'), self.popupmymenu)
        self.refreshlistView()

    def refreshlistView(self):
        self.clear()
        tags = self.manager.getTags(self.clientid)
        for k, v in tags.items():
            KListViewItem(self, k, v)

    def popupmymenu(self):
        print 'popupmymenu, right click worked'

    def rightButtonClicked(self, item, *args):
        print args
        print item
        print 'rightButtonClicked'
        
class ClientTagEditorWin(SimpleWindow):
    def __init__(self, app, parent, clientid):
        SimpleWindow.__init__(self, app, parent, 'ContactEditor')
        self.app = app
        self.manager = ClientManager(self.app)
        self.clientid = clientid
        self.fields =  ['tag', 'value']
        self.dialogs = {}
        self.mainView = TagRowView(self.app, self, clientid)
        self.setCentralWidget(self.mainView)
        self.setCaption('ClientTagEditor')
        self.resize(300, 500)
        self.show()
        
    def initActions(self):
        collection = self.actionCollection()
        self.newAction = KStdAction.openNew(self.slotNewTag, collection)
        self.editAction = KStdAction.replace(self.slotEditTag, collection)
        self.quitAction = KStdAction.quit(self.close, collection)
        
    def initMenus(self):
        mainMenu = KPopupMenu(self)
        self.newAction.plug(mainMenu)
        self.editAction.plug(mainMenu)
        self.quitAction.plug(mainMenu)
        self.menuBar().insertItem('&Main', mainMenu)
        self.menuBar().insertItem('&Help', self.helpMenu(''))

    def initToolbar(self):
        toolbar = self.toolBar()
        self.newAction.plug(toolbar)
        self.editAction.plug(toolbar)
        self.quitAction.plug(toolbar)
        
    def slotNewTag(self):
        dlg = SimpleRecordDialog(self, ['tag', 'value'])
        dlg.connect(dlg, SIGNAL('okClicked()'), self.insertTag)
        dlg.connect(dlg, PYSIGNAL('updated()'), self.mainView.refreshlistView)
        self.dialogs['new-tag'] = dlg

    def slotEditTag(self):
        print 'slotEditTag'
    def insertTag(self):
        dlg = self.dialogs['new-tag']
        data = dlg.getRecordData()
        print 'data', data
        #data['clientid'] = self.clientid
        self.manager.appendTag(self.clientid, data['tag'], data['value'])
        #self.manager.updateContact(contactid, data)
        dlg.emit(PYSIGNAL('updated()'), ())
        dlg.close()
        
