from qt import SIGNAL, SLOT, Qt

from useless.kbase.refdata import RefData
from useless.kbase.gui import EditRecordDialog
from useless.db.record import EmptyRefRecord
from useless.kdb.gui import SimpleRecordDialog

from konsultant.db.gui import AddressSelector
from konsultant.db.xmlgen import AddressLink

class AddressData(RefData):
    def __init__(self):
        RefData.__init__(self, dict(address='addressid'))

class _HasAddressDialog(object):
    def selAddress(self):
        dlg = AddressSelector(self.app, self, modal=True)
        dlg.setSource(self.addressidSelected)
        self.dialogs['address'] = dlg
    
    def addressidSelected(self, url):
        addressid = int(str(url).split('.')[2])
        self.enableButtonOK(True)
        self.dialogs['address'].done(0)
        #self.refbuttons['address'].close()
        #n = self.grid.fields.index('address') + 1
        text = AddressLink(self.app.db, addressid).firstChild.data
        #lbl = QLabel(text, self.page)
        #lbl.show()
        self.refbuttons['address'].setText(text)
        #self.grid.addMultiCellWidget(lbl, n, n, 1, 1)
        self.addressid = addressid
        
        
class WithAddressIdRecDialog(SimpleRecordDialog, _HasAddressDialog):
    def __init__(self, app, parent, fields, name):
        record = EmptyRefRecord(fields, AddressData())
        SimpleRecordDialog.__init__(self, parent, fields, record=record, name=name)
        self.app = app
        self.connect(self.refbuttons['address'],
                     SIGNAL('clicked()'), self.selAddress)
        self.enableButtonOK(False)

class WithAddressIdEditDialog(EditRecordDialog, _HasAddressDialog):
    def __init__(self, app, parent, fields, record, name):
        EditRecordDialog.__init__(self, parent, fields, record, name)
        self.app = app
        self.connect(self.refbuttons['address'],
                     SIGNAL('clicked()'), self.selAddress)
        #self.enableButtonOK(False)
        addressid = record.addressid
        text = AddressLink(self.app.db, addressid).firstChild.data
        self.refbuttons['address'].setText(text)
        self.addressid = addressid
        


class ClientDialog(SimpleRecordDialog):
    def __init__(self, app, parent, name='ClientDialog'):
        fields = ['client']
        SimpleRecordDialog.__init__(self, parent, fields, name='ClientDialog')

class ClientEditDialog(EditRecordDialog):
    def __init__(self, app, parent, record):
        EditRecordDialog.__init__(self, parent, ['client'], record, 'ClientEditDialog')
        self.clientid = record['clientid']
        
class LocationDialog(WithAddressIdRecDialog):
    def __init__(self, app, parent, name='LocationDialog'):
        fields = ['name', 'address', 'isp', 'connection',
                  'ip', 'static', 'serviced']
        WithAddressIdRecDialog.__init__(self, app, parent, fields, name=name)
        
class ContactDialog(WithAddressIdRecDialog):
    def __init__(self, app, parent, name='ContactDialog'):
        fields = ['name', 'address', 'email', 'description']
        WithAddressIdRecDialog.__init__(self, app, parent, fields, name=name)
        
