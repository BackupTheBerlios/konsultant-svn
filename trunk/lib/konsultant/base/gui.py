from qt import QSplitter, QPixmap, QGridLayout
from qt import QLabel, QFrame, QString
from qt import SIGNAL, SLOT, Qt
from qt import QMimeSourceFactory

from kdecore import KConfigDialogManager
from kdecore import KAboutData
from kdeui import KMainWindow, KEdit, KPushButton
from kdeui import KMessageBox, KAboutDialog
from kdeui import KConfigDialog, KListView
from kdeui import KDialogBase, KLineEdit
from kdeui import KTextBrowser, KPopupMenu
from kdeui import KStdAction

from konsultant.base.actions import EditAddresses, ManageClients
from konsultant.base.config import DefaultSkeleton, KonsultantConfig

class MimeSources(QMimeSourceFactory):
    def __init__(self):
        QMimeSourceFactory.__init__(self)
        self.addFilePath('/usr/share/wallpapers')
        
class AboutData(KAboutData):
    def __init__(self):
        KAboutData.__init__(self,
                            'Konsultant',
                            'konsultant',
                            '0.1',
                            'Client Management for Small Business')
        self.addAuthor('Joseph Rawson', 'author',
                       'umeboshi@gregscomputerservice.com')
        self.setCopyrightStatement('plublic domain')
        
                            
class AboutDialog(KAboutDialog):
    def __init__(self, parent, *args):
        KAboutDialog.__init__(self, parent, *args)
        self.setTitle('Konsultant Database')
        self.setAuthor('Joseph Rawson')
        self.show()

class MainWindow(KMainWindow):
    def __init__(self, parent, name='MainWindow'):
        KMainWindow.__init__(self, parent, name)
        self.initActions()
        self.initMenus()
        if hasattr(self, 'initToolbar'):
            self.initToolbar()

    def initActions(self, collection=None):
        if collection is None:
            collection = self.actionCollection()
        self.quitAction = KStdAction.quit(self.close, collection)

    def initMenus(self, mainmenu=None):
        if mainmenu is None:
            mainmenu = KPopupMenu(self)
        self.quitAction.plug(mainmenu)
        self.menuBar().insertItem('&Main', mainmenu)
        self.menuBar().insertItem('&Help', self.helpMenu(''))
    
class SimpleRecord(QGridLayout):
    def __init__(self, parent, fields, text=None, record=None, name=None):
        print 'record, name', record, name
        if name is None:
            print 'I need a name', record
            raise Exception, 'name needed in SimpleRecord'
        QGridLayout.__init__(self, parent, len(fields) + 1, 2, 1, -1, name)
        self.fields = fields
        self.entries = {}
        #self._setupfields(parent)
        self.setSpacing(7)
        self.setMargin(10)
        self.record = record
        self._refbuttons = {}
        self._setupfields(parent)
        
    def _setupfields(self, parent, text=None):
        if text is None:
            text = '<b>insert a simple record</b>'
        for child in self.parent().children():
            print child
            #child.close()
        refdata = None
        if self.record is not None and hasattr(self.record, '_refdata'):
            print 'record is not None', self.record
            refdata = self.record._refdata
        for f in range(len(self.fields)):
            field = self.fields[f]
            print 'field is', field
            if refdata is not None and field in refdata.cols:
                button = KPushButton('select/create', parent)
                self._refbuttons[field] = button
                self.addWidget(button, f + 1, 1)
                label = QLabel(entry, field, parent, field)
                self.addWidget(label, f + 1, 0)
            else:
                entry = KLineEdit('', parent)
                if self.record is not None:
                    entry.setText(str(self.record[field]))
                self.entries[field] = entry
                self.addWidget(entry, f + 1, 1)
                label = QLabel(entry, field, parent, field)
                self.addWidget(label, f + 1, 0)
        self.addMultiCellWidget(QLabel(text, parent), 0, 0, 0, 1)

    def getRecordData(self):
        return dict([(k,str(v.text())) for k,v in self.entries.items()])

class SimpleRecordDialog(KDialogBase):
    def __init__(self, parent, fields, record=None, name='SimpleRecordDialog'):
        KDialogBase.__init__(self, parent, name)
        self.page = QFrame(self)
        self.setMainWidget(self.page)
        text = 'this is a <em>simple</em> record dialog'
        self.grid = SimpleRecord(self.page, fields, text,
                                 record=record,name=name)
        self.showButtonApply(False)
        self.setButtonOKText('insert', 'insert')
        self.dialogs = {}
        self.refbuttons = self.grid._refbuttons
        self.show()

    def getRecordData(self):
        return self.grid.getRecordData()
    

class EditRecordDialog(SimpleRecordDialog):
    def __init__(self, parent, fields, record, name):
        SimpleRecordDialog.__init__(self, parent, fields, record=record, name=name)
        self.record = record
        if hasattr(record, '_refdata'):
            print 'record has refdata'
        self.setButtonOKText('update', 'update')
        
class ConfigureDialog(KConfigDialog):
    def __init__(self, parent, cfg, name='ConfigureDialog'):
        print 'repreper'
        #skel = DefaultSkeleton()
        skel = KonsultantConfig()
        print 'hwllo'
        #skel.readConfig()
        print skel
        KConfigDialog.__init__(self, parent, name, skel)
        #self.manager = KConfigDialogManager(self, skel, 'ConfigureDialogManager')
