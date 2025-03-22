import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# User-Agent для requests и selenium
user_agent = 'Mozilla/80.0'

options = webdriver.ChromeOptions()
# Правильная передача User-Agent и других параметров
options.add_argument(f"user-agent={user_agent}")
options.add_argument("--disable-blink-features=AutomationControlled")

driver = webdriver.Chrome(options=options)
driver.get("https://www.bloomberg.com/latest?utm_campaign=latest")

def translate(word):
    headers = {'User-Agent': user_agent}  # Используем тот же User-Agent
    url_tr = "https://clients5.google.com/translate_a/t?client=dict-chrome-ex&sl=auto&tl=ru&q=" + word

    request_result = requests.get(url_tr, headers=headers).json()
    return request_result[0][0]

try:
    wait = WebDriverWait(driver, 5)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.LineupContentArchiveFiltered_itemContainer__xMp27")))

    news_items = driver.find_elements(By.CSS_SELECTOR, "div.LineupContentArchiveFiltered_itemContainer__xMp27")

    for item in news_items:
        try:
            time_element = item.find_element(By.CSS_SELECTOR, "div.LineupContentArchiveFiltered_itemTimestamp__lehuG time")
            time = time_element.text.strip()

            link_element = item.find_element(By.CSS_SELECTOR, "a.LineupContentArchiveFiltered_storyLink__cz5Qc")
            title = link_element.find_element(By.CSS_SELECTOR, "[data-testid='headline'] span").text.strip()
            url = link_element.get_attribute('href')

            print(f"Заголовок: {translate(title)}")
            print(f"Время: {time}")
            print(f"Ссылка: {url}")
            print("-" * 80)

        except Exception as e:
            print(f"Ошибка при парсинге элемента: {str(e)}")
            continue

except Exception as e:
    print(f"Произошла ошибка: {str(e)}")
finally:
    driver.quit()