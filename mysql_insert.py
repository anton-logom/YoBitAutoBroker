# coding: utf8
import MySQLdb
import json
import checksum
import time

# НАСТРОЙКИ
import mysql_config
buy_file = 'buy.json'
sell_file = 'sell.json'
price_file = 'price.json'
clear = 0               # очистка БД при запуске программы 0 = не очищать, 1 = очищать


def load_from_json(Fname):
    with open(Fname, 'r', encoding='utf-8') as file:
        d = json.load(file)
    return d


def db_clear():
    conn = MySQLdb.connect(host=mysql_config.Host,
                           port=mysql_config.Port,
                           user=mysql_config.username,
                           passwd=mysql_config.password,
                           charset="utf8",
                           db=mysql_config.db)
    c = conn.cursor()

    # PUT YOUR CODE HERE

    conn.commit()
    c.close()
    conn.close()
    print('БД очищена.')


def insert_into_buy(lst_put):
    start_time = time.time()
    conn = MySQLdb.connect(host=mysql_config.Host,
                           port=mysql_config.Port,
                           user=mysql_config.username,
                           passwd=mysql_config.password,
                           charset="utf8",
                           db=mysql_config.db)
    conn.autocommit(True)
    c = conn.cursor()

    # PUT YOU CODE HERE FOR INSERT INTO TABLE BUY

    c.close()
    conn.close()
    print("Время записи составило: %s сек" % (time.time() - start_time))


def insert_into_prices(lst_put):
    start_time = time.time()
    conn = MySQLdb.connect(host=mysql_config.Host,
                           port=mysql_config.Port,
                           user=mysql_config.username,
                           passwd=mysql_config.password,
                           charset="utf8",
                           db=mysql_config.db)
    conn.autocommit(True)
    c = conn.cursor()

    # PUT YOU CODE HERE FOR INSERT INTO TABLE PRICES

    c.close()
    conn.close()
    print("Время записи составило: %s сек" % (time.time() - start_time))


def insert_into_sell(lst_put):
    start_time = time.time()
    conn = MySQLdb.connect(host=mysql_config.Host,
                           port=mysql_config.Port,
                           user=mysql_config.username,
                           passwd=mysql_config.password,
                           charset="utf8",
                           db=mysql_config.db)
    conn.autocommit(True)
    c = conn.cursor()

    # PUT YOU CODE HERE FOR INSERT INTO TABLE SELL

    c.close()
    conn.close()
    print("Время записи составило: %s сек" % (time.time() - start_time))


while __name__ == '__main__':
    if clear:
        db_clear()
    print('Ждем обновления json файла...')
    old_sha1_buy = checksum.get_sha1(buy_file)
    new_sha1_buy = checksum.get_sha1(buy_file)
    old_sha1_sell = checksum.get_sha1(sell_file)
    new_sha1_sell = checksum.get_sha1(sell_file)
    old_sha1_price = checksum.get_sha1(price_file)
    new_sha1_price = checksum.get_sha1(price_file)
    while old_sha1_buy == new_sha1_buy and old_sha1_sell == new_sha1_sell and old_sha1_price == new_sha1_price:
        new_sha1_buy = checksum.get_sha1(buy_file)
        new_sha1_sell = checksum.get_sha1(sell_file)
        new_sha1_price = checksum.get_sha1(price_file)
        time.sleep(1)

    print('json-файл обновлён, начинаем запись в БД...')
    if old_sha1_price == new_sha1_price:
        list_put = load_from_json(buy_file)
        insert_into_prices(list_put)
    elif old_sha1_buy != new_sha1_buy:
        list_put = load_from_json(sell_file)
        insert_into_buy(list_put)
    elif old_sha1_sell != new_sha1_sell:
        list_put = load_from_json(price_file)
        insert_into_sell(list_put)




