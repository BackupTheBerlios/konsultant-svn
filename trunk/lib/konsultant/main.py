import os
from qt import SLOT, SIGNAL, Qt
from kdecore import KApplication, KIconLoader
from kdecore import KStandardDirs
from kdecore import KLockFile

from kdeui import KMainWindow, KSystemTray
from kdeui import KPopupMenu

from konsultant.base.config import BaseConfig
from konsultant.base.gui import MainWindow, ConfigureDialog
from konsultant.base.actions import EditAddresses, ManageClients
from konsultant.base.actions import ManageTickets, ConfigureKonsultant
from konsultant.db import BaseDatabase, BaseObject
from konsultant.db.pgpool import PgPool
from konsultant.db.gui import AddressSelector
from konsultant.clientmanager import ClientManagerWidget
from konsultant.ticketmanager import TicketManagerWidget

class KonsultantMainApplication(KApplication):
    def __init__(self, *args):
        KApplication.__init__(self)
        cfg = BaseConfig()
        self.cfg = cfg
        dirs = KStandardDirs()
        self.tmpdir = str(dirs.findResourceDir('tmp', '/'))
        self.datadir = str(dirs.findResourceDir('data', '/'))
        self.socketdir = str(dirs.findResourceDir('socket', '/'))
        dsn = {}
        self.cfg.setGroup('database')
        dsn['user'] = self.cfg.readEntry('dbuser')
        dsn['dbname'] = self.cfg.readEntry('dbname')
        dsn['passwd'] = self.cfg.readEntry('dbpass')
        self.cfg.setGroup('pgpool')
        self.pgpool = None
        usepgpool = self.cfg.readEntry('usepgpool')
        if usepgpool != 'false':
            print 'using pgpool'
            self.pgpool = PgPool(self.cfg, self.tmpdir, self.datadir)
            if not os.path.isfile(self.pgpool.pidfile):
                self.pgpool.run()
            else:
                self.pgpool = None
            dsn['host'] = 'localhost'
            dsn['port'] = self.cfg.readEntry('port')
        else:
            self.cfg.setGroup('database')
            dsn['host'] = self.cfg.readEntry('dbhost')
            dsn['port'] = self.cfg.readEntry('dbport')
        self.db = BaseDatabase(dsn, 'Konsultant', self)
        self.connect(self, SIGNAL('aboutToQuit()'), self.quit)
        
        
    def quit(self):
        if self.pgpool is not None:
            if os.path.isfile(self.pgpool.pidfile):
                self.pgpool.stop()
        KApplication.quit(self)
        

                
        

class KonsultantMainWindow(KMainWindow):
    def __init__(self, app, *args):
        KMainWindow.__init__(self, *args)
        self.icons = KIconLoader()
        self.systray = KSystemTray(self)
        self.systray.setPixmap(self.icons.loadIcon('connect_no', 1))
        self.systray.show()
        self.initActions()
        self.initMenus()
        self.initToolbar()
        self.app = app
        self.db = app.db
        self.cfg = app.cfg
        
    def initActions(self):
        collection = self.systray.actionCollection()
        self.editaddressAction = EditAddresses(self.slotEditAddresses, collection)
        self.manageclientsAction = ManageClients(self.slotManageClients, collection)
        self.manageticketsAction = ManageTickets(self.slotManageTickets, collection)
        self.configureAction = ConfigureKonsultant(self.slotConfigure, collection)
        
    def initMenus(self):
        trayMenu = self.systray.contextMenu()
        mainMenu = KPopupMenu(self)
        self.menuBar().insertItem('&Main', mainMenu)
        self.menuBar().insertItem('&Help', self.helpMenu(''))
        for menu in [trayMenu, mainMenu]:
            self.editaddressAction.plug(menu)
            self.manageclientsAction.plug(menu)
            self.manageticketsAction.plug(menu)
            self.configureAction.plug(menu)

    def initToolbar(self):
        toolbar = self.toolBar()
        actions = [self.manageclientsAction, self.manageticketsAction,
                   self.editaddressAction, self.configureAction]
        for action in actions:
            action.plug(toolbar)
        
        
    def slotEditAddresses(self):
        AddressSelector(self, self.db, 'AddressBrowser', modal=False)

    def slotManageClients(self):
        win = ClientManagerWidget(self, self.db)
        win.show()

    def slotManageTickets(self):
        win = TicketManagerWidget(self, self.db)
        win.show()

    def slotConfigure(self):
        print 'Configure Konsultant'
        c = ConfigureDialog(self, self.cfg)
        c.show()
