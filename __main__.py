import json
import os
import sys
import time

import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
import atexit

import pyautogui

from merge_photos import get_img_by_name, read_csv, write_csv, read_day_csv

output_data = [['match_id', 'link', 'wp_link']]


def main():
    day = input("Day: ")

    driver = Driver()
    driver.login('TAadmin', 'TA2020_x4t')

    # day = 2
    # round_ = (int(day) + 1) // 2

    with open('mappings.json') as f:
        mappings = json.load(f)

    files = [str(f) for f in os.listdir('imgs')]
    try:
        os.mkdir(f'Output/Day {day}')
    except FileExistsError:
        pass

    data = read_day_csv(day)[1:]
    for (
            a1, a2, a3, a4, a5, match_id,
            t1_p1_l, t1_p1_f, a6, t1_p2_f, t1_p2_l, a7,
            t2_p1_l, t2_p1_f, a8, t2_p2_f, t2_p2_l, a9,
            a11, a12, photo_link, wp_link
    ) in data:
        t1, t2 = (t1_p1_l, t1_p1_f, t1_p2_l, t1_p2_f), (t2_p1_l, t2_p1_f, t2_p2_l, t2_p2_f)
        if photo_link or wp_link:
            output_data.append([a1, a2, a3, a4, a5, match_id,
                                t1_p1_l, t1_p1_f, a6, t1_p2_f, t1_p2_l, a7,
                                t2_p1_l, t2_p1_f, a8, t2_p2_f, t2_p2_l, a9,
                                a11, a12, photo_link, wp_link])
            continue
            # continue
        try:
            driver.create_graphic()
            ask = False
            t1_img_name = get_img_by_name(t1, files, mappings, ask=ask)
            t2_img_name = get_img_by_name(t2, files, mappings, ask=ask)
            time.sleep(5)

            if t1_img_name is None or t2_img_name is None:
                output_data.append([a1, a2, a3, a4, a5, match_id,
                                    t1_p1_l, t1_p1_f, a6, t1_p2_f, t1_p2_l, a7,
                                    t2_p1_l, t2_p1_f, a8, t2_p2_f, t2_p2_l, a9,
                                    a11, a12, 'https://www.tennis.com.au/doc/ao2021-placeholder', None])
                continue

            driver.input_by_xpath('//*[@id="App"]/div[2]/div/div[5]/div/div[2]/div/div[1]/input', t1_p1_l)

            driver.input_by_xpath('//*[@id="App"]/div[2]/div/div[5]/div/div[2]/div/div[2]/input', t2_p1_l)

            round_ = match_id[2]
            driver.input_by_xpath('//*[@id="App"]/div[2]/div/div[5]/div/div[2]/div/div[3]/input', f'Round {round_}')

            driver.input_file_by_xpath(
                '//*[@id="App"]/div[2]/div/div[6]/div[1]/div/div[2]/div/div[1]/div[2]/button', t1_img_name)
            driver.input_file_by_xpath(
                '//*[@id="App"]/div[2]/div/div[6]/div[1]/div/div[2]/div/div[2]/div[2]/button', t2_img_name)
            time.sleep(20)

            driver.click_by_xpath('//*[@id="App"]/div[2]/div/div[6]/div[2]/button[2]')
            time.sleep(20)

            elem = driver.find_element_by_xpath('//*[@id="App"]/div[2]/div/div[2]/div[2]/div/div[2]/div[1]/div/img')
            url = elem.get_attribute('src')

        except selenium.common.exceptions.TimeoutException as e:
            url = None
            print(e, file=sys.stderr)

        output_data.append([a1, a2, a3, a4, a5, match_id,
                            t1_p1_l, t1_p1_f, a6, t1_p2_f, t1_p2_l, a7,
                            t2_p1_l, t2_p1_f, a8, t2_p2_f, t2_p2_l, a9,
                            a11, a12, url, None])

    write_csv(f'Output/Clipro day {day}.csv', output_data)

    with open('mappings.json', 'w') as f:
        json.dump(mappings, f)


class Driver:
    def __init__(self):
        chromeOptions = webdriver.ChromeOptions()
        chromeOptions.add_argument("--start-maximized")
        prefs = {"download.default_directory": 'dl'}
        chromeOptions.add_experimental_option("prefs", prefs)
        chromeOptions.add_argument("user-data-dir=cache")
        chromedriver = 'chromedriver.exe'
        self.driver = webdriver.Chrome(executable_path=chromedriver, options=chromeOptions)

    def login(self, un, pw):
        try:
            self.driver.get('https://www.clipro.tv/graphics/Create/League/tid/14618/sbid/none/details')
            username_input = self.driver.find_element_by_xpath('//*[@id="LoginPage"]/div[1]/div/form/div[1]/input')
            password_input = self.driver.find_element_by_xpath('//*[@id="LoginPage"]/div[1]/div/form/div[2]/input')
            button = self.driver.find_element_by_xpath('//*[@id="LoginPage"]/div[1]/div/form/button[1]')

            username_input.click()
            username_input.send_keys(un)

            password_input.click()
            password_input.send_keys(pw)

            button.click()

            time.sleep(1)

        except selenium.common.exceptions.NoSuchElementException as e:
            pass

    def create_graphic(self):
        self.driver.get('https://www.clipro.tv/graphics/Create/League/tid/14618/sbid/none/details')

    def my_graphics(self):
        button = self.driver.find_element_by_xpath('//*[@id="ActivityFlowBtns"]/button[2]')
        button.click()

    def find_element_by_xpath(self, xpath):
        elem = WebDriverWait(self.driver, 5).until(expected_conditions.presence_of_element_located((By.XPATH, xpath)))
        return elem

    def input_by_xpath(self, xpath, input_text):
        input_elem = self.driver.find_element_by_xpath(xpath)
        input_elem.send_keys(input_text)

    def click_by_xpath(self, xpath):
        elem = self.driver.find_element_by_xpath(xpath)
        elem.click()

    def input_file_by_xpath(self, xpath, file_path):
        input_elem = self.driver.find_element_by_xpath(xpath)
        input_elem.click()
        time.sleep(1)

        pyautogui.typewrite(os.path.abspath(f'imgs/{file_path}'))
        pyautogui.keyDown('Enter')
        time.sleep(1)
        self.click_by_xpath('//*[@id="App"]/div[2]/div/div[1]/div/div/div[2]/div[3]/button[2]')


def exit_handler():
    write_csv('output_crashed.csv', output_data)


if __name__ == '__main__':
    atexit.register(exit_handler)
    try:
        main()
    except Exception as e:
        print(e, file=sys.stderr)
        write_csv('output_crashed.csv', output_data)
        raise (e)
