import json
from typing import Any, Dict, List, Optional
import time

class AIStreamProtocol:
    """
    Helper class to format messages according to the Vercel AI SDK Data Stream Protocol v1.
    Reference: https://sdk.vercel.ai/docs/ai-sdk-ui/stream-protocol#data-stream-protocol
    """
    
    @staticmethod
    def text(content: str) -> str:
        """
        Type 0: Text Part
        Format: 0:{string_content}
        """
        # Ensure proper JSON escaping for the string content
        return f'0:{json.dumps(content)}\n'

    @staticmethod
    def data(payload: Any) -> str:
        """
        Type 2: Data Part (Arbitrary JSON data)
        Format: 2:[{json_object}]
        
        The SDK expects an array of data objects for 'data' events.
        Use this for Widgets, Charts, and Status updates.
        """
        # We wrap the payload in a list as per protocol convention for 'data' parts
        return f'2:{json.dumps([payload])}\n'

    @staticmethod
    def tool_call(call_id: str, name: str, args: Dict[str, Any]) -> str:
        """
        Type 9: Tool Call Part
        Format: 9:{"toolCallId": "...", "toolName": "...", "args": {}}
        """
        payload = {
            "toolCallId": call_id,
            "toolName": name,
            "args": args
        }
        return f'9:{json.dumps(payload)}\n'
    
    @staticmethod
    def tool_result(call_id: str, tool_name: str, result: Any) -> str:
        """
        Type a: Tool Result Part
        Format: a:{"toolCallId": "...", "toolName": "...", "result": ...}
        """
        payload = {
            "toolCallId": call_id,
            "toolName": tool_name,
            "result": result
        }
        return f'a:{json.dumps(payload)}\n'

    @staticmethod
    def error(message: str) -> str:
        """
        Type 3: Error Part (or Type e in some contexts, but standardizing on text error usually safer)
        For now, we'll stream it as text to ensure visibility, or specific error protocol if supported.
        Let's use the 'finish_message' approach or just text for safety in this version.
        """
        return f'0:{json.dumps("Error: " + message)}\n'

    @staticmethod
    def trace(content: str, tool: Optional[str] = None, args: Optional[Dict[str, Any]] = None, result: Optional[Any] = None, duration: Optional[float] = None, type: str = "debug") -> str:
        """
        Type 2: Data Part (Trace Event)
        Format: 2:[{"type": "trace", "data": {...}}]
        """
        payload = {
            "type": "trace",
            "data": {
                "type": type,
                "content": content,
                "tool": tool,
                "args": args,
                "result": result,
                "duration": duration,
                "timestamp": str(time.time())
            }
        }
        return f'2:{json.dumps([payload])}\n'
