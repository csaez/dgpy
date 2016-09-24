# Copyright (c) 2016 Cesar Saez

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import pprint
import logging
from collections import OrderedDict, Counter

logger = logging.getLogger(__name__)
NODES = dict()
PUSH = 0
PULL = 1


def registerNode(nodeType):
    nodeName = nodeType.__name__
    NODES[nodeName] = nodeType


def getRefCounterFromData(data):
    count = Counter()

    for nodeName, nodeData in data["nodes"].items():

        for portName, portData in nodeData["inputPorts"].items():
            for sourceName in portData["sources"]:
                sourceOwner = sourceName.split(".")[0]
                count[sourceOwner] -= 1

        for portName, portData in nodeData["outputPorts"].items():
            for sourceName in portData["sources"]:
                sourceOwner = sourceName.split(".")[0]
                count[sourceOwner] += 1

    # normalize
    if len(count.values()):
        toAdd = abs(min(count.values()))
        for k in count.keys():
            count[k] += toAdd

    return count


class Graph(object):
    def __init__(self):
        super(Graph, self).__init__()
        self._nodes = dict()
        self.model = None

    @property
    def nodes(self):
        return tuple(self._nodes.values())

    def addNode(self, name, nodeType, **kwargs):
        node = nodeType(name)
        node.model = self.model
        self._nodes[name] = node
        for k, v in kwargs.items():
            p = node.getInputPort(k)
            if p:
                p.value = v
        return node

    def removeNode(self, node):
        del self._nodes[node.name]

    def getNode(self, name):
        return self._nodes.get(name)

    def get(self, fullname):
        splitName = fullname.split(".")
        node = self.getNode(splitName[0])
        if node and len(splitName) == 2:
            port = node.getInputPort(splitName[1])
            if port is None:
                port = node.getOutputPort(splitName[1])
            if port:
                return port
        return node

    def serialize(self):
        data = {
            "dataType": "dgpy",
            "version": "1.0.0",
            "model": self.model,
            "nodes": dict(),
        }
        for node in self.nodes:
            data["nodes"][node.name] = node.serialize()

        logger.debug("Serializing graph...")
        logger.debug(pprint.pformat(data))
        return data

    @classmethod
    def fromData(cls, data):
        # validation
        if not isinstance(data, dict) or data.get("dataType") != "dgpy":
            return

        graph = cls()
        graph.model = data.get("model")

        count = getRefCounterFromData(data)
        orderedNodes = sorted(data["nodes"].keys(), key=lambda x: count[x])

        for nodeName in orderedNodes:
            nodeData = data["nodes"][nodeName]
            nodeClass = NODES.get(nodeData["className"])
            node = graph.addNode(nodeName, nodeClass)
            node.model = nodeData["model"]

            for portName, portData in nodeData["inputPorts"].items():
                port = node.getInputPort(portName)

                for sourceName in portData["sources"]:
                    port.connect(graph.get(sourceName))

                if not port.isConnected:
                    port.value = portData["value"]

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

    def serialize(self):
        data = {
            "value": self.value,
            "sources": [x.fullname for x in self.sources],
        }
        return data

    def getValue(self):
        return self._value

    def setValue(self, value):
        self._value = value

    @property
    def isConnected(self):
        return len(self.sources) > 0

    @property
    def fullname(self):
        return ".".join((self.owner.fullname, self.name))


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
                for port in self.owner._inputPorts.values():
                    if port.isConnected:
                        for src in port.sources:
                            port.value = src.value
                self.owner.evaluate()
                self.owner.isDirty = False
        return super(OutputPort, self).getValue()


class VoidNode(object):
    """
    Empty and most basic node type.
    Every custom node is asumed to subclass, or at least replicate, this
    interface.
    """
    isDirty = property(fget=lambda x: x._isDirty,
                       fset=lambda x, value: x.setDirty(value))

    def __init__(self, name):
        super(VoidNode, self).__init__()
        self.name = name
        self.model = None
        self.evalCount = 0
        self._isDirty = True
        self._inputPorts = OrderedDict()
        self._outputPorts = OrderedDict()
        self.initPorts()

    @property
    def inputPorts(self):
        return tuple(self._inputPorts.values())

    @property
    def outputPorts(self):
        return tuple(self._outputPorts.values())

    @property
    def fullname(self):
        return self.name

    def serialize(self):
        """Return a dict containing the serialized data (json/yaml/markup friendly).
        """
        data = {
            "model": self.model,
            "inputPorts": dict(),
            "outputPorts": dict(),
            "className": type(self).__name__,
        }
        for port in self.inputPorts:
            data["inputPorts"][port.name] = port.serialize()
        for port in self.outputPorts:
            data["outputPorts"][port.name] = port.serialize()
        return data

    def setDirty(self, value):
        """Tag the node to be reevaluated the next time the graph pull its data.
        """
        self._isDirty = value
        if not value:
            return
        for port in self._outputPorts.values():
            if port.isConnected:
                for src in port.sources:
                    src.owner.isDirty = True

    def initPorts(self):
        """Callback where ports should be added/registered."""
        pass

    def getInputPort(self, name):
        return self._inputPorts.get(name)

    def getOutputPort(self, name):
        return self._outputPorts.get(name)

    def addInputPort(self, name):
        """Add/register an input port to the node."""
        port = InputPort(name)
        port.owner = self
        self._inputPorts[name] = port

    def addOutputPort(self, name):
        """Add/register an output port to the node."""
        port = OutputPort(name)
        port.owner = self
        self._outputPorts[name] = port

    def evaluate(self):
        """Node computation should be implemented here.
        Please extend this method in order to keep track of evaluation count.
        """
        logger.debug("Evaluating {}".format(self.name))
        self.evalCount += 1

registerNode(VoidNode)
