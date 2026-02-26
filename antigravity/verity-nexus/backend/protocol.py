import json
from typing import Any, Optional

class AIStreamProtocol:
    """
    Enforces the 'Zero-Parsing' AI architecture (Vercel AI SDK compatible).
    """
    @staticmethod
    def text(content: str) -> str:
        """Type 0: Text Part"""
        return f'0:{json.dumps(content)}\n'

    @staticmethod
    def data(payload: Any) -> str:
        """Type 2: Data Part (Widgets, Charts). Must be a list."""
        return f'2:{json.dumps([payload])}\n'

    @staticmethod
    def tool_call(call_id: str, name: str, args: dict) -> str:
        """Type 9: Tool Call"""
        payload = {"toolCallId": call_id, "toolName": name, "args": args}
        return f'9:{json.dumps(payload)}\n'

    @staticmethod
    def tool_result(call_id: str, result: Any) -> str:
        """Type a: Tool Result"""
        payload = {"toolCallId": call_id, "result": result}
        return f'a:{json.dumps(payload)}\n'

    @staticmethod
    def error(message: str) -> str:
        """Type 3: Error Part"""
        return f'3:{json.dumps(message)}\n'
