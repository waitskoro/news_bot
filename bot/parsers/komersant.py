from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class Kommersant:
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
                (By.XPATH, '//article[@data-article-publishing-id]')
            ))

            news_items = driver.find_elements(By.XPATH, '//article[contains(@class, "rubric_lenta__item")]')

            for item in news_items:

                ime_elements = item.find_elements(By.XPATH, './/p[contains(@class, "rubric_lenta__item_tag")]')
                datetime = ime_elements[0].text.strip()

                title = item.get_attribute('data-article-title')
                url = item.get_attribute('data-article-url')

                info = self.db.get_source("Коммерсантъ")
                self.db.set_news(title=title, datetime=datetime, url=url, magazine_id=info.id)

            print(f"Просмотренные новости: {len(news_items)}. Коммерсантъ.")

        finally:
            driver.quit()