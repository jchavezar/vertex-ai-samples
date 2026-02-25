
import sys
import os

# Add backend and vendor to path
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), 'backend'))
sys.path.append(os.path.join(os.getcwd(), 'backend', 'vendor'))

try:
    from backend.agent_pkg import agent
    print("Import successful")
    interceptor = agent.GEMINIPayloadInterceptor()
    print("Instantiation successful")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
