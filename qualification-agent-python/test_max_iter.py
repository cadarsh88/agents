from strands import Agent
print("Agent init signature:")
print(Agent.__init__.__doc__)
import inspect
print("\nAgent __init__ parameters:")
sig = inspect.signature(Agent.__init__)
for param in sig.parameters:
    print(f"  - {param}")
