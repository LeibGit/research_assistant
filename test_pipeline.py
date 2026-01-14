from brave_search import search, extract_info
from main import relevance_scoring, format_research_report


query = "What is the leading causes of cancer?"


raw = search(query)
processed = extract_info(raw)
scored = relevance_scoring(processed)

report = format_research_report(
    query=query,
    results=scored
)
print("loading your summary...")
print(report)