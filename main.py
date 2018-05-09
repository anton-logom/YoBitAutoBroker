from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
import os, time, json, requests
from py_linq import Enumerable

options = webdriver.ChromeOptions()

# НАСТРОЙКИ
currency1 = 'liza'
currency2 = 'usd'

# Windows
# chrome_driver_path = ".\chromedriver.exe"  # путь до драйвера Chrome
# profile_dir = r"C:\Users\Antoshka\AppData\Local\Google\Chrome\User Data"  # Директория кэша Chrome
# options.add_argument("--user-data-dir=" + os.path.abspath(profile_dir))

# MacOS
chrome_driver_path = "/Users/r3m1x/ChromeDriver/chromedriver"
chrome_cache_path = "--user-data-dir=/Users/r3m1x/ChromeDriver/caсhe/"
options.add_argument(chrome_cache_path)


def get_price():
    result = requests.get("https://yobit.net/api/3/ticker/" + currency1 + "_" + currency2)
    temp_data = json.loads(result.text)
    data = dict()
    data['time'] = time.ctime()
    data['buy'] = temp_data['liza_usd']['sell']
    data['sell'] = temp_data['liza_usd']['buy']
    save_price(data)
    return data


def buy_click(total_price=0.10000001, price=0, quantity=0.0001):
    driver.get("https://www.yobit.net/ru/trade/" + currency1.upper() + "/" + currency2.upper())
    time.sleep(1)
    # quantity_input = driver.find_element_by_xpath('//*[@id="data-pjax-container"]/div[2]/div[1]/div/div[3]/div/input')
    # quantity_input.send_keys(Keys.BACKSPACE*10, quantity)
    # price_input = driver.find_element_by_xpath('//*[@id="data-pjax-container"]/div[2]/div[1]/div/div[4]/div/input')
    # price_input.send_keys(Keys.BACKSPACE*10, str(price))
    total_price_input = driver.find_element_by_xpath('//*[@id="data-pjax-container"]/div[2]/div[1]/div/div[5]/div/input')
    total_price_input.send_keys(Keys.BACKSPACE * 10, str(total_price))

    time.sleep(1)
    quantity = driver.find_element_by_xpath('//*[@id="data-pjax-container"]/div[2]/div[1]/div/div[3]/div/input')
    price = driver.find_element_by_xpath('//*[@id="data-pjax-container"]/div[2]/div[1]/div/div[4]/div/input')
    save_json('buy', currency1, quantity.get_attribute('value'), price.get_attribute('value'))

    # button = driver.find_element_by_xpath('//*[@id="data-pjax-container"]/div[2]/div[1]/div/input[3]')
    # button.click()
    print("Куплено!")

def sell_click(quantity=0, price=0):
    driver.get("https://www.yobit.net/ru/trade/" + currency1.upper() + "/" + currency2.upper())
    time.sleep(1)
    quantity = get_current_balance(currency1) - 1
    quantity_input = driver.find_element_by_xpath('//*[@id="data-pjax-container"]/div[3]/div[1]/div/div[3]/div/input')
    quantity_input.send_keys(Keys.BACKSPACE*10, str(quantity))
    # price_input = driver.find_element_by_xpath('//*[@id="data-pjax-container"]/div[3]/div[1]/div/div[4]/div/input')
    # price_input.send_keys(Keys.BACKSPACE*10, str(price))

    time.sleep(1)
    quantity = driver.find_element_by_xpath('//*[@id="data-pjax-container"]/div[3]/div[1]/div/div[3]/div/input')
    price = driver.find_element_by_xpath('//*[@id="data-pjax-container"]/div[3]/div[1]/div/div[4]/div/input')
    save_json('sell', currency1, quantity.get_attribute('value'), price.get_attribute('value'))

    # button = driver.find_element_by_xpath('//*[@id="data-pjax-container"]/div[3]/div[1]/div/input[3]')
    # button.click()
    print("Продано!")

def get_current_balance(curr):
    time.sleep(0.5)
    try:
        cb = driver.find_element_by_css_selector("tr[href*='/ru/history/bids/" + curr.upper() + "/BTC']")
        cb = cb.find_element_by_xpath('td[2]')
        return float(cb.text)
    except NoSuchElementException:
        return 0


def load_json(name):
    with open(name+'.json', 'r', encoding='utf-8') as file:
        d = json.load(file)
    return d


def save_json(action, currency, quantity, price):
    obj = []
    obj.append({
        'currency': currency,
        'quantity': quantity,
        'price': price,
        'time': time.ctime()
    })
    with open(action+'.json', 'a+', encoding='utf-8') as f:
        f.seek(0, 2)
        if f.tell() == 0:
            json.dump(obj, f, indent=2, ensure_ascii=False)
        else:
            f.seek(f.tell()-1, 0)
            f.truncate()
            f.write(',')
            json.dump(obj[0], f, indent=2, ensure_ascii=False)
            f.write('\n]')


def save_price(price):
    with open('price.json', 'a+', encoding='utf-8') as f:
        f.seek(0, 2)
        if f.tell() == 0:
            temp = []
            temp.append(price)
            json.dump(temp, f, indent=2, ensure_ascii=False)
        else:
            f.seek(f.tell()-1, 0)
            f.truncate()
            f.write(' ,\n')
            json.dump(price, f, indent=2, ensure_ascii=False)
            f.write('\n]')


def start_broker():
    print("Старт брокера...")
    if get_current_balance(currency1) == 1:
        buy_click()
    buy_list = load_json('buy')
    current_balance = get_current_balance(currency1) - 1
    num_of_deal = 1
    buy_history = float(buy_list[len(buy_list) - num_of_deal]['quantity'])
    average_price = float(buy_list[len(buy_list) - num_of_deal]['price'])
    while current_balance != buy_history:
        num_of_deal += 1
        buy_history += float(buy_list[len(buy_list) - num_of_deal]['quantity'])
        average_price = (average_price + float(buy_list[len(buy_list) - num_of_deal]['price']))/2
    sell_price = get_price()['sell']
    while num_of_deal < 5:
        start_check_price_time = time.time()
        while sell_price < average_price:
            sell_price = get_price()['sell']
            time.sleep(6)
            if (time.time() - start_check_price_time) > 59:
                break
        if sell_price > average_price:
            sell_click()
            break
        else:
            buy_click()
            buy_list = load_json('buy')
            num_of_deal += 1
            average_price = (average_price + float(buy_list[len(buy_list) - 1]['price']))/2
            print(average_price)
    if get_current_balance(currency1) != 209.24881774: # Изменить потом на 1
        while sell_price < average_price:
            sell_price = get_price()['sell']
            time.sleep(6)
        sell_click()
    action = int(input("Итерация брокера окончена. Начать следующую? \n0 - нет\nдругое число - да\n"))
    # action = 1 # Включение постоянной работы
    if action:
        start_broker()


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
        start_broker()
    driver.close()
    print("Работа окончена.")

