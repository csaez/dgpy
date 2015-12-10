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


class VoidNode(object):
    def __init__(self):
        super(VoidNode, self).__init__()
