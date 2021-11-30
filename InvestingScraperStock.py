import selenium.common.exceptions
from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
import sqlite3 as lite
import threading
import pickle
import logging
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options

import config


def init_db():
    # DEPRECATED
    try:
        con = lite.connect('identifier.sqlite')
        cur = con.cursor()
        cur.execute(config.create_company_table)
        cur.execute(config.create_employee_table)
        con.commit()
    except lite.Error:
        if con:
            con.rollback()
    finally:
        if con:
            con.close()


def getAllCompanies():
    con = lite.connect('identifier.sqlite')

    with con:
        cur = con.cursor()
        cur.execute("SELECT * FROM company")

        rows = cur.fetchall()

        return [row for row in rows]


def insertCompany(companyMetaData):
    try:
        sqliteConnection = lite.connect('identifier.sqlite')
        cursor = sqliteConnection.cursor()

        sqlite_insert_with_param = """INSERT INTO stock_company
                             (ticker, name, website, headquarter, employees, industry, type, source) 
                             VALUES (?, ?, ?, ?, ?, ?, ?, "investing");"""

        cursor.execute(sqlite_insert_with_param, companyMetaData)
        sqliteConnection.commit()

        cursor.close()

    except lite.Error as error:
        print("Failed to insert Python variable into sqlite table", error)
    finally:
        if sqliteConnection:
            sqliteConnection.close()


def insertEmployee(employeeMetaData):
    try:
        sqliteConnection = lite.connect('identifier.sqlite')
        cursor = sqliteConnection.cursor()

        sqlite_insert_with_param = """INSERT INTO stock_employee
                                ( name, title, company_ticker, source ) 
                                VALUES (?, ?, ?, "investing");"""

        cursor.execute(sqlite_insert_with_param, employeeMetaData)
        sqliteConnection.commit()

        cursor.close()

    except lite.Error as error:
        print("Failed to insert Python variable into sqlite table", error)
    finally:
        if sqliteConnection:
            sqliteConnection.close()


def scrapeEmployees(table, currentCompany):
    trs = table.find_elements(By.TAG_NAME, "tr")

    for tr in trs:
        tds = tr.find_elements(By.TAG_NAME, "td")
        rawData = (
             tds[0].text,
             tds[3].text,
             currentCompany
        )
        insertEmployee(rawData)


def handle_cookies_popup(driver):
    sleep(1)
    driver.find_element_by_id("onetrust-pc-btn-handler").click()
    sleep(1)
    driver.find_element_by_xpath('//*[@id="accept-recommended-btn-handler"]').click()
    sleep(1)


def get_all_links(path):
    driver = webdriver.Chrome(
        executable_path=r'C:\Users\RaffaeleScarano\Università\Ing Dati\AssignmentTwo\chromedriver.exe')
    sleep(3)
    driver.get(path)
    handle_cookies_popup(driver)

    links = []
    end = 25
    for i in range(0, end):
        companies = WebDriverWait(driver, 10).until(
            ec.presence_of_all_elements_located((By.XPATH, '//*[@id="resultsTable"]/tbody/tr/td/a')))
        # companies = driver.find_elements_by_xpath('//*[@id="resultsTable"]/tbody/tr/td/a')
        links.extend([c.get_attribute('href') for c in companies])
        driver.find_element_by_xpath('//*[@id="paginationWrap"]/div[3]/a').click()
        print(i)
        sleep(5)
    return links


def startScraping(start, end, threads):
    ranges = defineScrapeRanges(start, end, threads)
    print(ranges)
    for i in range(threads):
        print(ranges[threads - i], ranges[threads - i - 1])
        t = threading.Thread(target=worker, args=( ranges[threads - i - 1], ranges[threads - i]))
        t.start()


def worker(start, end):
    current = start
    ending = end

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(
        executable_path=r'C:\Users\RaffaeleScarano\Università\Ing Dati\AssignmentTwo\chromedriver.exe', options=chrome_options)

    links = pickle.load(open('investing_links.p', 'rb'))
    while current < ending:
        pos = links[current].find('?')
        if pos == -1:
            driver.get(links[current] + "-company-profile/")
        else:
            driver.get(links[current][:pos] + "-company-profile/")

        if current == start:
            handle_cookies_popup(driver)

            sleep(2)
        else:
            sleep(1)
        try:
            name=driver.find_element_by_xpath('//*[@id="leftColumn"]/div[1]/h1').text
            ticker= name[name.find("(")+1:name.find(")")]
            companyMetadata = (
                ticker,
                name,
                driver.find_element_by_xpath('//*[@id="leftColumn"]/div[10]/div[1]/div[4]/span[3]/a').text,
                driver.find_element_by_xpath('//*[@id="leftColumn"]/div[10]/div[1]/div[1]/span[3]').text.replace("\n", " "),
                driver.find_element_by_xpath('//*[@id="leftColumn"]/div[8]/div[3]/p').text,
                driver.find_element_by_xpath('//*[@id="leftColumn"]/div[8]/div[1]/a').text,
                driver.find_element_by_xpath('//*[@id="leftColumn"]/div[8]/div[4]/p').text
            )
        except selenium.common.exceptions.NoSuchElementException as err:
            print(err)
            print(links[current])
            print(links[current][:pos] + "-company-profile/")
        insertCompany(companyMetadata)
        try:
            scrapeEmployees(driver.find_element_by_xpath('//*[@id="leftColumn"]/table/tbody'), ticker)
        except selenium.common.exceptions.NoSuchElementException as err:
            print(err)
            print(links[current])
            print(links[current][:pos] + "-company-profile/")

        current +=1



def defineScrapeRanges(start, end, threads):
    delta = end - start
    roundsEachThread = int(delta / threads)
    ranges = []
    for num in range(threads + 1):
        ranges.append(roundsEachThread * num)

    return ranges


if __name__ == '__main__':
    #links = get_all_links(config.PATH_TO_INVESTING)
    #pickle.dump(links, open('investing_links.p', 'wb'))
    #obj = pickle.load(open('investing_links.p', 'rb'))
    startScraping(0, 1248, 16)
    #print(len(obj))
    #worker(0, 1250)
