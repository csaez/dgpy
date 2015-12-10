import dgpy
import unittest


class UsageCase(unittest.TestCase):
    def testBaseClasses(self):
        graph = dgpy.Graph()
        node = graph.addNode(dgpy.VoidNode)
        self.assertEqual(len(graph.nodes), 1)
        graph.removeNode(node)
        self.assertEqual(len(graph.nodes), 0)

    def testAddNode(self):
        graph = dgpy.Graph()
        node = graph.addNode(dgpy.AddNode)
        node.getInputPort("value1").value = 2
        node.getInputPort("value2").value = 3
        node.evaluate()
        self.assertEqual(node.getOutputPort("result").value, 2+3)

    def testAddNodeConnections(self):
        graph = dgpy.Graph()

        node1 = graph.addNode(dgpy.AddNode)
        node1.getInputPort("value1").value = 5
        node1.getInputPort("value2").value = 10
        node1.evaluate()

        node2 = graph.addNode(dgpy.AddNode)
        node2.getInputPort("value1").value = 5
        node2.getInputPort("value2").connect(node1.getOutputPort("result"))
        node2.evaluate()

        self.assertEqual(node2.getOutputPort("result").value, 20)


if __name__ == '__main__':
    unittest.main(verbosity=2)
