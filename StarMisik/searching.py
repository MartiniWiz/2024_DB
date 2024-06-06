import sys
import requests
from bs4 import BeautifulSoup

def search_bing(query):
    bing_search_url = f"https://www.bing.com/search?q=site:tabelog.com+{query}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    response = requests.get(bing_search_url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        first_link_tag = soup.select_one('#b_results a')
        if first_link_tag and 'href' in first_link_tag.attrs:
            return first_link_tag['href']
    return None

if __name__ == "__main__":
    query = sys.argv[1]
    result = search_bing(query)
    if result:
        print(result)
    else:
        print("No result found")
