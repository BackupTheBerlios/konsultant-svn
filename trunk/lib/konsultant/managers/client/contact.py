from qt import SIGNAL, SLOT, Qt
from qt import QSplitter
from kdeui import KStdAction, KPopupMenu

from konsultant.base.gui import SimpleRecordDialog
from konsultant.db.gui import ViewBrowser, RecordSelector
from konsultant.db.gui import SimpleWindow, RecordView

from xmlgen import ContactDoc
from db import ClientManager

class ContactView(RecordView):
    def __init__(self, app, parent, clientid):
        RecordView.__init__(self, app, parent, clientid, ContactDoc,
                            ClientManager, 'edit')
        
    def setSource(self, url):
        print url
        action, context, id = str(url).split('.')
        fields = [context]
        dlg = SimpleRecordDialog(self, fields, name='hello')
        current = self.doc.records[int(id)].record[context]
        dlg.grid.entries[context].setText(current)
        
class ContactEditorWidget(QSplitter):
    def __init__(self, parent, app, clientid):
        QSplitter.__init__(self, parent, 'ContactEditorWidget')
        self.app = app
        self.db = app.db
        self.recView = ContactView(self.app, self, clientid)
        
class ContactEditorWin(SimpleWindow):
    def __init__(self, parent, app, clientid):
        SimpleWindow.__init__(self, parent, app, 'ContactEditor')
        self.fields = ['name', 'email', 'description']
        self.mainView = ContactView(self.app, self, clientid)
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
        

