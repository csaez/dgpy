import dgpy
import unittest
import logging

logger = logging.getLogger("dgpy")
logger.addHandler(logging.StreamHandler())


class UsageCase(unittest.TestCase):
    def testAddRemoveNodes(self):
        graph = dgpy.Graph()
        node1 = graph.addNode("node1", dgpy.VoidNode)
        self.assertEqual(len(graph.nodes), 1)
        graph.removeNode(node1)
        self.assertEqual(len(graph.nodes), 0)


class PushModelCase(unittest.TestCase):
    def __init__(self, *args):
        super(PushModelCase, self).__init__(*args)
        self.model = dgpy.PUSH

    def setUp(self):
        self.loggerLevel = logger.level
        logger.setLevel(logging.NOTSET)

    def tearDown(self):
        logger.setLevel(self.loggerLevel)

    def testSingleNodeEvaluation(self):
        graph = dgpy.Graph()
        graph.model = self.model

        node1 = graph.addNode("node1", dgpy.AddNode)
        node1.getInputPort("value1").value = 2
        node1.getInputPort("value2").value = 3
        self.assertEqual(node1.getOutputPort("result").value, 2+3)

        return graph

    def testModelIsolation(self):
        graph = dgpy.Graph()
        graph.model = None

        node1 = graph.addNode("node1", dgpy.AddNode)
        node1.getInputPort("value1").value = 2
        node1.getInputPort("value2").value = 3
        self.assertIsNone(node1.getOutputPort("result").value)

        return graph

    def testNodeConnections(self):
        graph = dgpy.Graph()
        graph.model = self.model

        node1 = graph.addNode("node1", dgpy.AddNode)
        node1.getInputPort("value1").value = 2
        node1.getInputPort("value2").value = 3

        node2 = graph.addNode("node2", dgpy.AddNode, value1=5)
        node2.getInputPort("value2").connect(node1.getOutputPort("result"))
        self.assertEqual(node2.getOutputPort("result").value, 5 + 5)

        return graph

    def testPersistentConnections(self):
        graph = dgpy.Graph()
        graph.model = self.model

        node1 = graph.addNode("node1", dgpy.AddNode)
        node1.getInputPort("value1").value = 2
        node1.getInputPort("value2").value = 3

        node2 = graph.addNode("node2", dgpy.AddNode, value1=5)
        node2.getInputPort("value2").connect(node1.getOutputPort("result"))
        self.assertEqual(node2.getOutputPort("result").value, 5 + 5)

        node1.getInputPort("value1").value = 10
        self.assertEqual(node2.getOutputPort("result").value, 5 + 13)

        return graph

    def testBranching(self):
        graph = self.testNodeConnections()

        node1 = graph.getNode("node1")

        node3 = graph.addNode("node3", dgpy.AddNode, value1=8)
        node3.getInputPort("value2").connect(node1.getOutputPort("result"))
        self.assertEqual(node3.getOutputPort("result").value, 8 + 5)

        return graph

    def testBranchingPersistence(self):
        graph = self.testBranching()

        node1 = graph.getNode("node1")
        node1.getInputPort("value1").value = 1
        self.assertEqual(node1.getOutputPort("result").value, 1 + 3)

        node3 = graph.getNode("node3")
        self.assertEqual(node3.getOutputPort("result").value, 8 + 4)

        node2 = graph.getNode("node2")
        self.assertEqual(node2.getOutputPort("result").value, 5 + 4)


class PullModelCase(PushModelCase):
    def __init__(self, *args):
        super(PullModelCase, self).__init__(*args)
        self.model = dgpy.PULL

    def testEvaluationCount(self):
        graph = self.testSingleNodeEvaluation()
        node1 = graph.getNode("node1")
        node1.getOutputPort("result").value
        self.assertEqual(node1.evalCount, 1)

if __name__ == '__main__':
    logger.setLevel(logging.DEBUG)
    unittest.main(verbosity=2)
