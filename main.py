from selenium import webdriver
import os, time, json

options = webdriver.ChromeOptions()

# НАСТРОЙКИ
API_KEY = 'A2168C449D4A05EE70B8C9BFE27A7A8C'
API_SECRET = b'1ed5e2f37ba0608521b240bd984ffec7'

# Windows
chrome_driver_path = ".\chromedriver.exe"  # путь до драйвера Chrome
profile_dir = r"C:\Users\Antoshka\AppData\Local\Google\Chrome\User Data"  # Директория кэша Chrome
options.add_argument("--user-data-dir=" + os.path.abspath(profile_dir))

# # MacOS
# chrome_driver_path = "/Users/r3m1x/ChromeDriver/chromedriver"
# chrome_cache_path = "--user-data-dir=/Users/r3m1x/ChromeDriver/caсhe/"
# options.add_argument(chrome_cache_path)


if __name__ == '__main__':
    print("Стартуем...")
    driver = webdriver.Chrome(chrome_driver_path, chrome_options=options)
    print('Ждем загрузки страницы...')
    driver.get("https://yobit.net/api/3/ticker/ltc_btc")
    time.sleep(0.2)
    html_source = driver.find_element_by_tag_name('body')
    data = json.loads(html_source.text)
    print(data)
    print("SELL: %0.8f" % data['ltc_btc']['sell'])
    print("BUY: %0.8f" % data['ltc_btc']['buy'])
    print('Готово')
    driver.close()

