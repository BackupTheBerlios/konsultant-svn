from xml.dom.minidom import Element, Text

class BaseElement(Element):
    def __init__(self, tagname):
        Element.__init__(self, tagname)

class TextElement(BaseElement):
    def __init__(self, name, data):
        BaseElement.__init__(self, name)
        elementd = Text()
        if type(data) == str:
            lines = data.split('\n')
            if len(lines) > 1:
                for line in lines:
                    e = Text()
                    e.data = line
                    self.appendChild(e)
                    self.appendChild(BaseElement('br'))
            else:
                elementd.data = data
                self.appendChild(elementd)
        elif hasattr(data, 'hasChildNodes'):
            self.appendChild(data)
        else:
            #print 'type data', type(data)
            elementd.data = str(data)
            self.appendChild(elementd)

class Anchor(TextElement):
    def __init__(self, href, data):
        TextElement.__init__(self, 'a', data)
        self.setAttribute('href', href)

class TableBaseElement(BaseElement):
    def appendRowDataElement(self, parent, data, align='right'):
        element  = BaseElement('td')
        element.setAttribute('align', align)
        elementd = Text()
        if type(data) == str:
            lines = data.split('\n')
            if len(lines) > 1:
                for line in lines:
                    e = Text()
                    e.data = line
                    element.appendChild(e)
                    element.appendChild(BaseElement('br'))
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
        element = BaseElement('tr')
        for r in row:            
            self.appendRowDataElement(element, r, align)
        parent.appendChild(element)
        
class TableElement(TableBaseElement):
    def __init__(self, cols, align='right', border='1'):
        TableBaseElement.__init__(self, 'table')
        self.setAttribute('border', border)
        self.setAttribute('class', 'tableheader')
        labels = BaseElement('tr')
        self.appendRowElement(labels, cols, align)
        self.appendChild(labels)

class TableRowElement(TableBaseElement):
    def __init__(self, row, align='right'):
        TableBaseElement.__init__(self, 'tr')
        self.appendRowElement(self, row, align)

class Html(BaseElement):
    def __init__(self):
        BaseElement.__init__(self, 'html')

class Body(BaseElement):
    def __init__(self):
        BaseElement.__init__(self, 'body')
        

class ListItem(TextElement):
    def __init__(self, data):
        TextElement.__init__(self, 'li', data)

class UnorderedList(BaseElement):
    def __init__(self):
        BaseElement.__init__(self, 'ul')

