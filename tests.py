import dgpy
import unittest
import logging


class UsageCase(unittest.TestCase):
    def testBaseClasses(self):
        graph = dgpy.Graph()
        node = graph.addNode("node", dgpy.VoidNode)
        self.assertEqual(len(graph.nodes), 1)
        graph.removeNode(node)
        self.assertEqual(len(graph.nodes), 0)

    def testAddNode(self):
        graph = dgpy.Graph()
        node = graph.addNode("node", dgpy.AddNode)
        node.getInputPort("value1").value = 2
        node.getInputPort("value2").value = 3
        self.assertEqual(node.getOutputPort("result").value, 2+3)

    # def testAddNodeConnections(self):
        # graph = dgpy.Graph()

        # node1 = graph.addNode("node1", dgpy.AddNode, value1=5, value2=10)
        # node1.evaluate()

        # node2 = graph.addNode("node2", dgpy.AddNode, value1=5)
        # node2.getInputPort("value2").connect(node1.getOutputPort("result"))
        # node2.evaluate()

        # self.assertEqual(node2.getOutputPort("result").value, 20)

        # return graph

    # def testGetNodesFromGraph(self):
        # graph = self.testAddNodeConnections()

        # node1 = graph.getNode("node1")
        # node1.getInputPort("value1").value = 10
        # node1.evaluate()
        # self.assertEqual(node1.getOutputPort("result").value, 10 + 10)

        # node2 = graph.getNode("node2")
        # node2.evaluate()

        # self.assertEqual(node2.getOutputPort("result").value, 25)


if __name__ == '__main__':
    logger = logging.getLogger("dgpy")
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.DEBUG)
    unittest.main(verbosity=2)
