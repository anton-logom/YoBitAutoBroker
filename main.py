from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
import os, time, json

options = webdriver.ChromeOptions()

# НАСТРОЙКИ
currency1 = 'liza'
currency2 = 'usd'

# Windows
chrome_driver_path = ".\chromedriver.exe"  # путь до драйвера Chrome
profile_dir = r"C:\Users\Antoshka\AppData\Local\Google\Chrome\User Data"  # Директория кэша Chrome
options.add_argument("--user-data-dir=" + os.path.abspath(profile_dir))

# # MacOS
# chrome_driver_path = "/Users/r3m1x/ChromeDriver/chromedriver"
# chrome_cache_path = "--user-data-dir=/Users/r3m1x/ChromeDriver/caсhe/"
# options.add_argument(chrome_cache_path)


def get_ticker():
    driver.get("https://yobit.net/api/3/ticker/" + currency1 + "_" + currency2)
    time.sleep(0.2)
    html_source = driver.find_element_by_tag_name('body')
    data = json.loads(html_source.text)
    return data


def buy_kripto(kolvo, price):
    driver.get("https://www.yobit.net/ru/trade/" + currency1.upper() + "/" + currency2.upper())
    time.sleep(1)
    kvp = driver.find_element_by_xpath('//*[@id="data-pjax-container"]/div[2]/div[1]/div/div[3]/div/input')
    kvp.send_keys(Keys.BACKSPACE*10, kolvo)
    pricep = driver.find_element_by_xpath('//*[@id="data-pjax-container"]/div[2]/div[1]/div/div[4]/div/input')
    pricep.send_keys(Keys.BACKSPACE*13, price)
    # btn = driver.find_element_by_xpath('//*[@id="data-pjax-container"]/div[2]/div[1]/div/input[3]')
    # btn.click()


def sell_kripto(kolvo, price):
    driver.get("https://www.yobit.net/ru/trade/" + currency1.upper() + "/" + currency2.upper())
    time.sleep(1)
    kvp = driver.find_element_by_xpath('//*[@id="data-pjax-container"]/div[3]/div[1]/div/div[3]/div/input')
    kvp.send_keys(Keys.BACKSPACE*10, kolvo)
    pricep = driver.find_element_by_xpath('//*[@id="data-pjax-container"]/div[3]/div[1]/div/div[4]/div/input')
    pricep.send_keys(Keys.BACKSPACE*13, price)
    # btn = driver.find_element_by_xpath('//*[@id="data-pjax-container"]/div[3]/div[1]/div/input[3]')
    # btn.click()


def get_current_balance(curr):
    driver.get("https://www.yobit.net/ru/wallets")
    time.sleep(0.5)
    try:
        cb = driver.find_element_by_css_selector("tr[href*='/ru/history/bids/" + curr.upper() + "/BTC']")
        cb = cb.find_element_by_xpath('td[2]')
        return cb.text
    except NoSuchElementException:
        return '0.0'


if __name__ == '__main__':
    print("Стартуем...")
    driver = webdriver.Chrome(chrome_driver_path, chrome_options=options)
    print('Ждем загрузки страницы...')
    driver.get("https://www.yobit.net/ru/trade/" + currency1.upper() + "/" + currency2.upper())
    time.sleep(1)
    try:
        if driver.find_element_by_xpath('/html/body/div[1]/header/div/div[2]/ul[1]/li[2]/a').text == 'Войти':
            print('Отсутствует аутентификация на сайте!')

    except NoSuchElementException:
        print(get_current_balance(currency1))
        data = get_ticker()
        print("SELL: %0.8f" % data[currency1 + "_" + currency2]['sell'])
        print("BUY: %0.8f" % data[currency1 + "_" + currency2]['buy'])
        buy_kripto("0.0001", str(data[currency1 + "_" + currency2]['sell']))
        #sell_kripto("0.0001", str(data[currency1 + "_" + currency2]['buy']))
        print('Готово')

    driver.close()
    #input()

