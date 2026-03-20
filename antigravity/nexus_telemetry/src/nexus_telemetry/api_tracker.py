import typing
from fastapi import Request
from starlette.types import ASGIApp, Receive, Scope, Send, Message
from .client import _default_client

class NexusAPITrackerMiddleware:
    """
    Pure ASGI middleware to intercept all API outputs (streaming and static) without 
    blocking the primary application event loop. Perfect zero-latency observability.
    """
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        method = scope.get("method", "UNKNOWN")
        path = scope.get("path", "UNKNOWN")
        query_string = scope.get("query_string", b"").decode("utf-8")
        url = f"{path}?{query_string}" if query_string else path

        # This send wrapper allows us to intercept the ASGI messages going OUT to the client
        async def intercept_send(message: Message) -> None:
            if message["type"] == "http.response.body":
                body = message.get("body", b"")
                if body:
                    try:
                        decoded_body = body.decode("utf-8")
                        # Ship it asynchronously via the non-blocking queue
                        _default_client._queue.put_nowait({
                            "tag": "api_output",
                            "event": {
                                "method": method,
                                "url": url,
                                "response_chunk": decoded_body
                            }
                        })
                    except Exception:
                        pass # Ignore decode errors for binary data / avoid crashing
            await send(message)

        await self.app(scope, receive, intercept_send)
