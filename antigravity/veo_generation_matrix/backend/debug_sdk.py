import vertexai
from vertexai.preview import reasoning_engines

print("Agent Engines methods:")
print(dir(reasoning_engines.ReasoningEngine))

# Let's also check if there's an update method
import inspect
if hasattr(reasoning_engines.ReasoningEngine, 'update'):
    print("\nUpdate method signature:")
    print(inspect.signature(reasoning_engines.ReasoningEngine.update))
    print(inspect.getdoc(reasoning_engines.ReasoningEngine.update))
