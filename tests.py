import dgpy
import unittest


class UsageCase(unittest.TestCase):
    def testBaseClasses(self):
        graph = dgpy.Graph()
        node = graph.addNode(dgpy.VoidNode)
        self.assertEqual(len(graph.nodes), 1)
        graph.removeNode(node)
        self.assertEqual(len(graph.nodes), 0)

if __name__ == '__main__':
    unittest.main(verbosity=2)
