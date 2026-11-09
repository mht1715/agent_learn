from typing import List

from langchain_core.tools import BaseTool

from app.agent.tools.builtin import get_weather, get_order_status
from app.agent.tools.rag_tool import search_knowledge_base

TOOLS: List[BaseTool] = [get_weather, get_order_status, search_knowledge_base]
TOOL_MAP: dict[str, BaseTool] = {
    t.name: t
    for t in TOOLS
}
