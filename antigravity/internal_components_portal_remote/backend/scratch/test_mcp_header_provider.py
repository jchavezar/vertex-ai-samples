import unittest
import sys
import os

# Add backend dir to path
backend_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(backend_dir)

from agents.agent import mcp_header_provider

class MockState(dict):
    pass

class MockSession:
    def __init__(self, state):
        self.state = state

class MockReadonlyContext:
    def __init__(self, session=None):
        if session:
            self.session = session

class TestMcpHeaderProvider(unittest.TestCase):
    def test_extracts_token_from_state(self):
        # Create a mock state with a token-like string (eyJ...)
        mock_state = MockState({
            "user_jwt": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.e30.s7tX..."
        })
        mock_session = MockSession(state=mock_state)
        mock_context = MockReadonlyContext(session=mock_session)
        
        # Clear env to force fallback failure if state read fails
        if "USER_TOKEN" in os.environ:
             del os.environ["USER_TOKEN"]

        headers = mcp_header_provider(mock_context)
        
        self.assertIn("Authorization", headers)
        self.assertEqual(headers["Authorization"], "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.e30.s7tX...")
        print("✅ Success: Token extracted from session state correctly.")

    def test_fallback_to_local_auth(self):
         # Create a context with NO state token
         mock_context = MockReadonlyContext()
         
         # Mock the get_user_token to return something known
         # We can inject into env or verify standard path.
         # For simplicity, we just set USER_TOKEN in env to force the local fallback
         os.environ["USER_TOKEN"] = "local_mock_token_123"
         
         headers = mcp_header_provider(mock_context)
         self.assertIn("Authorization", headers)
         self.assertEqual(headers["Authorization"], "Bearer local_mock_token_123")
         print("✅ Success: Fallback to local auth context correctly triggers execution.")

if __name__ == "__main__":
    unittest.main()
