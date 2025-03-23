import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class Bloomberg:
    def __init__(self):
        self.user_agent = 'Mozilla/80.0'

        options = webdriver.ChromeOptions()
        options.add_argument(f"user-agent={self.user_agent}")
        options.add_argument("--disable-blink-features=AutomationControlled")

        self.driver = webdriver.Chrome(options=options)
        self.driver.get("https://www.bloomberg.com/latest?utm_campaign=latest")

        self.__scraping()

    def translate(self, word):
        headers = {'User-Agent': self.user_agent}
        url = "https://clients5.google.com/translate_a/t?client=dict-chrome-ex&sl=auto&tl=ru&q=" + word

        request_result = requests.get(url, headers=headers).json()
        return request_result[0][0]

    def __scraping(self):
        try:
            wait = WebDriverWait(self.driver, 5)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.LineupContentArchiveFiltered_itemContainer__xMp27")))

            news_items = self.driver.find_elements(By.CSS_SELECTOR, "div.LineupContentArchiveFiltered_itemContainer__xMp27")

            for item in news_items:
                try:
                    time_element = item.find_element(By.CSS_SELECTOR, "div.LineupContentArchiveFiltered_itemTimestamp__lehuG time")
                    time = time_element.text.strip()

                    link_element = item.find_element(By.CSS_SELECTOR, "a.LineupContentArchiveFiltered_storyLink__cz5Qc")
                    title = link_element.find_element(By.CSS_SELECTOR, "[data-testid='headline'] span").text.strip()
                    url = link_element.get_attribute('href')

                    print(f"Заголовок: {self.translate(title)}")
                    print(f"Время: {time}")
                    print(f"Ссылка: {url}")
                    print("-" * 80)

                except Exception as e:
                    print(f"Ошибка при парсинге элемента: {str(e)}")
                    continue

        except Exception as e:
            print(f"Произошла ошибка: {str(e)}")
        finally:
            self.driver.quit()