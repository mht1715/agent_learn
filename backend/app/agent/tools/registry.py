from typing import List

from langchain_core.tools import BaseTool

from app.agent.tools.builtin import get_weather, get_order_status

TOOLS: List[BaseTool] = [get_weather, get_order_status]
TOOL_MAP: dict[str, BaseTool] = {
    t.name: t
    for t in TOOLS
}
