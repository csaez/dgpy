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


if __name__ == '__main__':
    unittest.main(verbosity=2)
