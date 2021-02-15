import json
import os
import sys
import time
import urllib

import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
import atexit

import pyautogui

from get_schedule import get_schedule, get_matches
from merge_photos import get_image_by_name, read_csv, write_csv, read_day_csv

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
            t1_img_name = get_image_by_name(t1, files, mappings, ask=ask)
            t2_img_name = get_image_by_name(t2, files, mappings, ask=ask)
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


def new_main():
    day = input("Day: ")

    driver = Driver()
    driver.login('TAadmin', 'TA2020_x4t')

    # day = 2
    # round_ = (int(day) + 1) // 2

    with open('mappings.json') as f:
        mappings = json.load(f)

    with open('clipro_links.json') as f:
        clipro_links = json.load(f)

    with open('wp_links.json') as f:
        wp_links = json.load(f)

    files = [str(f) for f in os.listdir('imgs')]
    try:
        os.mkdir(f'Output/Day {day}')
    except FileExistsError:
        pass

    data = get_matches(day)
    for match in data.values():
        if not ('WS' in match['match_id'] or 'MS' in match['match_id']):
            continue

        t1_p1_l, t1_p1_f = match['players'][0][0]['last_name'], match['players'][0][0]['first_name']
        try:
            t1_p2_l, t1_p2_f = match['players'][0][1]['last_name'], match['players'][0][1]['first_name']
        except IndexError:
            t1_p2_l, t1_p2_f = None, None
        t2_p1_l, t2_p1_f = match['players'][1][0]['last_name'], match['players'][1][0]['first_name']
        try:
            t2_p2_l, t2_p2_f = match['players'][1][1]['last_name'], match['players'][1][1]['first_name']
        except IndexError:
            t2_p2_l, t2_p2_f = None, None

        t1, t2 = (t1_p1_l, t1_p1_f, t1_p2_l, t1_p2_f), (t2_p1_l, t2_p1_f, t2_p2_l, t2_p2_f)

        photo_link = clipro_links.get(match['match_id'], None)
        wp_link = wp_links.get(match['match_id'], None)

        if photo_link or wp_link:
            output_data.append([match['match_id'],
                                t1_p1_l, t1_p1_f, t1_p2_f, t1_p2_l,
                                t2_p1_l, t2_p1_f, t2_p2_f, t2_p2_l,
                                photo_link, wp_link])
            continue
        try:
            driver.create_graphic()
            ask = False
            t1_img_name = get_image_by_name(t1, files, mappings, ask=ask)
            t2_img_name = get_image_by_name(t2, files, mappings, ask=ask)
            time.sleep(5)

            if t1_img_name is None or t2_img_name is None:
                output_data.append([match['match_id'],
                                    t1_p1_l, t1_p1_f, t1_p2_f, t1_p2_l,
                                    t2_p1_l, t2_p1_f, t2_p2_f, t2_p2_l,
                                    'https://www.tennis.com.au/doc/ao2021-placeholder', None])
                continue

            # Left name
            driver.input_by_xpath('//*[@id="App"]/div[2]/div/div[5]/div/div[2]/div/div[1]/input', t1_p1_l)

            # Right name
            driver.input_by_xpath('//*[@id="App"]/div[2]/div/div[5]/div/div[2]/div/div[2]/input', t2_p1_l)

            # Round
            round_ = get_round(match['match_id'])
            driver.input_by_xpath('//*[@id="App"]/div[2]/div/div[5]/div/div[2]/div/div[3]/input', f'Round {round_}')

            # Left player image
            driver.click_by_xpath('//*[@id="App"]/div[2]/div/div[6]/div[1]/div/div[2]/div/div[1]/div[2]/span/button')
            driver.input_by_xpath(
                '//*[@id="poppers"]/div/div/input',
                f"https://raw.githubusercontent.com/fraser-langton/ausopen_thumbnails/master/imgs/{urllib.parse.quote(t1_img_name)}"
            )
            driver.click_by_xpath('//*[@id="poppers"]/div/div/button')
            time.sleep(7)
            driver.click_by_xpath('//*[@id="App"]/div[2]/div/div[1]/div/div/div[2]/div[3]/button[2]')

            # Right player image
            driver.click_by_xpath('//*[@id="App"]/div[2]/div/div[6]/div[1]/div/div[2]/div/div[2]/div[2]/span/button')
            driver.input_by_xpath(
                '//*[@id="poppers"]/div/div/input',
                f"https://raw.githubusercontent.com/fraser-langton/ausopen_thumbnails/master/imgs/{urllib.parse.quote(t2_img_name)}"
            )
            driver.click_by_xpath('//*[@id="poppers"]/div/div/button')
            time.sleep(7)
            driver.click_by_xpath('//*[@id="App"]/div[2]/div/div[1]/div/div/div[2]/div[3]/button[2]')

            # driver.input_file_by_xpath(
            #     '//*[@id="App"]/div[2]/div/div[6]/div[1]/div/div[2]/div/div[1]/div[2]/button', t1_img_name)
            # driver.input_file_by_xpath(
            #     '//*[@id="App"]/div[2]/div/div[6]/div[1]/div/div[2]/div/div[2]/div[2]/button', t2_img_name)
            # time.sleep(20)

            time.sleep(4)
            driver.click_by_xpath('//*[@id="App"]/div[2]/div/div[6]/div[2]/button[2]')
            time.sleep(20)

            elem = driver.find_element_by_xpath('//*[@id="App"]/div[2]/div/div[2]/div[2]/div/div[2]/div[1]/div/img')
            url = elem.get_attribute('src')

        except selenium.common.exceptions.TimeoutException as e:
            url = None
            print(e, file=sys.stderr)

        clipro_links[match['match_id']] = url
        with open('clipro_links.json', 'w') as f:
            json.dump(clipro_links, f)

        output_data.append([match['match_id'],
                            t1_p1_l, t1_p1_f, t1_p2_f, t1_p2_l,
                            t2_p1_l, t2_p1_f, t2_p2_f, t2_p2_l,
                            url, wp_link])

    write_csv(f'Output/Clipro day {day}.csv', output_data)

    with open('mappings.json', 'w') as f:
        json.dump(mappings, f)


def get_round(match_id):
    r = int(match_id[2])
    if r > 4:
        return {
            5: 'QF',
            6: 'SF',
            7: 'Final'
        }[r]
    return r


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
        new_main()
    except Exception as e:
        print(e, file=sys.stderr)
        write_csv('output_crashed.csv', output_data)
        raise (e)
