from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time

import xlrd
from os import listdir, remove
from os.path import isfile, join
import os
import csv

from string import Template
from Archtics import QuandooGetTables


########################################################################################################################

RESTAURANT_NAMES = ['88 Melbourne', 'Laneway Club', 'Glasshouse', 'Nobu', 'Rockpool', 'Chef Series', 'Beijing Betty',
                    'Showcourt', 'Vault']

SESSION_NAMES = ['Mon 14 AM', 'Mon 14 PM', 'Tue 15 AM', 'Tue 15 PM', 'Wed 16 AM', 'Wed 16 PM', 'Thu 17 AM', 'Thu 17 PM',
                 'Fri 18 AM', 'Fri 18 PM', 'Sat 19 AM', 'Sat 19 PM', 'Sun 20 AM', 'Sun 20 PM', 'Mon 21 AM', 'Mon 21 PM',
                 'Tue 22 AM', 'Tue 22 PM', 'Wed 23 AM', 'Wed 23 PM', 'Thu 24 AM', 'Thu 24 PM',
                 'Fri 25 PM', 'Sat 26 PM', 'Sun 27 PM']

###########################################################

URL = "https://admin.quandoo.com/#/auth/signin"
TITLE = "Quandoo Business Center"
UN_ELEM = "login"
LOGINS = [
    ("menright@tennis.com.au", "Tennis2019",
     [
         "Nobu",
         "Sun Kitchen",
         # "56 by The Glasshouse",
         # "88 Melbourne",
         # "Beijing Betty",
         # "Showcourt",
         # "Vault"
     ]),
    ("nicole.bergin@tennis.com.au", "Tennis2019",
     [
         "Rockpool"
     ]),
    ("kfryer@tennis.com.au", "Tennis2019",
     [
         "Chef Series"
     ]),
    ("gframe@tennis.com.au", "Tennis2019",
     [
         "Glasshouse"
     ])
]
PW_ELEM = "password"
PRE = "https://admin.quandoo.com/#/app/"
POST = "/reports?country=AU"
BASE = 0
DATES = [
    "01/20/2020 - 01/21/2020",
    "01/22/2020 - 01/23/2020",
    "01/24/2020 - 01/25/2020",
    "01/26/2020 - 01/27/2020",
    "01/28/2020 - 01/29/2020",
    "01/30/2020 - 01/31/2020",
    "02/01/2020 - 02/01/2020",
    "02/02/2020 - 02/02/2020",
]
ELEM_DELAY = .2
DELAY = .5

###########################################################

DOWNLOADS_PATH = "M:\Corporates\AO2020\Archtics\Availibilty Spreadsheets\data\quandoo partials\\"
ARCHIVE_PATH = "M:/Corporates/AO2019/FL/AO/Quandoo Report Archive/"
DRIVER_PATH = "M:\Corporates\AO2019\FL\AO/reports\chromedriver.exe"
REPORT_PATH = "M:\Corporates\AO2020\Archtics\Availibilty Spreadsheets\data"
HEADER = 2
REST_FILE_INDEX = 6

###########################################################

EMAIL = "frasers.python@gmail.com"
PASSWORD = "montY_299792458"
CONTACTS = [("fraser.clydesdale@tennis.com.au", "Fraser"),
            # ("smorgan@tennis.com.au", "Sam"),
            # ("paige.zotti@tennis.com.au", "Paige")
            ]
FILENAME = 'Quandoo report.csv'

Q_BOOKING_ID = 0
Q_COMPANY = 1
Q_CONTACT = 2
Q_EMAIL = 3
Q_PAX = 4
Q_TABLES = 5
Q_AREA = 6
Q_RES_NOTE = 7
Q_DATE_MADE = 8
Q_RES_TAG = 9
Q_AUTO_TAG = 10

REMOVE = True


# REMOVE = False

########################################################################################################################
########################################################################################################################


def main():
    print("LOOP STARTED\n")

    # report()
    # combine_files()
    # qua_sheets()
    # ava_sheet()
    # exit()

    for f in os.listdir(DOWNLOADS_PATH):
        os.remove(DOWNLOADS_PATH + f)

    report()

    done = False
    while not done:
        try:
            combine_files()
            done = True
        except:
            enter = input(
                "\n!!!ERROR!!! - !!!ERROR!!! - !!!ERROR!!!\n\nPlease exit all combine_files() files and press Y once done:\n").upper()

    QuandooGetTables.main()

    print("\nLOOP ENDED\n\n" + 3 * (54 * "-" + "\n"))


########################################################################################################################
########################################################################################################################


def login(un, pw):
    # username
    elem = driver.find_element_by_name(UN_ELEM)
    elem.clear()
    elem.send_keys(un)

    # password
    elem = driver.find_element_by_name(PW_ELEM)
    elem.clear()
    elem.send_keys(pw)
    elem.send_keys(Keys.RETURN)

    print("Logging in:", un)

    time.sleep(5)


def logout(un):
    elem = driver.find_element_by_class_name("logout")
    elem.click()

    print("Logging out:", un)
    print()
    time.sleep(5)


def wait(dur):
    for i in range(dur, 0, -1):
        print("\tWaiting:", i)
        time.sleep(1)
    print()


