from qt import QSplitter, QPixmap, QGridLayout
from qt import QLabel, QFrame
from kdeui import KMainWindow, KEdit
from kdeui import KMessageBox, KAboutDialog
from kdeui import KConfigDialog, KListView
from kdeui import KDialogBase, KLineEdit

class AboutDialog(KAboutDialog):
    def __init__(self, parent, *args):
        KAboutDialog.__init__(self, parent, *args)
        self.setTitle('Konsultant Database')
        self.setAuthor('Joseph Rawson')
        self.show()
        
class MainEditWindow(KMainWindow):
    def __init__(self, *args):
        KMainWindow.__init__(self, *args)
        self.setGeometry (0, 0, 400, 600)

        self.edit = KEdit (self)
        self.setCentralWidget (self.edit)
        lines = file('/etc/profile').readlines()
        map(self.edit.insertLine, lines)
        self.show()

class MainWindow(KMainWindow):
    def __init__(self, *args):
        KMainWindow.__init__(self, *args)
        self.setGeometry (0, 0, 400, 600)
        self.mainView = QSplitter(self, 'main view')
        self.listView = KListView(self.mainView, 'listView')
        self.setCentralWidget (self.mainView)
        self.show()


        
class SimpleRecord(QGridLayout):
    def __init__(self, parent, fields, text=None, name='SimpleRecord'):
        if text is None:
            text = '<b>insert a simple record</b>'
        QGridLayout.__init__(self, parent, len(fields) + 1, 2, 1, -1, name)
        self.fields = fields
        self.entries = {}
        self._setupfields(parent)
        self.setSpacing(7)
        self.setMargin(10)
        print text
        self.addMultiCellWidget(QLabel(text, parent), 0, 0, 0, 1)

    def _setupfields(self, parent):
        for f in range(len(self.fields)):
            entry = KLineEdit('', parent)
            self.entries[self.fields[f]] = entry
            self.addWidget(entry, f + 1, 1)
            label = QLabel(entry, self.fields[f], parent, self.fields[f])
            self.addWidget(label, f + 1, 0)
        
class SimpleRecordDialog(KDialogBase):
    def __init__(self, parent, fields, name='SimpleRecordDialog'):
        KDialogBase.__init__(self, parent, name)
        self.page = QFrame(self)
        self.setMainWidget(self.page)
        text = 'this is a <em>simple</em> record dialog'
        self.grid = SimpleRecord(self.page, fields, text, name=name)
        self.showButtonApply(False)
        self.setButtonOKText('insert', 'insert')
        self.show()


