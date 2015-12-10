from collections import OrderedDict


class Graph(object):
    def __init__(self):
        super(Graph, self).__init__()
        self.nodes = set()

    def addNode(self, nodeType):
        node = nodeType()
        self.nodes.add(node)
        return node

    def removeNode(self, node):
        self.nodes.remove(node)


class Port(object):
    def __init__(self, name):
        super(Port, self).__init__()
        self.name = name
        self.value = None

    def connect(self, outputPort):
        self.value = outputPort.value


class VoidNode(object):
    def __init__(self):
        super(VoidNode, self).__init__()
        self.inputPorts = OrderedDict()
        self.outputPorts = OrderedDict()
        self.initPorts()

    def initPorts(self):
        pass

    def getInputPort(self, name):
        return self.inputPorts.get(name)

    def getOutputPort(self, name):
        return self.outputPorts.get(name)

    def addInputPort(self, name):
        port = Port(name)
        self.inputPorts[name] = port

    def addOutputPort(self, name):
        port = Port(name)
        self.outputPorts[name] = port

    def evaluate(self):
        pass


class AddNode(VoidNode):
    def __init__(self):
        super(AddNode, self).__init__()

    def initPorts(self):
        super(AddNode, self).initPorts()
        self.addInputPort("value1")
        self.addInputPort("value2")
        self.addOutputPort("result")

    def evaluate(self):
        super(AddNode, self).evaluate()
        result = sum([p.value for p in self.inputPorts.values()
                      if p.value is not None])
        self.getOutputPort("result").value = result
