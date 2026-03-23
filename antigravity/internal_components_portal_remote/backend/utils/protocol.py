import json
from typing import Any

class AIStreamProtocol:
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
