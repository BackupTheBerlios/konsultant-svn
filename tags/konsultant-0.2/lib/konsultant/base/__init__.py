from qt import QString, QStringList
from dcopexport import DCOPExObj

class Error(Exception):
    pass

class ExistsError(Error):
    pass

class NoExistError(Error):
    pass
class NoFileError(NoExistError):
    pass

class UnbornError(NoExistError):
    pass

class KeyError(ExistsError):
    pass

class TableError(ExistsError):
    pass



class DeadParrotObject (DCOPExObj):
    def __init__ (self, db, id = 'dead parrot'):
        DCOPExObj.__init__ (self, id)
        self.db = db
        # the methods available from this app via DCOP
        #     addMethod (<signature>, <Python method>)
        self.addMethod ('QString getParrotType()', self.get_type)
        self.addMethod ('void setParrotType (QString)', self.set_type)
        self.addMethod ('QString squawk()', self.squawk)
        self.addMethod ('QStringList adjectives()', self.adjectives)
        self.addMethod('QStringList get_tables()', self.get_tables)
        self.addMethod('QStringList get_fields(QString)', self.get_fields)
        # set up object variables
        self.parrot_type = QString ("Norwegian Blue")

    def get_type (self):
        return self.parrot_type

    def set_type (self, parrot_type):
        self.parrot_type = parrot_type

    def squawk (self):
        return "This parrot, a %s, is pining for the fjords" % (self.parrot_type)

    def adjectives (self):
        adjList = ["passed on", "is no more", "ceased to be", "expired", "gone to meet his maker",
                   "a stiff", "bereft of life", "rests in peace", "metabolic processes are now history",
                   "off the twig", "kicked the bucket", "shuffled off his mortal coil",
                   "run down his curtain", "joined the bleedin' choir invisible", "THIS IS AN EX-PARROT"]
        qadjList = QStringList ()
        for adj in adjList:
            qadjList.append (adj)

        return qadjList

    def get_tables(self):
        tables = self.db.mcursor.tables()
        return self._make_qlist(tables)
    
    def _make_qlist(self, alist):
        qlist = QStringList()
        for item in alist:
            qlist.append(item)
        return qlist

    def get_fields(self, table):
        return self._make_qlist(self.db.mcursor.fields(table))
    
