import os
import requests
from langchain.tools import tool
from bs4 import BeautifulSoup
from tavily import TavilyClient
from dotenv import load_dotenv
from rich import print

load_dotenv()

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


@tool
def web_search(query: str) -> str:
    """Search the web for recent and reliable information on a topic and return Titles, URLs and snippets."""
    
    print("web_search called")

    search_result = tavily.search(query=query, max_results=5)
    
    print(search_result)
    
    extract_details = []
    
    for r in search_result['results']:
        extract_details.append(
            f"Title : {r['title']}\n URL : {r['url']}\n snippet : {r['content'][:300]}\n "
        )
    return "\n ------ \n".join(extract_details)


@tool
def scrape_url(url: str) -> str:
    """Scrape and return clean text content from a given URL for deeper reading."""
    try:
        resp = requests.get(url, timeout=8, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()
        return soup.get_text(separator=" ", strip=True)[:3000]
    except Exception as e:
        return f"Could not scrape URL: {str(e)}"