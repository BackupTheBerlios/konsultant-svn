from kdeui import KLineEdit, KTextEdit

from useless.kbase.gui import VboxDialog, MyCombo

from db import TroubleManager

class TroubleDialog(VboxDialog):
    def __init__(self, app, parent, clientid, name='TroubleDialog'):
        VboxDialog.__init__(self, parent, name)
        self.app = app
        self.manager = TroubleManager(self.app)
        self.clientid = clientid
        self.problemEdit = KLineEdit('', self.page)
        self.magnetBox = MyCombo(self.page)
        self.magnetBox.fill(self.manager.getAvailableMagnets())
        self.worktodoEdit = KTextEdit(self.page)
        self.vbox.addWidget(self.problemEdit)
        self.vbox.addWidget(self.magnetBox)
        self.vbox.addWidget(self.worktodoEdit)
        self.showButtonApply(False)
        self.setButtonOKText('insert', 'insert')
        self.show()

    def getRecordData(self):
        problem = str(self.problemEdit.text())
        worktodo = str(self.worktodoEdit.text())
        magnet = str(self.magnetBox.currentText())
        return dict(problem=problem, magnet=magnet,
                    worktodo=worktodo, clientid=self.clientid)
    
