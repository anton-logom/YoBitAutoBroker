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

    c.execute('TRUNCATE `price`')
    c.execute('TRUNCATE `operations`')

    conn.commit()
    c.close()
    conn.close()
    print('БД очищена.')


def insert_into_buy(lst_put, conn):
    c = conn.cursor()
    c.execute("SELECT `id` FROM `operations` WHERE `action` = 'buy'")
    lastdb = c.rowcount
    if lastdb:
        lst_put = lst_put[lastdb + 1:]
    print('ластдб' + str(lastdb))
    print(lst_put)
    c.close()
    c = conn.cursor()
    try:
        c.executemany("""
                INSERT INTO operations (`currency`, `action`, `time`, `price`, `quantity`) VALUES (%(currency)s, 'buy', %(time)s, %(price)s, %(quantity)s)
                """, lst_put)
        print("Информация о покупке добавлена в БД")

    except MySQLdb.DatabaseError:
        print('Проблема при записи в БД: покупки не записаны')
    c.close()


def insert_into_prices(lst_put, conn):
    c = conn.cursor()
    c.execute('SELECT max(`id`) FROM price')
    lastdb = c.fetchone()[0]
    if lastdb:
        lst_put = lst_put[lastdb + 1:]
    c.close()
    c = conn.cursor()
    try:
        c.executemany("""
        INSERT INTO price (`time`, `currency`, `buy`, `sell`) VALUES (%(time)s, %(currency)s, %(buy)s, %(sell)s)
        """, lst_put)
        print("Информация о курсе добавлена в БД")
    except MySQLdb.DatabaseError:
        print('Проблема при записи в БД: курсы валют не записаны')
    c.close()


def insert_into_sell(lst_put, conn):
    c = conn.cursor()

    c.execute("SELECT `id` FROM `operations` WHERE `action` = 'sell'")
    lastdb = c.rowcount
    if lastdb:
        lst_put = lst_put[lastdb + 1:]
    c.close()
    c = conn.cursor()
    try:
        c.executemany("""
            INSERT INTO operations (`currency`, `action`, `time`, `price`, `quantity`) VALUES (%(currency)s, 'sell', %(time)s, %(price)s, %(quantity)s)
            """, lst_put)
        print("Информация о продаже добавлена в БД")

    except MySQLdb.DatabaseError:
        print('Проблема при записи в БД: продажи не записаны')
    c.close()

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
    start_time = time.time()
    conn = MySQLdb.connect(host=mysql_config.Host,
                           port=mysql_config.Port,
                           user=mysql_config.username,
                           passwd=mysql_config.password,
                           charset="utf8",
                           db=mysql_config.db)
    conn.autocommit(True)
    if old_sha1_price != new_sha1_price:
        list_put = load_from_json(price_file)
        insert_into_prices(list_put, conn)
    if old_sha1_buy != new_sha1_buy:
        list_put = load_from_json(buy_file)
        insert_into_buy(list_put, conn)
    if old_sha1_sell != new_sha1_sell:
        list_put = load_from_json(sell_file)
        insert_into_sell(list_put, conn)
    print("Этап записи завершен, время записи составило: %s сек" % (time.time() - start_time))
    conn.close()





