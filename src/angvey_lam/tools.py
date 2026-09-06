"""Tool registry — decorator + metadata for agent-callable functions."""

from __future__ import annotations

import inspect
from dataclasses import dataclass
from typing import Any, Callable, Optional


@dataclass
class ToolSpec:
    name: str
    description: str
    fn: Callable[..., Any]
    parameters: dict[str, Any]
    is_write: bool = False


def tool(
    name: Optional[str] = None,
    description: str = "",
    *,
    is_write: bool = False,
) -> Callable:
    """Register a Python function as an agent tool."""

    def decorator(fn: Callable) -> Callable:
        tool_name = name or fn.__name__
        sig = inspect.signature(fn)
        params: dict[str, Any] = {"type": "object", "properties": {}, "required": []}
        for pname, param in sig.parameters.items():
            if pname in ("self", "cls"):
                continue
            ptype = "string"
            ann = param.annotation
            if ann is int:
                ptype = "integer"
            elif ann is float:
                ptype = "number"
            elif ann is bool:
                ptype = "boolean"
            params["properties"][pname] = {"type": ptype}
            if param.default is inspect.Parameter.empty:
                params["required"].append(pname)

        fn._angvey_tool = ToolSpec(
            name=tool_name,
            description=description or (fn.__doc__ or tool_name),
            fn=fn,
            parameters=params,
            is_write=is_write,
        )
        return fn

    return decorator


def collect_tools(obj: Any) -> dict[str, ToolSpec]:
    tools: dict[str, ToolSpec] = {}
    for attr_name in dir(obj):
        if attr_name.startswith("_"):
            continue
        try:
            attr = getattr(obj, attr_name)
        except Exception:
            continue
        spec = getattr(attr, "_angvey_tool", None)
        if isinstance(spec, ToolSpec):
            tools[spec.name] = spec
    return tools
