from qt import SIGNAL, SLOT, Qt
from qt import QSplitter
from kdeui import KStdAction, KPopupMenu


from konsultant.base.gui import EditRecordDialog
from konsultant.db.gui import ViewBrowser, RecordSelector
from konsultant.db.gui import SimpleWindow, RecordView

from xmlgen import LocationDoc
from db import ClientManager

LOCFIELDS = ['name', 'address', 'isp', 'connection', 'ip', 'static', 'serviced']

class EditLocationDialog(EditRecordDialog):
    def __init__(self, parent, record):
        fields = LOCFIELDS
        EditRecordDialog.__init__(self, parent, fields, record, name='EditLocation')
        
class LocationView(RecordView):
    def __init__(self, app, parent, records):
        RecordView.__init__(self, app, parent, records, LocationDoc,
                            'edit')
        
    def setSource(self, url):
        action, context, id = str(url).split('.')
        dlg = EditLocationDialog(self, self.doc.records[int(id)].record)
        dlg.connect(dlg, SIGNAL('okClicked()'), self.updateRecord)
        self.dialogs['edit-location'] = dlg

    def updateRecord(self):
        dlg = self.dialogs['edit-location']
        data = dlg.getRecordData()
        locationid = dlg.record.locationid
        print 'updateRecord', locationid
        self.manager.updateLocation(locationid, data)
        

        
class LocationEditorWin(SimpleWindow):
    def __init__(self, parent, app, records):
        SimpleWindow.__init__(self, parent, app, 'ContactEditor')
        self.fields = LOCFIELDS
        self.mainView = LocationView(self.app, self, records)
        self.setCentralWidget(self.mainView)
        self.setCaption('LocationEditor')
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
        

