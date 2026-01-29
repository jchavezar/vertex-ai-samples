import logging
import asyncio
import inspect
from typing import Any, Optional, Dict
from google.adk.tools.base_tool import BaseTool
from google.genai import types

logger = logging.getLogger("tool_utils")

class DelegatingTool(BaseTool):
    @property
    def parameters(self):
        """
        Hack to satisfy google.adk.models.google_llm._build_function_declaration_log
        which expects a 'parameters' attribute with a 'properties' attribute.
        """
        class MockParams:
            @property
            def properties(self):
                return {}
        return MockParams()

    def __init__(self, target_tool, schema_override=None, observer=None):
        name = getattr(target_tool, "name", getattr(target_tool, "__name__", "UNKNOWN"))
        description = getattr(target_tool, "description", getattr(target_tool, "__doc__", ""))
        super().__init__(name=name, description=description)
        
        self._target = target_tool
        self._observer = observer
        
        # Set Schema
        if schema_override:
            self.input_schema = schema_override
        elif hasattr(target_tool, "input_schema"):
            self.input_schema = target_tool.input_schema
        else:
            # AUTO-GENERATE SCHEMA FROM SIGNATURE
            try:
                import inspect
                sig = inspect.signature(target_tool)
                properties = {}
                required = []
                for p_name, param in sig.parameters.items():
                    if p_name in ["args", "kwargs"]: continue
                    
                    # Basic type mapping
                    p_type = "string"
                    if param.annotation == int: p_type = "integer"
                    elif param.annotation == float: p_type = "number"
                    elif param.annotation == bool: p_type = "boolean"
                    elif param.annotation == list: p_type = "array"
                    elif param.annotation == dict: p_type = "object"
                    
                    properties[p_name] = {"type": p_type}
                    if param.default == inspect.Parameter.empty:
                        required.append(p_name)
                
                self.input_schema = {
                    "type": "object",
                    "properties": properties,
                    "required": required if required else None
                }
                # Clean up None required
                if not self.input_schema["required"]:
                    del self.input_schema["required"]
                
                logger.debug(f"Auto-generated schema for {name}: {self.input_schema}")
            except Exception as e:
                logger.warning(f"Failed to auto-generate schema for {name}: {e}")
                self.input_schema = {"type": "object", "properties": {}}

    def _get_declaration(self):
        try:
             from google.genai import types
             return types.FunctionDeclaration(
                 name=self.name,
                 description=self.description,
                 parameters=self.input_schema 
             )
        except Exception as e:
            logger.error(f"DelegatingTool Declaration Error: {e}")
            raise e

    async def run_async(self, *args, **kwargs):
        try:
            # 1. Determine the actual method to call
            # If target has run_async (BaseTool), use it.
            # Otherwise use target itself if it's a coroutine or callable.
            method = self._target
            if hasattr(self._target, "run_async"):
                method = self._target.run_async
            elif hasattr(self._target, "run"):
                method = self._target.run
            
            # Inspect signature to decide on unpacking and filtering
            should_unpack = True
            allowed_keys = None 
            
            try:
                sig = inspect.signature(method)
                params = sig.parameters
                
                # If target explicitly accepts 'args', do NOT unpack properties into kwargs
                if "args" in params:
                    should_unpack = False
                
                # Determine allowed keys for filtering
                has_var_keyword = any(p.kind == inspect.Parameter.VAR_KEYWORD for p in params.values())
                if not has_var_keyword:
                    allowed_keys = set(params.keys())
            except Exception as e:
                logger.warning(f"Signature inspection failed for {self.name}: {e}")

            # Smart Unpacking (Vertex AI specific)
            if "args" in kwargs and isinstance(kwargs["args"], dict):
                if should_unpack:
                    tool_args = kwargs.pop("args")
                    kwargs.update(tool_args)
            
            # Filter KWARGS
            if allowed_keys is not None:
                kwargs = {k: v for k, v in kwargs.items() if k in allowed_keys}

            # Execute
            if asyncio.iscoroutinefunction(method):
                 res = await method(*args, **kwargs)
            else:
                 # It might be an async method that inspect doesn't detect?
                 # Or just a regular callable.
                 res = method(*args, **kwargs)
                 if asyncio.iscoroutine(res):
                      res = await res

            # Observe
            if self._observer:
                 try:
                     if asyncio.iscoroutinefunction(self._observer):
                         await self._observer(self.name, args, kwargs, res)
                     else:
                         self._observer(self.name, args, kwargs, res)
                 except Exception as oe:
                     logger.error(f"Observer Error: {oe}")
            return res
            
        except Exception as e:
            # Observe Error
            if self._observer:
                 try:
                     err_res = f"Error: {e}"
                     if asyncio.iscoroutinefunction(self._observer):
                         await self._observer(self.name, args, kwargs, err_res)
                     else:
                         self._observer(self.name, args, kwargs, err_res)
                 except: pass
            raise e

    def __call__(self, *args, **kwargs):
        raise NotImplementedError("Sync execution not supported in this wrapper")
