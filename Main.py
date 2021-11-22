from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
import sqlite3 as lite
import threading

def readAllRounds():
    con = lite.connect('test.db')

    with con:

        cur = con.cursor()
        cur.execute("SELECT * FROM Round group  by id")

        rows = cur.fetchall()

        return [row for row in rows]


def insertRound(roundMetadata):
    try:
        con = lite.connect('test.db')

        cur = con.cursor()
        cur.execute(
            "insert into Round values({},{},{},'{}','{}')".format(roundMetadata["roundId"], roundMetadata["day"],
                                                                  roundMetadata["crashPoint"], roundMetadata["hash"],
                                                                  roundMetadata["secret"]))

        con.commit()
    except lite.Error:
        if con:
            con.rollback()
    finally:
        if con:
            con.close()


def getMinRound():
    con = lite.connect('test.db')

    with con:

        cur = con.cursor()
        cur.execute("SELECT min(id) FROM Round")

        rows = cur.fetchall()

        return rows[0][0]

def scrapeRound(table,currentRound):
    trs = table.find_elements(By.TAG_NAME, "tr")
    rawData = [td.text for td in trs]
    roundMetadata = {
                    "roundId": currentRound,
                    "day": rawData[1].split(" ")[-1],
                    "crashPoint": rawData[2].split(" ")[-1][1:],
                    "hash": rawData[3].split(" ")[-1],
                    "secret": rawData[4].split(" ")[-1]
                }
    insertRound(roundMetadata)


def worker(start, end):
    currentRound = start
    endingRound = end

    driver = webdriver.Chrome(executable_path='/Users/raffaele/Downloads/chromedriver')
    sleep(3)
    driver.get("https://www.wtfskins.com/login")
    sleep(1)
    driver.find_element_by_css_selector(".form-check-input.ng-untouched.ng-pristine.ng-valid").click()
    driver.find_element_by_css_selector(".form-check-input.ng-untouched.ng-pristine.ng-valid").click()
    sleep(0.5)
    driver.find_element_by_css_selector(".enter-button.pointer").click()

    while currentRound != endingRound:
        driver.get("https://www.wtfskins.com/crash/history/round/" + str(currentRound))
        sleep(2)
        scrapeRound(driver.find_element_by_class_name("table"), currentRound)
        currentRound -= 1


def startScraping(start, end, threads):
    ranges = defineScrapeRanges(start, end, threads)
    print(ranges)
    for i in range(threads):
        t = threading.Thread(target=worker, args=(ranges[threads - i], ranges[threads - i - 1],))
        t.start()

def defineScrapeRanges(start, end, threads):
    delta = start - end
    roundsEachThread = int(delta/threads)
    ranges = []
    for num in range(threads+1):
        ranges.append(roundsEachThread*num)
    for i in range(len(ranges)):
        ranges[i] += end
    return ranges


if __name__ == '__main__':
    startScraping(18000, 17000, 4)