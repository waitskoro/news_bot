from datetime import datetime

import dateparser
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class Interfax:
    def __init__(self, url, db):
        self.url = url
        self.db = db

    def scraping(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

        driver = webdriver.Chrome(options=options)
        driver.get(self.url)
        try:
            wait = WebDriverWait(driver, 15)

            wait.until(EC.presence_of_element_located(
                (By.XPATH, '//div[contains(@class, "timeline")]')
            ))

            news_blocks = driver.find_elements(By.XPATH,
                                                    '//div[contains(@class, "timeline")]/div[contains(@class, "timeline__text")] | '
                                                    '//div[contains(@class, "timeline")]/div[contains(@class, "timeline__photo")] | '
                                                    '//div[contains(@class, "timeline")]/div[contains(@class, "timeline__smalltext")] | '
                                                    '//div[contains(@class, "timeline__group")]/div'
                                                    )
            info = self.db.get_source("Интерфакс")

            for block in news_blocks:
                try:
                    time_element = block.find_element(By.TAG_NAME, 'time')
                    time = time_element.text.strip()

                    time_str = time_element.text.strip()
                    parsed_time = dateparser.parse(
                        time_str,
                        languages=['ru'],
                        settings={'PREFER_DATES_FROM': 'current_period'}
                    )

                    # Если дата не распознана, используем текущую дату + время
                    if not parsed_time:
                        current_date = datetime.now().date()
                        time_only = datetime.strptime(time_str, "%H:%M").time()
                        parsed_time = datetime.combine(current_date, time_only)

                    if not parsed_time:
                        current_date = datetime.now().date()
                        time_only = datetime.strptime(time_str, "%H:%M").time()
                        parsed_time = datetime.combine(current_date, time_only)

                    link_element = block.find_element(By.XPATH, './/a[./h3]')
                    title = link_element.get_attribute('title') or link_element.find_element(By.TAG_NAME, 'h3').text
                    url = link_element.get_attribute('href')

                    self.db.set_news(title=title, datetime=parsed_time, url=url, source_id=info.id)

                except Exception as e:
                    continue
            print(f"Просмотренные новости: {len(news_blocks)}. Интерфакс.")

        finally:
            driver.quit()