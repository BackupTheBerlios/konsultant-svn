from xml.dom.minidom import Element, Text

class BaseElement(Element):
    def __init__(self, tagname):
        Element.__init__(self, tagname)
        self._auto = False

    def __repr__(self):
        if not self._auto:
            return Element.__repr__(self)
        else:
            return self.toxml()

    def __str__(self):
        if not self._auto:
            return Element.__str__(self)
        else:
            return self.toxml()

class TextElement(BaseElement):
    def __init__(self, name, data):
        BaseElement.__init__(self, name)
        element = Text()
        element.data = data
        self.appendChild(element)

class Anchor(TextElement):
    def __init__(self, href, data):
        TextElement.__init__(self, 'a', data)
        self.setAttribute('href', href)

class TableBaseElement(BaseElement):
    def appendRowDataElement(self, parent, data, align='right'):
        element  = Element('td')
        element.setAttribute('align', align)
        elementd = Text()
        if type(data) == str:
            lines = data.split('\n')
            if len(lines) > 1:
                for line in lines:
                    e = Text()
                    e.data = line
                    element.appendChild(e)
                    element.appendChild(Element('br'))
            else:
                elementd.data = data
                element.appendChild(elementd)
        elif hasattr(data, 'hasChildNodes'):
            element.appendChild(data)
        else:
            #print 'type data', type(data)
            elementd.data = str(data)
            element.appendChild(elementd)
        parent.appendChild(element)

    def appendRowElement(self, parent, row, align='right'):
        element = Element('tr')
        for r in row:            
            self.appendRowDataElement(element, r, align)
        parent.appendChild(element)
        
class TableElement(TableBaseElement):
    def __init__(self, cols, align='right', border='1'):
        TableBaseElement.__init__(self, 'table')
        self.setAttribute('border', border)
        labels = Element('tr')
        self.appendRowElement(labels, cols, align)
        self.appendChild(labels)

class TableRowElement(TableBaseElement):
    def __init__(self, row, align='right'):
        TableBaseElement.__init__(self, 'tr')
        self.appendRowElement(self, row, align)

class Html(BaseElement):
    def __init__(self):
        Element.__init__(self, 'html')

class Body(BaseElement):
    def __init__(self):
        Element.__init__(self, 'body')
        