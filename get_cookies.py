import pickle
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

options = Options()
# options.add_argument("--start-maximized")  # Обычный режим (не headless)
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument( # тут настройки для chrome для mac
    "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

driver.get("https://www.ozon.ru/") # тут нужно через точку остановы зайти на сайт и залогиниться. потом продолжить скрипт

pickle.dump(driver.get_cookies(), open("cookies.pkl", "wb"))

driver.quit()
