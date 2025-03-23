from datetime import datetime, timedelta
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class Bloomberg:
    def __init__(self, url, db):
        self.url = url
        self.db = db
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'

    def parse_relative_time(self, time_str):
        try:
            # Парсим относительное время
            numbers = re.findall(r'\d+', time_str)
            if not numbers:
                return datetime.now()

            value = int(numbers[0])

            if 'min' in time_str:
                return datetime.now() - timedelta(minutes=value)
            elif 'hour' in time_str:
                return datetime.now() - timedelta(hours=value)
            elif 'day' in time_str:
                return datetime.now() - timedelta(days=value)

            return datetime.now()
        except Exception as e:
            print(f"Ошибка парсинга времени '{time_str}': {str(e)}")
            return datetime.now()

    def scraping(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument(f"user-agent={self.user_agent}")
        options.add_argument("--disable-blink-features=AutomationControlled")

        driver = webdriver.Chrome(options=options)
        driver.get(self.url)

        try:
            wait = WebDriverWait(driver, 10)
            wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "div.LineupContentArchiveFiltered_itemContainer__xMp27")))

            news_items = driver.find_elements(By.CSS_SELECTOR, "div.LineupContentArchiveFiltered_itemContainer__xMp27")
            info = self.db.get_source("Bloomberg")

            for item in news_items:
                try:
                    # Парсим время
                    time_element = item.find_element(By.CSS_SELECTOR,
                                                     "div.LineupContentArchiveFiltered_itemTimestamp__lehuG time")
                    time_str = time_element.text.strip()
                    parsed_time = self.parse_relative_time(time_str)

                    # Парсим заголовок и ссылку
                    link_element = item.find_element(By.CSS_SELECTOR, "a.LineupContentArchiveFiltered_storyLink__cz5Qc")
                    title = link_element.find_element(By.CSS_SELECTOR, "[data-testid='headline'] span").text.strip()
                    url = link_element.get_attribute('href')

                    # Сохраняем в БД
                    self.db.set_news(
                        title=title,
                        datetime=parsed_time,
                        url=url,
                        magazine_id=info.id
                    )

                except Exception as e:
                    print(f"Ошибка при парсинге элемента: {str(e)}")
                    continue

            print(f"Обработано новостей: {len(news_items)}. Bloomberg")

        except Exception as e:
            print(f"Критическая ошибка: {str(e)}")
        finally:
            driver.quit()