
import os
import uvicorn
import nest_asyncio

# Apply patches early
# Apply patches early
import src.factset_core
print(f"DEBUG: src.factset_core imported from {src.factset_core.__file__}")
import sys
print(f"DEBUG: sys.path: {sys.path}")

if __name__ == "__main__":
    import logging
    # SILENCE THE BUGGY LOGGER (Just in case)
    logging.getLogger("google.adk.models.google_llm").setLevel(logging.CRITICAL)
    
    # MONKEY PATCH google.genai.types.Tool
    # The ADK logger crashes because it treats Tool as FunctionDeclaration.
    # FIXED: src/smart_agent.py now returns FunctionDeclaration directly.
    pass

    try:
        import google.ai.generativelanguage as gl
        if hasattr(gl, "Tool") and not hasattr(gl.Tool, "parameters"):
            print("Applying Monkey Patch to google.ai.generativelanguage.Tool...")
            @property
            def mock_parameters_gl(self):
                 class Mock:
                    def __getattr__(self, name):
                        return {} if name == "properties" else self
                    @property
                    def properties(self):
                        return {}
                 return Mock()
            gl.Tool.parameters = mock_parameters_gl
            gl.Tool.parameters_json_schema = mock_parameters_gl
            gl.Tool.response = mock_parameters_gl
    except ImportError:
        pass
    except Exception as e:
        print(f"Failed to patch google.ai.generativelanguage.Tool: {e}")

    nest_asyncio.apply()
    port = int(os.getenv("PORT", 8001))
    print(f"Starting Uvicorn via run_backend.py on port {port} with patches applied...")
    uvicorn.run("src.main:app", host="0.0.0.0", port=port, reload=False, log_level="info")