def run_report(rest):
    # click into saved report
    click('//*[@id="app"]/div/div[2]/ui-view/div/div[3]/table/tbody/tr/td[2]/span')

    for date in DATES:
        # date text box
        clear_date('//*[@id="app"]/div/div[2]/ui-view/ui-view/div/div/form/div[1]/div/input')
        enter_date('//*[@id="app"]/div/div[2]/ui-view/ui-view/div/div/form/div[1]/div/input', date)

        # click apply
        click('//*[@id="app"]/div/div[2]/ui-view/ui-view/div/div/div[1]/h1')

        # click run & download
        click('//*[@id="app"]/div/div[2]/ui-view/ui-view/div/div/form/div[2]/div[1]/div[3]/button')

        # choose excel
        click('//*[@id="app"]/div/div[2]/ui-view/ui-view/div/div/form/div[2]/div[1]/div[3]/ul/li[1]/a/span')

        # click download
        click('//*[@id="app"]/div/div[2]/ui-view/ui-view/div/div/form/div[2]/div[1]/div[3]/div/a')

        print("\t\tDownloading report for:", date)


def click(xpath):
    time.sleep(DELAY)
    try:
        elem = driver.find_element_by_xpath(xpath)
        time.sleep(ELEM_DELAY)
        elem.click()
        # print("SUCCESS")
    except:
        # print("FAILURE - TRYING AGAIN")
        click(xpath)


def clear_date(xpath):
    time.sleep(DELAY)
    try:
        elem = driver.find_element_by_xpath(xpath)
        elem.clear()
    except:
        clear_date(xpath)


def enter_date(xpath, date):
    time.sleep(DELAY)
    try:
        elem = driver.find_element_by_xpath(xpath)
        elem.clear()
        elem.send_keys(date)
        # print("SUCCESS")
    except:
        # print("FAILURE - TRYING AGAIN")
        enter_date(xpath, date)


###########################################################


def write_csv(data, path):
    with open(path, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(data)
    return


def read_csv(filename, header=0):
    with open(filename) as file:
        reader = csv.reader(file)
        data = [row for row in reader]
    return data[header:]


###########################################################


def read_template(filename):
    with open(filename, 'r', encoding='utf-8') as template_file:
        template_file_content = template_file.read()
    return Template(template_file_content)


########################################################################################################################


def report():
    driver.get(URL)

    for un, pw, r in LOGINS:
        login(un, pw)

        # access reporting of base restaurant
        click('//*[@id="app"]/aside-menu/div/div/main-nav/nav/ul/li[6]/a')
        print("\tAccessing reporting for:", r[BASE])
        run_report(r[BASE])

        # access reporting peripheral restaurants
        for restaurant in r[1:]:

            # search for restaurant
            click('//*[@id="app"]/navbar-header/sub-navbar-header/ul/li[1]/a/b')

            # open new restaurant
            done = False
            while not done:
                try:
                    elem = driver.find_element_by_xpath(
                        '//*[@id="app"]/navbar-header/sub-navbar-header/ul/li[1]/ul/div/input')
                    time.sleep(.5)
                    elem.clear()
                    elem.send_keys(restaurant)
                    time.sleep(.5)
                    elem.send_keys(Keys.ENTER)
                    done = True
                except:
                    done = False
            print("\tAccessing reporting for:", restaurant)
            time.sleep(5)

            # close current tab
            # driver.switch_to.window(driver.window_handles[0])
            # driver.close()

            # changing tabs
            driver.switch_to.window(driver.window_handles[-1])

            run_report(restaurant)

        logout(un)

    print("Reporting successful\n")


###########################################################


def combine_files():
    INPUT_ID = 0
    INPUT_FIRST_NAME = 1
    INPUT_LAST_NAME = 2
    INPUT_EMAIL_ADDRESS = 3
    INPUT_DATE = 4
    INPUT_START = 5
    INPUT_STATUS = 6
    INPUT_PEOPLE = 7
    INPUT_TABLE_NUMBER = 8
    INPUT_AREAS = 9
    INPUT_RESERVATION_NOTE = 10
    INPUT_CREATION_DATE = 11
    INPUT_RESERVATION_CATEGORY = 12

    RESTAURANT = 0

    files = [f for f in listdir(DOWNLOADS_PATH) if isfile(join(DOWNLOADS_PATH, f)) and "xls" in f]

    main_array = [
        ["Restaurant", "Booking_ID", "Contact", "Company", "Email", "Date", "Start", "Status",
         "Pax", "Table", "Area", "Res Note", "Date Made", "Res Tag", "End", "data"]]
    to_remove = []

    booking_ids = []

    for file in files:
        try:
            restaurant = file.split("-")[REST_FILE_INDEX].strip("_").replace("_", " ")
            workbook = xlrd.open_workbook(DOWNLOADS_PATH + file)
            sheet = workbook.sheet_by_index(0)
            for i in range(HEADER, sheet.nrows):
                if "CANCEL" not in sheet.row_values(i)[INPUT_STATUS]:
                    if sheet.row_values(i)[0] in booking_ids:
                        print("\n__DUPLICATE__\n{}\n{}".format(file, sheet.row_values(i)))
                    else:
                        main_array.append([restaurant] + sheet.row_values(i))
                        booking_ids.append(sheet.row_values(i)[0])

            to_remove.append(DOWNLOADS_PATH + file)
        except IndexError:
            print(file, "is not valid")

    while True:
        try:
            write_csv(main_array, join(REPORT_PATH, FILENAME))
            break
        except PermissionError as e:
            print("{} waiting 5 seconds".format(e))
            time.sleep(5)

    if REMOVE:
        for file in to_remove:
            remove(file)

    print("Sheets combined - csv created\n")


########################################################################################################################


if __name__ == '__main__':

    chromeOptions = webdriver.ChromeOptions()
    prefs = {"download.default_directory": DOWNLOADS_PATH}
    chromeOptions.add_experimental_option("prefs", prefs)
    chromedriver = DRIVER_PATH
    driver = webdriver.Chrome(executable_path=chromedriver, options=chromeOptions)

    while 1:
        main()
