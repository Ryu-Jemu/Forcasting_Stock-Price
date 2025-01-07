import time
import random
from bs4 import BeautifulSoup
import requests
import re
import datetime
import pandas as pd
from tqdm import tqdm

# Setting Page Numbers
def makePgNum(num):
    return (num - 1) * 10 + 1

# Generate Each Page
def makeUrl(search, start_pg, end_pg):
    urls = []
    for i in range(start_pg, end_pg + 1):
        page = makePgNum(i)
        url = f"https://search.naver.com/search.naver?where=news&sm=tab_pge&query={search}&start={page}"
        urls.append(url)
    return urls

# Crawling function
def articles_crawler(url):
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36"
            ),
            "Referer": "https://www.naver.com",
        }
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            raise Exception(f"HTTP request failed with status code {response.status_code}")
        html = BeautifulSoup(response.text, "html.parser")
        url_naver = html.select("div.group_news > ul.list_news > li div.news_area > div.news_info > div.info_group > a.info")
        return [i.attrs['href'] for i in url_naver if "news.naver.com" in i.attrs['href']]
    except Exception as e:
        print(f"Error in articles_crawler: {e}")
        return []
    
def extract_news_content(url):
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36"
            ),
            "Referer": "https://www.naver.com",
        }
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            raise Exception(f"HTTP request failed with status code {response.status_code}")
        html = BeautifulSoup(response.text, "html.parser")

        title = html.select_one("#ct > div.media_end_head.go_trans > div.media_end_head_title > h2")
        if not title:
            title = html.select_one("#content > div.end_ct > div > h2")
        title = re.sub('<[^>]*>', '', str(title)).strip()

        content = html.select("article#dic_area")
        if not content:
            content = html.select("#articeBody")
        content = ''.join(re.sub('<[^>]*>', '', str(c)).strip() for c in content)

        date_elem = html.select_one("div#ct > div.media_end_head.go_trans > div.media_end_head_info.nv_notrans > div.media_end_head_info_datestamp > div > span")
        if date_elem:
            date = date_elem.attrs.get('data-date-time', '').strip()
        else:
            date = None

        return title, content, date
    except Exception as e:
        print(f"Error extracting content from {url}: {e}")
        return None, None, None
    
def main():
    keywords = input("Enter 5 search keywords separated by commas: ").split(',')
    # 모든 키워드의 공백 제거 후, 빈 문자열 제거
    keywords = [kw.strip() for kw in keywords]
    # 중간에 빈 키워드가 있다면 이를 사용자에게 명확히 알림
    if len(keywords) != 5 or '' in keywords:
        print(f"Invalid input. You entered: {keywords}")
        print("Please enter exactly 5 valid keywords separated by commas.")
        return

    try:
        start_page = int(input("Enter start page (e.g., 1): "))
        end_page = int(input("Enter end page (e.g., 20): "))
    except ValueError:
        print("Invalid page number. Please enter an integer.")
        return

    news_data = []

    for search in keywords:
        print(f"\nCrawling for keyword: {search}")
        urls = makeUrl(search, start_page, end_page)
        all_urls = []

        for url in tqdm(urls, desc=f"Fetching URLs for {search}"):
            all_urls.extend(articles_crawler(url))
            time.sleep(random.uniform(1, 3))
            
         # Remove duplicate URLs
        all_urls = list(set(all_urls))

        for url in tqdm(all_urls, desc=f"Crawling articles for {search}"):
            title, content, date = extract_news_content(url)
            time.sleep(random.uniform(1, 3))
            if title and content and date:
                news_data.append({'keyword': search, 'date': date, 'title': title, 'link': url, 'content': content})

    if news_data:
        news_df = pd.DataFrame(news_data)
        news_df = news_df.drop_duplicates(subset=['title'], keep='first', ignore_index=True)

        filename = "crawled_news.csv"
        news_df.to_csv(filename, encoding='utf-8-sig', index=False)
        print(f"Saved {len(news_df)} articles to {filename}")
    else:
        print("No data crawled. Please check your inputs and try again.")

if __name__ == "__main__":
    main()