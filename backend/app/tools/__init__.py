from .base import BaseTool, ToolResult
from .search_tool import SearchTool
from .scraper_tool import ScraperTool
from .document_parser import DocumentParserTool
from .form_generator import FormGeneratorTool
from .reminder_tool import ReminderTool
from .status_tracker import StatusTrackerTool

# Tool registry
AVAILABLE_TOOLS = {
    "search_tool": SearchTool(),
    "scraper_tool": ScraperTool(),
    "document_parser": DocumentParserTool(),
    "form_generator": FormGeneratorTool(),
    "reminder_tool": ReminderTool(),
    "status_tracker": StatusTrackerTool()
}

def get_tool(tool_name: str) -> BaseTool:
    """Get tool instance by name"""
    if tool_name not in AVAILABLE_TOOLS:
        raise ValueError(f"Tool '{tool_name}' not available")
    return AVAILABLE_TOOLS[tool_name]

def list_available_tools() -> list:
    """List all available tools"""
    return list(AVAILABLE_TOOLS.keys())
