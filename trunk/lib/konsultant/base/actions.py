from qt import QString
from kdecore import KShortcut
from kdeui import KGuiItem, KAction


class BaseItem(KGuiItem):
    def __init__(self, text, icon, ttip, whatsit):
        KGuiItem.__init__(self, QString(text), QString(icon), QString(ttip),
                          QString(whatsit))
        
class EditAddressesItem(KGuiItem):
    def __init__(self):
        text = QString('Edit addresses')
        icon = QString('edit')
        ttip = QString('Edit addresses')
        wtf = QString('edit or browse addresses')
        KGuiItem.__init__(self, text, icon, ttip, wtf)

class ManageClientsItem(KGuiItem):
    def __init__(self):
        text = QString('Manage Clients')
        icon = QString('identity')
        ttip = QString('Manage Clients')
        wtf = QString('manage or browse Clients')
        KGuiItem.__init__(self, text, icon, ttip, wtf)

    
class ManageTicketsItem(BaseItem):
    def __init__(self):
        BaseItem.__init__(self, 'Manage Tickets', 'contents',
                          'Manage Tickets', 'manage or brouse Tickets')

class ConfigItem(BaseItem):
    def __init__(self):
        BaseItem.__init__(self, 'Configure Konsultant', 'configure',
                          'Configure Konsultant', 'Configure Konsultant')
        
class EditAddresses(KAction):
    def __init__(self, slot, parent):
        item = EditAddressesItem()
        name = 'EditAddresses'
        cut = KShortcut()
        KAction.__init__(self, item, cut, slot, parent, name)

class ManageClients(KAction):
    def __init__(self, slot, parent):
        item = ManageClientsItem()
        name = 'ManageClients'
        cut = KShortcut()
        KAction.__init__(self, item, cut, slot, parent, name)

class ManageTickets(KAction):
    def __init__(self, slot, parent):
        item = ManageTicketsItem()
        name = 'ManageTickets'
        cut = KShortcut()
        KAction.__init__(self, item, cut, slot, parent, name)

class ConfigureKonsultant(KAction):
    def __init__(self, slot, parent):
        item = ConfigItem()
        name = 'ConfigureKonsultant'
        cut = KShortcut()
        KAction.__init__(self, item, cut, slot, parent, name)
        
