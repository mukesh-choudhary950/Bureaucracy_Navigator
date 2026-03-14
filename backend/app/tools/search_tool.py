import requests
from typing import Dict, Any, List
from app.tools.base import BaseTool, ToolResult
from app.core.config import settings
import json

class SearchTool(BaseTool):
    name = "search_tool"
    description = "Search for government information using SerpAPI"
    
    async def execute(self, query: str, num_results: int = 5) -> ToolResult:
        """Execute web search for government procedures and information"""
        try:
            url = "https://serpapi.com/search"
            params = {
                "api_key": settings.SERPAPI_KEY,
                "engine": "google",
                "q": query,
                "num": num_results,
                "hl": "en",
                "gl": "in"  # India-specific results
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract relevant information
            results = []
            if "organic_results" in data:
                for result in data["organic_results"][:num_results]:
                    results.append({
                        "title": result.get("title", ""),
                        "link": result.get("link", ""),
                        "snippet": result.get("snippet", ""),
                        "position": result.get("position", 0)
                    })
            
            # Check for knowledge graph results
            knowledge_graph = None
            if "knowledge_graph" in data:
                knowledge_graph = {
                    "title": data["knowledge_graph"].get("title", ""),
                    "description": data["knowledge_graph"].get("description", ""),
                    "source": data["knowledge_graph"].get("source", {}).get("name", "")
                }
            
            return ToolResult(
                success=True,
                data={
                    "query": query,
                    "results": results,
                    "knowledge_graph": knowledge_graph,
                    "total_results": len(results)
                },
                metadata={"search_engine": "google", "region": "india"}
            )
            
        except requests.RequestException as e:
            return ToolResult(
                success=False,
                error=f"Search request failed: {str(e)}"
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Search tool error: {str(e)}"
            )
    
    def get_parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query for government procedures or information"
                },
                "num_results": {
                    "type": "integer",
                    "description": "Number of search results to return",
                    "default": 5
                }
            },
            "required": ["query"]
        }
