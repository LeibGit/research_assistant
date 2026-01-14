from brave_search import search, extract_info, extract_article_text
from fastmcp import FastMCP
from urllib.parse import urlparse
import requests


mcp = FastMCP("Research MCP Server")

# search
#@mcp.tool
def brave_search_tool(query: str) -> list[dict]:
    """Calls Brave Search MCP"""
    raw = search(query)
    return extract_info(raw)

# relevance scoring
#@mcp.tool
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
#@mcp.tool
def summarize_text(text: str, max_words: int = 200) -> str:
    prompt = f"""
    Summarize the following text clearly and concisely.
    Focus on factual information.
    Limit the summary to approximately {max_words} words.

    TEXT:
    {text}
    """

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3",
            "prompt": prompt,
            "stream": False,
        },
        timeout=60,
    )

    response.raise_for_status()
    return response.json()["response"]


#@mcp.tool
def format_research_report(
    query: str,
    results: list[dict],
    max_words: int = 300
) -> str:
        
    prompt = f"""
        You are a research assistant.

        User query:
        "{query}"

        You are given a list of sources already ranked by reliability.
        Each source contains:
        - title
        - url
        - snippet
        - source
        - source_score (0–1)

        Tasks:
        1. Briefly summarize the overall findings.
        2. List sources in descending order of reliability.
        3. For each source, show:
        - Title
        - Source score
        - One-sentence relevance explanation
        4. Cite all sources clearly.

        Limit output to ~{max_words} words.
        Be factual. No speculation.

        DATA:
        {results}
        """

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3.2:latest",
            "prompt": prompt,
            "stream": False,
        },
        timeout=60,
    )

    response.raise_for_status()
    return response.json()["response"]
if __name__ == "__main__":
    mcp.run(transport="stdio")