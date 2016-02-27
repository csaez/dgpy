# dgpy

`dgpy` is a generic dependency graph implemented in python, coded live, 10
minutes at a time, in a test-driven development fashion.

You can watch the playlist on
[youtube](https://youtu.be/pXUL_aDhN-Y?list=PLYcUacEjhPL-nSolgfdIJ_GqBakUp790z)
and read more about the motivations behind this project at
[cesarsaez.me](http://cesarsaez.me).


## Features

In terms of features, `dgpy` implements a **null/void node supporting input and
output ports/plugs** as a base for user specialization, a **push and/or pull
evaluation model** (you can mix it as the model get set per node) and
**serialization** allowing to save and load graphs (reference counting is done
during import, so the *serialized data is hack-able*).


## Usage

There's no much to document as `dgpy` doesn't include any builtin node or data
type in order to keep it away from any domain specific task, however there's a
very simple `AddNode` implemented in the test suite that could serve as an
example (and was used all over the place to drive the development).

Here's a selection of snippets from the test suite showcasing how to get things
started.

```python
import dgpy

# Let's implement a simple node
class AddNode(dgpy.VoidNode):
    def initPorts(self):
        super(AddNode, self).initPorts()
        self.addInputPort("value1")
        self.addInputPort("value2")
        self.addOutputPort("result")

    def evaluate(self):
        super(AddNode, self).evaluate()
        result = 0
        for p in self._inputPorts.values():
            if p.value is not None:
                result += p.value
        self.getOutputPort("result").value = result

dgpy.registerNode("AddNode", AddNode)


# Let's create a network
graph = dgpy.Graph()
graph.model = dgpy.PULL

node1 = graph.addNode("node1", AddNode, value1=2, value2=3)
node2 = graph.addNode("node2", AddNode, value1=5)
node2.getInputPort("value2").connect(node1.getOutputPort("result"))

print node2.getOutputPort("result").value  # 5 + 5

node1.getInputPort("value1").value = 10

print node2.getOutputPort("result").value  # 13 + 5


# Let's play with the serialization
data = graph.serialize()
clone = dgpy.Graph.fromData(data)
```

> Check `tests.py` for more snippets of usage.


## Testing

This project uses `unittest` as testing framework (python std library), I'm
pretty sure every python developers out there have good reasons to prefer any
of the alternatives available but I wanted to keep it simple/accesible to
everyone without forcing dependencies.

Coverage at the time this readme was written is 100%, but you can check it by
running the test suite.

```
pip install coverage

coverage run --source=dgpy -m unittest discover
coverage report
```
