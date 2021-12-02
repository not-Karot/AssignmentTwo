import selenium.common.exceptions
from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
import sqlite3 as lite
import threading
import pickle
import logging
import re
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options

import config



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
                             (ticker, name, website, headquarter, employees, industry, source) 
                             VALUES ( ?, ?, ?, ?, ?, ?, "yahoo");"""

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
                                VALUES (?, ?, ?, "yahoo");"""

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
        tds = tr.find_elements(By.TAG_NAME, "span")
        rawData = (
            tds[0].text,
            tds[1].text,
            currentCompany
        )

        insertEmployee(rawData,)


def handle_cookies_popup(driver):
    sleep(1)
    driver.find_element_by_xpath('/html/body/div/div/div/div/form/div[2]/div[2]/button').click()
    sleep(1)


def get_all_links(path):
    driver = webdriver.Chrome(
        executable_path=r'C:\Users\RaffaeleScarano\Università\Ing Dati\AssignmentTwo\chromedriver.exe')

    driver.get(path)
    handle_cookies_popup(driver)
    links = []
    end = 12
    for i in range(0, end):
        companies = WebDriverWait(driver, 10).until(
            ec.presence_of_all_elements_located((By.XPATH, '//*[@id="scr-res-table"]/div[1]/table/tbody/tr/td/a')))
        # companies = driver.find_elements_by_xpath('//*[@id="resultsTable"]/tbody/tr/td/a')
        links.extend([c.get_attribute('href') for c in companies])
        driver.find_element_by_xpath('//*[@id="scr-res-table"]/div[2]/button[3]').click()
        print(i)
        sleep(5)
    return links


def startScraping(start, end, threads):
    ranges = defineScrapeRanges(start, end, threads)
    print(ranges)
    for i in range(threads):
        print(ranges[threads - i], ranges[threads - i - 1])
        t = threading.Thread(target=worker, args=(ranges[threads - i - 1], ranges[threads - i]))
        t.start()


def worker(start, end):

    current = start
    ending = end

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(
        executable_path=r'C:\Users\RaffaeleScarano\Università\Ing Dati\AssignmentTwo\chromedriver.exe',
        options=chrome_options)

    links = pickle.load(open('yahoo_links.p', 'rb'))
    while current < ending:
        # name, website, headquarter, employees, industry, type, source)
        pos = links[current].find('?')
        if pos == -1:
            driver.get(links[current] + "/profile/")
        else:
            driver.get(links[current][:pos] + "/profile/")
        if current == start:
            handle_cookies_popup(driver)
            sleep(2)
        else:
            sleep(1)

        try:
            headquarter = ""
            for e in driver.find_elements_by_xpath(
                    '/html/body/div[1]/div/div/div[1]/div/div[3]/div[1]/div/div[1]/div/div/section/div[1]/div/div/p[1]'):
                headquarter+= e.text.replace("\n", " ")
            try:
                employees= int(driver.find_element_by_xpath(
                    '//*[@id="Col1-0-Profile-Proxy"]/section/div[1]/div/div/p[2]/span[6]/span').text.replace(",", ""))
            except selenium.common.exceptions.NoSuchElementException as err:
                print("No such employees number")
                employees=0

            ticker = str(driver.current_url).split("/")[4]
            companyMetadata = (
                ticker,
                driver.find_element_by_xpath('//*[@id="Col1-0-Profile-Proxy"]/section/div[1]/div/h3').text,
                driver.find_element_by_xpath('//*[@id="Col1-0-Profile-Proxy"]/section/div[1]/div/div/p[1]/a[2]').text,
                headquarter,
                employees,
                driver.find_element_by_xpath('//*[@id="Col1-0-Profile-Proxy"]/section/div[1]/div/div/p[2]/span[4]').text
            )
            insertCompany(companyMetadata)
        except selenium.common.exceptions.NoSuchElementException as err:
            print(err)
            print(links[current])
            print(links[current][:pos] + "/profile/")
        try:
            scrapeEmployees(
                driver.find_element_by_xpath('//*[@id="Col1-0-Profile-Proxy"]/section/section[1]/table/tbody'), ticker)
        except selenium.common.exceptions.NoSuchElementException as err:
            print(err)
            print(links[current])
            print(links[current][:pos] + "/profile/")

        current += 1


def defineScrapeRanges(start, end, threads):
    delta = end - start
    roundsEachThread = int(delta / threads)
    ranges = []
    for num in range(threads + 1):
        ranges.append(roundsEachThread * num)

    return ranges


if __name__ == '__main__':
    links = get_all_links(config.PATH_TO_YAHOO)
    pickle.dump(links, open('yahoo_links.p', 'wb'))
    startScraping(0, 1200, 16)

