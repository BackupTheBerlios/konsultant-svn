from qt import SIGNAL, SLOT, Qt
from qt import QSplitter
from kdeui import KStdAction, KPopupMenu


from konsultant.base.gui import SimpleRecordDialog
from konsultant.db.gui import ViewBrowser, RecordSelector
from konsultant.db.gui import SimpleWindow, RecordView

from xmlgen import LocationDoc
from db import ClientManager

class LocationView(RecordView):
    def __init__(self, app, parent, records):
        RecordView.__init__(self, app, parent, records, LocationDoc,
                            'edit')
        
    def setSource(self, url):
        print url
        action, context, id = str(url).split('.')
        fields = [context]
        dlg = SimpleRecordDialog(self, fields, name='hello')
        current = self.doc.records[int(id)].record[context]
        dlg.grid.entries[context].setText(current)
        

        
class LocationEditorWin(SimpleWindow):
    def __init__(self, parent, app, records):
        SimpleWindow.__init__(self, parent, app, 'ContactEditor')
        self.fields = ['name', 'isp', 'connection', 'ip', 'static', 'serviced']
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
        

