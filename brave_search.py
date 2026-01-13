from dotenv import load_dotenv
import requests
import os

load_dotenv()

BRAVE_KEY=os.getenv("BRAVE_API_KEY")

url = "https://api.search.brave.com/res/v1/web/search"


def search(user_query: str) -> dict:

    params = {
        "q": user_query
    }

    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "X-Subscription-Token": BRAVE_KEY,
    }

    response = requests.get(url, params=params, headers=headers)
    return response.json()


def extract_info(raw_json: dict, limit=5) -> list[dict]:
    """Extract url, source, snippet, and title from raw Brave search JSON"""
    results = []

    # Check if web results exist
    web_results = raw_json.get("web", {}).get("results", [])
    for item in web_results[:limit]:
        results.append({
            "title": item.get("title"),
            "url": item.get("url"),
            "source": item.get("profile", {}).get("name"),  # Brave stores source under profile->name
            "snippet": item.get("description", "")
        })

    return results


# test case
if __name__ == "__main__":
    raw = search("What are the leading cuases of cancer?")
    processed = extract_info(raw)
    print(processed)