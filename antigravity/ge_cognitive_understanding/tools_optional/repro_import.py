
import sys
import os

# Simulate agent.py logic
current_dir = os.getcwd()
vendor_path = os.path.join(current_dir, "backend", "vendor")
sys.path.insert(0, vendor_path)

print(f"Added {vendor_path} to sys.path")
try:
    import google.adk
    print("Successfully imported google.adk")
    print(f"google.adk file: {google.adk.__file__}")
except ImportError as e:
    print(f"Failed to import google.adk: {e}")

try:
    from google.adk.agents import BaseAgent
    print("Successfully imported BaseAgent")
except ImportError as e:
    print(f"Failed to import BaseAgent: {e}")
