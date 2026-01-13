from brave_search import search, extract_info
from fastmcp import FastMCP
from urllib.parse import urlparse

mcp = FastMCP("Research MCP Server")

# search
@mcp.tool
def brave_search_tool(query: str) -> list[dict]:
    """Calls Brave Search MCP"""
    raw = search(query)
    return extract_info(raw)

# relevance scoring
@mcp.tool
def relevance_scoring(results: list[dict]) -> list[dict]:
    """
    Rank search results by source sophistication.
    Adds a `source_score` field and returns results sorted by score.
    """

    def score_from_domain(url: str) -> float:
        if not url:
            return 0.5

        domain = urlparse(url).netloc.lower()

        if domain.endswith(".gov"):
            return 1.0
        elif domain.endswith(".edu"):
            return 0.9
        elif domain.endswith(".org"):
            return 0.8
        elif domain.endswith(".com"):
            return 0.7
        else:
            return 0.6

    for item in results:
        url = item.get("url", "")
        item["source_score"] = score_from_domain(url)

    # Sort by source_score (highest first)
    results.sort(key=lambda x: x["source_score"], reverse=True)

    return results

# summary