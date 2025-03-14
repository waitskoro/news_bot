import time

import requests
from bs4 import BeautifulSoup


url = 'https://www.interfax.ru/'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

def get_soup():
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return BeautifulSoup(response.text, 'html.parser')
    except Exception as e:
        print(f"Ошибка при получении данных: {e}")
        return None

def print_unique_section(title, items):
    print(f"\n=== {title.upper()} ===")
    seen = set()
    for item in items:
        if item not in seen:
            seen.add(item)
            print(f"- {item}")

def process_news_block(block, selector):
    if not block:
        return []
    return [elem.text.strip() for elem in block.select(selector) if elem.text.strip()]

def process_timeline_news(items):
    processed = set()
    news_items = []

    for item in items:
        if should_skip(item):
            continue

        time_tag, title = get_news_metadata(item)
        if not title:
            continue

        text = title.text.strip()
        if text in processed:
            continue

        processed.add(text)
        time = extract_time(time_tag)
        news_items.append(f"[{time}] {text}")

    return news_items

def should_skip(item):
    classes = item.get('class', [])
    return (
            any(cls in classes for cls in ['no__dot', 'wr__timeline']) or
            'ban' in item.get('id', '')
    )

def get_news_metadata(item):
    if 'timeline__group' in item.get('class', []):
        subitems = item.find_all('div')
        return next(
            ((subitem.find('time'), subitem.find('h3')) for subitem in subitems if subitem.find('time')),
            (None, None)
        )
    return item.find('time'), item.find('h3')

def extract_time(time_tag):
    return time_tag['datetime'].split('T')[1][:5] if time_tag else '--:--'

def parse_interfax():
    soup = get_soup()
    if not soup:
        return

    # Главные новости
    main_block = soup.find('div', class_='newsmain')
    main_news = process_news_block(main_block, 'a h3') if main_block else []
    print_unique_section('ГЛАВНЫЕ НОВОСТИ', main_news)

    # Последние новости
    timeline = soup.find('div', class_='timeline')
    timeline_news = process_timeline_news(timeline.find_all(True)) if timeline else []
    print_unique_section('ПОСЛЕДНИЕ НОВОСТИ', timeline_news)

    # Самое читаемое
    mr_block = soup.find('div', class_='rcMR')
    popular_news = process_news_block(mr_block, 'a.rcMR_nlink h3') if mr_block else []
    print_unique_section('САМОЕ ЧИТАЕМОЕ', popular_news)

if __name__=="__main__":

    while True:
        parse_interfax()
        time.sleep(60 * 3)
