import json
import os
import random
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
import time
import openpyxl

# тут настройки, потому что у озона есть защита от ботов
options = Options()
# options.add_argument("--start-maximized")  # Обычный режим (не headless)
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)



time.sleep(5)


def get_id(filepath):
    wb = openpyxl.load_workbook(filepath)
    sheet = wb.worksheets[0]
    amount_of_dates = 0
    i = 2
    while True:
        val = sheet[f'B{i}'].value
        if val is None:
            break
        else:
            amount_of_dates += 1
        i += 1
    i = 2
    ids = []
    while i < amount_of_dates:
        ids.append(sheet[f'B{i}'].value)
        i += 1

    return ids


def get_prices(filepath):
    global driver
    ids = get_id(filepath)
    try:
        time.sleep(2)
        driver.find_element(By.XPATH, '//*[@id="reload-button"]').click()
    except Exception:
        pass

    prices = []
    availability = []
    available = True
    row = 1
    for item in ids:  # основной цикл поиска товаров на основе
        search = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//input[@class="ia5a_33 tsBody500Medium" and @name="text"]'))
        )
        search.clear()
        search.send_keys(item)
        search.send_keys(Keys.RETURN)
        try:  # проверяем на наличие товара
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//input[@class="mp_27"')))
            available = False
        except Exception:
            pass

        if available:
            price_web = WebDriverWait(driver, 10).until(EC.presence_of_element_located((
                By.XPATH, '*//span[@class="t3m_27 mt4_27 t7m_27"]')))
            price = price_web.text
            prices_cleaned = price.replace('\u2009', ' ')
            availability.append('В наличии')
            prices.append(prices_cleaned)
        else:
            price = ''
            prices.append(price)

        driver.back()

    return prices, availability


def save_to_ex(prices, availability, filepath):
    i = 2
    wb = openpyxl.load_workbook(filepath)
    sheet = wb.worksheets[0]
    for pr, av in zip(prices, availability):
        sheet[f'C{i}'].value = pr
        sheet[f'D{i}'].value = av
        i += 1
    wb.save(filepath)


def get_low_price():
    global driver
    try:
        time.sleep(2)
        driver.find_element(By.XPATH, '//*[@id="reload-button"]').click()
    except Exception:
        pass
    catalog = driver.find_element(By.XPATH, '//*[@id="stickyHeader"]/div/div[1]/div/button')
    driver.execute_script('arguments[0].click()', catalog)
    catalog_button = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="10500"]/span'))
    )
    ActionChains(driver).move_to_element(catalog_button).perform()
    type_of_item = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="10500"]/div[2]/div[1]/div[1]/div[1]/a[2]')))
    type_of_item.click()
    print('нажал кнопку')
    time.sleep(10)
    window_handles = driver.window_handles
    driver.switch_to.window(window_handles[-1])
    all_items = driver.find_elements(
        By.XPATH, "//span[contains(@class, 'tsBody500Medium') and contains(text(), 'Холодильник')]")
    three_items = random.sample(all_items, 3)

    for item in three_items:
        time.sleep(5)
        driver.execute_script("arguments[0].click();", item)
        time.sleep(5)
        window_handles = driver.window_handles
        driver.switch_to.window(window_handles[-1])
        comparison = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((
                By.XPATH, '//*[@id="layoutPage"]/div[1]/div[4]/div[2]/div/div/div/div[2]/button[2]/div')))
        try:
            # driver.execute_script("arguments[0].click();", comparison)
            comparison.click()
            print('нажал кнопку')
        except Exception:
            print('Не удалось нажать кнопку')
        time.sleep(5)
        driver.close()
        time.sleep(5)
        window_handles = driver.window_handles
        driver.switch_to.window(window_handles[1])

    driver.get('https://www.ozon.ru/product/compare/')

    res = []
    for i in range(1, 4):
        price = driver.find_element(
            By.XPATH, f'//*[@id="layoutPage"]/div[1]/div[2]/div/div/div/div[4]/div[2]/div[1]/div/div[{i}]'
                      f'/div/div[2]/div[1]/div[2]/span[1]/span').text
        clear_price = price.replace(' ', '')
        clear_price = clear_price.replace('₽', '')
        res.append(int(clear_price))
        i += 1

    min_price = min(res)
    min_price_index = res.index(min_price)

    driver.find_element(By.XPATH, f'//*[@id="layoutPage"]/div[1]/div[2]/div/div/div/div[4]/div[2]/div[1]/div/'
                                  f'div[{min_price_index + 1}]/div/div[2]/div[3]/button').click()
    driver.get('https://www.ozon.ru/cart')
    buy_button = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.XPATH, '//*[@id="layoutPage"]/div[1]/div/div/div[2]/div[4]/div[2]/div/section/div[1]/div[1]/button')))
    buy_button.click()

if __name__ == '__main__':
    # filename = 'товары.xlsx'
    # filepath = os.path.join(os.getcwd(), filename)
    # prices, availability = get_prices(filepath)
    # save_to_ex(prices, availability, filepath)
    # print(prices)
    # print(availability)
    get_low_price()
    driver.quit()
