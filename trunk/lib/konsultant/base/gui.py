from qt import QSplitter, QPixmap, QGridLayout
from qt import QLabel, QFrame, QString
from qt import SIGNAL, SLOT, Qt
from qt import QMimeSourceFactory
from qt import QCheckBox

from kdecore import KConfigDialogManager
from kdecore import KAboutData
from kdeui import KMainWindow, KEdit, KPushButton
from kdeui import KMessageBox, KAboutDialog
from kdeui import KConfigDialog, KListView
from kdeui import KDialogBase, KLineEdit
from kdeui import KTextBrowser, KPopupMenu
from kdeui import KStdAction
from kdeui import KTabWidget

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

