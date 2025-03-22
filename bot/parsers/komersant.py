from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Настройка драйвера с ожиданием
options = webdriver.ChromeOptions()
options.add_argument("--headless=new")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

driver = webdriver.Chrome(options=options)
driver.get("https://www.kommersant.ru/lenta/news?from=lenta_news")

try:
    wait = WebDriverWait(driver, 15)

    wait.until(EC.presence_of_element_located(
        (By.XPATH, '//article[@data-article-publishing-id]')
    ))

    news_items = driver.find_elements(By.XPATH, '//article[contains(@class, "rubric_lenta__item")]')

    for item in news_items:

        ime_elements = item.find_elements(By.XPATH, './/p[contains(@class, "rubric_lenta__item_tag")]')
        time = ime_elements[0].text.strip()

        title = item.get_attribute('data-article-title')
        url = item.get_attribute('data-article-url')

        print(f"Заголовок: {title}")
        print(f"Время: {time}")
        print(f"Ссылка: {url}")
        print("-" * 80)

finally:
    driver.quit()