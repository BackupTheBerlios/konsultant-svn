

#refcols is a  name, idcol paired dictionary
#refdata[name] is a dictionary of id, record pairs
#  where id is from idcol in refcols
#refobject[name] is the object that handles the corresponding refdata
class RefData(object):
    def __init__(self, refcols):
        object.__init__(self)
        self.cols = refcols
        self.data = {}
        self.object = {}
        for col in refcols:
            self.set_refdata(col, {})
            self.set_refobject(col, None)
            

    def set_refobject(self, column, objeckt):
        self.object[column] = objeckt

    def set_refdata(self, column, refdata):
        self.data[column] = refdata
        
