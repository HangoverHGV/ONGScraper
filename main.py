from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException
import time

from sqlalchemy import create_engine, MetaData, Column, Integer, String, Table, inspect

host = 'localhost'
user = 'nonprofit'
password = '123nonprofit123'
db = 'ongdb'

uri = 'mysql+pymysql://' + user + ':' + password + '@' + host + '/' + db

engine = create_engine(uri, echo=False)

meta = MetaData()

nonprofittbl = Table('ongtbl', meta,
                     Column('id', Integer, primary_key=True),
                     Column('name', String(500)),
                     Column('description', String(5000)),
                     Column('address', String(500)),
                     Column('countries', String(500)),
                     Column('causes', String(500)),
                     Column('websites', String(500)),
                     )

table_name = 'ongtbl'


def GetTableName(name):
    Exists = False
    tables = inspect(engine)
    for t_name in tables.get_table_names():
        if t_name == name:
            Exists = True
            break
        else:
            Exists = False

    return Exists


if GetTableName(table_name) == False:
    meta.create_all(engine)

conn = engine.connect()


def ElementExists(xpath):
    try:
        driver.find_element(By.XPATH, xpath)
        return True
    except NoSuchElementException:
        return False


def CheckSQL(x, rows):
    for row in rows:
        rez = row[0]
        if x == rez:
            return True
    return False


main_url = 'https://www.pledge.to/organizations?cause=animals'

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.get(main_url)
driver.maximize_window()
time.sleep(0.5)

nav = driver.find_elements(By.XPATH, '//div[@class="d-flex"]/a')

next = False
for i in range(0, 9):
    nav = driver.find_elements(By.XPATH, '//div[@class="d-flex"]/a')
    print(f'CATEGORY: {nav[i].text}')
    if i > 0:
        nav[i].click()
    while True:
        if next:
            nxt = driver.find_element(By.XPATH, '//a[@aria-label="Next ›"]')
            nxt.click()
        for j in range(0, 11):
            time.sleep(1)
            if not ElementExists('//div[@class="h-100 d-flex flex-column"]/a'):
                Exit = True
                break
            org = driver.find_elements(By.XPATH, '//div[@class="h-100 d-flex flex-column"]/a')
            print(f'Organization: {org[j].text}')
            org[j].click()
            time.sleep(1)
            name = driver.find_element(By.XPATH, '/html/body/header/div/div/div[2]/h1').text

            try:
                description = driver.find_element(By.XPATH, '/html/body/div[4]/section[1]/p').text
            except:
                print('no description found')
                pass

            try:
                website = driver.find_element(By.XPATH, '/html/body/header/div/div/div[2]/ul/li/a')
                website_name = website.get_attribute('href')
            except:
                website_name = 'Not Found'
                print('no website found')
                pass

            try:
                address = driver.find_element(By.XPATH, '/html/body/header/div/div/div[2]/div/span/span').text
                rez = []
                for c in address:
                    rez.append(c.replace('\n', ''))
                address = ''
                for c in rez:
                    address += c
            except:
                address = 'Not Found'
                print('no address found')
                pass

            causes = ''
            cnt = 2
            a = True
            while (a):
                try:
                    cause = driver.find_element(By.XPATH, f'/html/body/div[4]/section[2]/ul[1]/li[{str(cnt)}]').text
                    causes += cause + ' '
                    cnt += 1
                except:
                    a = False

            countries = ''
            cnt = 2
            a = True
            while (a):
                try:
                    country = driver.find_element(By.XPATH, f'/html/body/div[4]/section[2]/ul[2]/li[{str(cnt)}]').text
                    countries = country + ' '
                    cnt += 1
                except:
                    a = False

            query = 'SELECT name from ongtbl'
            rows = conn.execute(query).fetchall()
            if CheckSQL(name, rows) == False:

                stmt = (
                    nonprofittbl.insert().values(name=name, address=address, countries=countries, causes=causes,
                                                 websites=website_name)
                )

                conn.execute(stmt)
                s = nonprofittbl.select()
                conn.execute(s).fetchall()
            else:
                print('------->Allready in DB<---------')

            driver.execute_script("window.history.go(-1)")
        next = True

        if Exit:
            break
