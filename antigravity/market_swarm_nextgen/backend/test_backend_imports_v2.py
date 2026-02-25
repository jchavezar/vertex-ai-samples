try:
    from google.genai.types import Content, Part
    from google.adk.agents import Agent
    import src.report_agent
    print("IMPORTS_OK")
except ImportError as e:
    print(f"IMPORT_ERROR: {e}")
except Exception as e:
    print(f"GENERAL_ERROR: {e}")
