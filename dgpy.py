import logging
from collections import OrderedDict

logger = logging.getLogger(__name__)


class Graph(object):
    def __init__(self):
        super(Graph, self).__init__()
        self.nodes = dict()

    def addNode(self, name, nodeType, **kwargs):
        node = nodeType(name)
        self.nodes[name] = node
        for k, v in kwargs.iteritems():
            p = node.getInputPort(k)
            if p:
                p.value = v
        return node

    def removeNode(self, node):
        del self.nodes[node.name]

    def getNode(self, name):
        return self.nodes.get(name)


class Port(object):
    value = property(fget=lambda x: x.getValue(),
                     fset=lambda x, value: x.setValue(value))

    def __init__(self, name):
        super(Port, self).__init__()
        self.name = name
        self.owner = None
        self._value = None
        self.isConnected = False
        self.dataSource = None

    def connect(self, outputPort):
        self.isConnected = True
        self.dataSource = outputPort
        self.updateValue()

    def updateValue(self):
        self.value = self.dataSource.value

    def getValue(self):
        return self._value

    def setValue(self, value):
        self._value = value


class InputPort(Port):
    def setValue(self, value):
        super(InputPort, self).setValue(value)
        self.owner.evaluate()


class VoidNode(object):
    def __init__(self, name):
        super(VoidNode, self).__init__()
        self.name = name
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
        port = InputPort(name)
        port.owner = self
        self.inputPorts[name] = port

    def addOutputPort(self, name):
        port = Port(name)
        port.owner = self
        self.outputPorts[name] = port

    def evaluate(self):
        logger.debug("Evaluating {}".format(self))
        for p in self.inputPorts.values():
            if p.isConnected:
                p.updateValue()


class AddNode(VoidNode):
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
