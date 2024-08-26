import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time

def fetch_article_content(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        content_div = soup.find('div', class_='sp-cn ins_storybody')
        if content_div:
            paragraphs = content_div.find_all('p')
            content = ' '.join([p.get_text(strip=True) for p in paragraphs])
            return content
        print(f"Content not found for {url}")
        return None
    except Exception as e:
        print(f"Error fetching content from {url}: {e}")
        return None

def scrape_headlines_and_content(base_url):
    response = requests.get(base_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    headlines = soup.find_all('h3', class_='LstWg1_tx mb-0 pip_fix')
    
    articles = []
    for headline in headlines:
        title_elem = headline.find('a', class_='crd_ttl8')
        if title_elem:
            title = title_elem.get_text(strip=True)
            link = title_elem['href']
            if not link.startswith('http'):
                link = base_url + link  # Handle relative URLs
            
            content = fetch_article_content(link)
            if content:
                articles.append({
                    'title': title,
                    'link': link,
                    'content': content,
                    'date': datetime.now().strftime('%Y-%m-%d')
                })
            time.sleep(1)  # Add a small delay between requests
    return articles

def main():
    base_url = 'https://www.ndtv.com/'
    articles = scrape_headlines_and_content(base_url)
    
    df = pd.DataFrame(articles)
    df.to_csv('articles.csv', index=False)
    print("Data successfully written to CSV.")

if __name__ == "__main__":
    main()
