from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
import os, time, json, requests
from py_linq import Enumerable

options = webdriver.ChromeOptions()

# НАСТРОЙКИ
currency1 = 'liza'  # валюта, которую будем покупать и продавать
currency2 = 'usd'   # исходная валюта для вложений в первую валюту (обычно usd)
action = 1          # Режим работы: 1 = постоянная автоматическая, 0 = ручное включение каждой итерации


# для работы под Windows
chrome_driver_path = ".\chromedriver.exe"  # путь до драйвера Chrome
profile_dir = r"C:\Users\Antoshka\AppData\Local\Google\Chrome\User Data"  # Директория кэша Chrome
options.add_argument("--user-data-dir=" + os.path.abspath(profile_dir))

# для работы под MacOS
# chrome_driver_path = "chromedriver"  # путь до драйвера Chrome
# chrome_cache_path = "--user-data-dir=/Users/r3m1x/ChromeDriver/caсhe/"  # Директория кэша Chrome
# options.add_argument(chrome_cache_path)


def get_price():
    data = dict()
    data['time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
    data['currency'] = currency1
    try:
        result = requests.get("https://yobit.net/api/3/ticker/" + currency1 + "_" + currency2)
        temp_data = json.loads(result.text)
        data['buy'] = temp_data[currency1 + "_" + currency2]['sell']
        data['sell'] = temp_data[currency1 + "_" + currency2]['buy']
    except Exception:
        temp_data = load_json('price')
        if len(temp_data) != 0:
            data = temp_data[len(temp_data)-1]
        else:
            data['buy'] = '0'
            data['sell'] = '0'
    print('Текущие курсы валюты ' + currency1 + ' - покупка: ' + str(data['buy']) + ' продажа:' + str(data['sell']))
    save_price(data)
    return data


def buy_click(total_price=0.10000100, price=0, quantity=0.0001):
    driver.get("https://www.yobit.net/ru/trade/" + currency1.upper() + "/" + currency2.upper())
    time.sleep(1)
    # quantity_input = driver.find_element_by_xpath('//*[@id="data-pjax-container"]/div[2]/div[1]/div/div[3]/div/input')
    # quantity_input.send_keys(Keys.BACKSPACE*15, quantity)
    # price_input = driver.find_element_by_xpath('//*[@id="data-pjax-container"]/div[2]/div[1]/div/div[4]/div/input')
    # price_input.send_keys(Keys.BACKSPACE*15, str(price))
    total_price_input = driver.find_element_by_xpath('//*[@id="data-pjax-container"]/div[2]/div[1]/div/div[5]/div/input')
    total_price_input.send_keys(Keys.BACKSPACE * 15, str(total_price))

    button = driver.find_element_by_xpath('//*[@id="data-pjax-container"]/div[2]/div[1]/div/input[3]')
    button.click()

    time.sleep(10)
    check = check_order()
    if check:
        time.sleep(0.5)
        quantity = driver.find_element_by_xpath('//*[@id="data-pjax-container"]/div[2]/div[1]/div/div[3]/div/input')
        price = driver.find_element_by_xpath('//*[@id="data-pjax-container"]/div[2]/div[1]/div/div[4]/div/input')
        temp_quantity = quantity.get_attribute('value')
        temp_price = price.get_attribute('value')
        save_json('buy', currency1, temp_quantity, temp_price)
        print("Куплено! \nПо цене: " + temp_price)
    else:
        print("Ордер не прошел. Повторяем...")
        start_broker()


def sell_click(quantity=0, price=0):
    driver.get("https://www.yobit.net/ru/trade/" + currency1.upper() + "/" + currency2.upper())
    time.sleep(1)
    quantity = get_current_balance(currency1)  # - 200
    quantity_input = driver.find_element_by_xpath('//*[@id="data-pjax-container"]/div[3]/div[1]/div/div[3]/div/input')
    quantity_input.send_keys(Keys.BACKSPACE*15, str(quantity))
    # price_input = driver.find_element_by_xpath('//*[@id="data-pjax-container"]/div[3]/div[1]/div/div[4]/div/input')
    # price_input.send_keys(Keys.BACKSPACE*15, str(price))

    time.sleep(0.5)
    price = driver.find_element_by_xpath('//*[@id="data-pjax-container"]/div[3]/div[1]/div/div[4]/div/input')
    temp_price = price.get_attribute('value')

    last_price = load_json('price')
    last_price = last_price[len(last_price)-3]
    last_price = last_price['sell']

    if last_price != float(temp_price):
        print('Цена успела измениться. Брокер продолжает работу...')
        start_broker()
    elif quantity < 0.1100001:
        start_broker()
    else:
        button = driver.find_element_by_xpath('//*[@id="data-pjax-container"]/div[3]/div[1]/div/input[3]')
        button.click()

        time.sleep(10)
        check = check_order()
        if check:
            time.sleep(0.5)
            quantity = driver.find_element_by_xpath('//*[@id="data-pjax-container"]/div[3]/div[1]/div/div[3]/div/input')
            temp_quantity = quantity.get_attribute('value')
            save_json('sell', currency1, temp_quantity, temp_price)
        else:
            print("Ордер не прошел. Повторяем...")
            start_broker()
        print("Продано! \nПо цене: " + temp_price)


def check_order():
    my_orders = driver.find_element_by_id('myord_table')
    my_orders = my_orders.find_elements_by_class_name('green') + my_orders.find_elements_by_class_name('red')
    if len(my_orders) == 0:
        print("Ордер прошел успешно!")
        return True
    else:
        my_orders = Enumerable(my_orders)
        my_orders = my_orders.select(lambda x: x.get_attribute('id'))
        my_orders = my_orders.to_list()
        for order in my_orders:
            driver.find_element_by_xpath('//*[@id="' + order + '"]/td[4]/table/tbody/tr/td[2]/a').click()
        print("Ордер был удален. Повтор...")
        return False


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
    obj = list()
    obj.append({
        'currency': currency,
        'quantity': quantity,
        'price': price,
        'time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
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
            temp = list()
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
    if get_current_balance(currency1) == 0:  # баланс
        buy_click()
    buy_list = load_json('buy')
    current_balance = get_current_balance(currency1)  # - 200
    num_of_deal = 1
    try:
        buy_history = float(buy_list[len(buy_list) - num_of_deal]['quantity'])
        average_price = float(buy_list[len(buy_list) - num_of_deal]['price'])
        average_price += round(average_price * 0.002, 8)  # Комиссия 0.2%
        average_price = round(average_price, 8)
        while round(current_balance, 3) != round(buy_history, 3):
            num_of_deal += 1
            if buy_list[len(buy_list) - num_of_deal]['currency'] == currency1:
                buy_history += float(buy_list[len(buy_list) - num_of_deal]['quantity'])
                average_price = (average_price + float(buy_list[len(buy_list) - num_of_deal]['price']))/2
                average_price += round(average_price * 0.002, 8)  # Комиссия 0.2%
                average_price = round(average_price, 8)
    except Exception:
        num_of_deal = 1
        average_price = 0
    sell_price = get_price()['sell']
    sell_price -= round(sell_price * 0.002, 8)  # Комиссия 0.2%
    sell_price = round(sell_price, 8)
    while num_of_deal < 5:
        start_check_price_time = time.time()
        while sell_price < average_price:
            sell_price = get_price()['sell']
            sell_price -= round(sell_price * 0.002, 8)  # Комиссия 0.2%
            sell_price = round(sell_price, 8)
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
            average_price += round(average_price * 0.002, 8)  # Комиссия 0.2%
            average_price = round(average_price, 8)
    if get_current_balance(currency1) < 0.1100001:  # - аланс
        while sell_price < average_price:
            sell_price = get_price()['sell']
            sell_price -= round(sell_price * 0.002, 8)  # Комиссия 0.2%
            sell_price = round(sell_price, 8)
            time.sleep(6)
        sell_click()

    if action:
        start_broker()
    elif int(input("Итерация брокера окончена. Начать следующую? 0 - нет, 1 - да")):
        start_broker()


if __name__ == '__main__':
    print("Стартуем...")
    driver = webdriver.Chrome(chrome_driver_path, chrome_options=options)
    print('Ждем загрузки страницы...')
    driver.get("https://www.yobit.net/ru/trade/" + currency1.upper() + "/" + currency2.upper())
    time.sleep(1)
    try:
        if driver.find_element_by_xpath('/html/body/div[1]/header/div/div[2]/ul[1]/li[2]/a').text == 'Войти':
            print('Отсутствует аутентификация на сайте! Авторизуйтесь и перезапустите программу.')
    except NoSuchElementException:
        print('Авторизация проверена')
        start_broker()
    driver.close()
    print("Работа окончена.")
    time.sleep(2)
