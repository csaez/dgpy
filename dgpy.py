import logging
from collections import OrderedDict

logger = logging.getLogger(__name__)
PUSH = 0
PULL = 1


class Graph(object):
    def __init__(self):
        super(Graph, self).__init__()
        self.nodes = dict()
        self.model = None

    def addNode(self, name, nodeType, **kwargs):
        node = nodeType(name)
        node.model = self.model
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

    def serialize(self):
        data = {
            "dataType": "dgpy",
            "version": "1.0.0",
            "model": self.model,
            "nodes": dict(),
        }
        return data

    @classmethod
    def fromData(cls, data):
        if data.get("dataType") != "dgpy":  # validation
            return

        graph = cls()
        graph.model = data.get("model")
        return graph


class Port(object):
    value = property(fget=lambda x: x.getValue(),
                     fset=lambda x, value: x.setValue(value))

    def __init__(self, name):
        super(Port, self).__init__()
        self.name = name
        self.owner = None
        self._value = None
        self.sources = set()

    def getValue(self):
        return self._value

    def setValue(self, value):
        self._value = value

    @property
    def isConnected(self):
        return len(self.sources) > 0


class InputPort(Port):
    def setValue(self, value):
        super(InputPort, self).setValue(value)
        if self.owner.model == PUSH:
            self.owner.evaluate()
        if self.owner.model == PULL:
            self.owner.isDirty = True

    def connect(self, outputPort):
        self.sources.add(outputPort)
        outputPort.sources.add(self)
        self.value = outputPort.value

    def disconnect(self):
        port = self.sources.pop()
        port.sources.remove(self)


class OutputPort(Port):
    def setValue(self, value):
        if self.isConnected:
            for port in self.sources:
                if self.owner.model == PUSH:
                    port.value = value
        super(OutputPort, self).setValue(value)

    def getValue(self):
        if self.owner.model == PULL:
            if self.owner.isDirty:
                for port in self.owner.inputPorts.values():
                    if port.isConnected:
                        for src in port.sources:
                            port.value = src.value
                self.owner.evaluate()
                self.owner.isDirty = False
        return super(OutputPort, self).getValue()


class VoidNode(object):
    isDirty = property(fget=lambda x: x._isDirty,
                       fset=lambda x, value: x.setDirty(value))

    def __init__(self, name):
        super(VoidNode, self).__init__()
        self.name = name
        self.model = None
        self.evalCount = 0
        self._isDirty = True
        self.inputPorts = OrderedDict()
        self.outputPorts = OrderedDict()
        self.initPorts()

    def setDirty(self, value):
        self._isDirty = value
        if not value:
            return
        for port in self.outputPorts.values():
            if port.isConnected:
                for src in port.sources:
                    src.owner.isDirty = True

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
        port = OutputPort(name)
        port.owner = self
        self.outputPorts[name] = port

    def evaluate(self):
        logger.debug("Evaluating {}".format(self.name))
        self.evalCount += 1


class AddNode(VoidNode):
    def initPorts(self):
        super(AddNode, self).initPorts()
        self.addInputPort("value1")
        self.addInputPort("value2")
        self.addOutputPort("result")

    def evaluate(self):
        super(AddNode, self).evaluate()
        result = 0
        for p in self.inputPorts.values():
            msg = "{0}: {1}".format(p.name, p.value)
            if p.isConnected:
                msg += " (connected)"
            logger.debug(msg)
            if p.value is not None:
                result += p.value
        self.getOutputPort("result").value = result
        logger.debug("---")
