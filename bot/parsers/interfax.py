from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class Interfax:
    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--headless=new")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

        self.driver = webdriver.Chrome(options=options)
        self.driver.get("https://www.interfax.ru/")

    def scraping(self):
        try:
            wait = WebDriverWait(self.driver, 15)

            wait.until(EC.presence_of_element_located(
                (By.XPATH, '//div[contains(@class, "timeline")]')
            ))

            news_blocks = self.driver.find_elements(By.XPATH,
                                               '//div[contains(@class, "timeline")]/div[contains(@class, "timeline__text")] | '
                                               '//div[contains(@class, "timeline")]/div[contains(@class, "timeline__photo")] | '
                                               '//div[contains(@class, "timeline")]/div[contains(@class, "timeline__smalltext")] | '
                                               '//div[contains(@class, "timeline__group")]/div'
                                               )
            for block in news_blocks:
                try:
                    time_element = block.find_element(By.TAG_NAME, 'time')
                    time = time_element.text.strip()

                    link_element = block.find_element(By.XPATH, './/a[./h3]')
                    title = link_element.get_attribute('title') or link_element.find_element(By.TAG_NAME, 'h3').text
                    url = link_element.get_attribute('href')

                    print(f"Заголовок: {title}")
                    print(f"Время: {time}")
                    print(f"Ссылка: {url}")
                    print("-" * 80)

                except Exception as e:
                    continue

        finally:
            self.driver.quit()