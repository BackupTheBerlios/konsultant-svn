from qt import QString
from kdecore import KShortcut
from kdeui import KGuiItem, KAction


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
        icon = QString('edit')
        ttip = QString('Manage Clients')
        wtf = QString('manage or browse Clients')
        KGuiItem.__init__(self, text, icon, ttip, wtf)
    
        
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


