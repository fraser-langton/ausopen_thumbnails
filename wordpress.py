import atexit
import json
import os
import sys
import time

import pyautogui
import requests
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from merge_photos import read_csv, write_csv, read_day_csv

output_data = [['match_id', 'link', 'wp_link']]


def main():
    day = input('Day: ')
    driver = Driver()
    driver.login('flangton', 'jcQX3boISY9h')

    data = read_day_csv(day)[1:]
    data = read_csv(f'Output/Clipro day {day}.csv')[1:]

    files = os.listdir(f'Output/Day {day}')
    for (
            a1, a2, a3, a4, a5, match_id,
            t1_p1_l, t1_p1_f, a6, t1_p2_f, t1_p2_l, a7,
            t2_p1_l, t2_p1_f, a8, t2_p2_f, t2_p2_l, a9,
            a11, a12, photo_link, wp_link
    ) in data:
        if wp_link or not photo_link:
            output_data.append([a1, a2, a3, a4, a5, match_id,
                                t1_p1_l, t1_p1_f, a6, t1_p2_f, t1_p2_l, a7,
                                t2_p1_l, t2_p1_f, a8, t2_p2_f, t2_p2_l, a9,
                                a11, a12, photo_link, wp_link])
            continue

        file = f'{match_id}.png'
        filepath = f'Output/Day {day}/{file}'
        r = requests.get(photo_link)
        with open(filepath, 'wb') as f:
            f.write(r.content)
            print(f'{match_id}.png downloaded')

        r = requests.get(f'https://www.tennis.com.au/doc/ao2021-{match_id}')
        if r.status_code == 200:
            driver.update_doc(match_id, filepath, day)
        elif r.status_code == 404:
            driver.new_doc(match_id, filepath, day)
        link = driver.get_link()

        output_data.append([a1, a2, a3, a4, a5, match_id,
                            t1_p1_l, t1_p1_f, a6, t1_p2_f, t1_p2_l, a7,
                            t2_p1_l, t2_p1_f, a8, t2_p2_f, t2_p2_l, a9,
                            a11, a12, photo_link, link])

    write_csv(f'Output/Wordpress day {day}.csv', output_data)


def new_main():
    day = input('Day: ')
    driver = Driver()
    driver.login('flangton', 'jcQX3boISY9h')

    with open('clipro_links.json') as f:
        clipro_links = json.load(f)

    with open('wp_links.json') as f:
        wp_links = json.load(f)

    for match_id, clipro_link in clipro_links.items():
        file = f'{match_id}.png'
        filepath = f'Output/Day {day}/{file}'
        r = requests.get(clipro_link)
        with open(filepath, 'wb') as f:
            f.write(r.content)
            print(f'{match_id}.png downloaded')

        r = requests.get(f'https://www.tennis.com.au/doc/ao2021-{match_id}')
        if r.status_code == 200:
            driver.update_doc(match_id, filepath, day)
        elif r.status_code == 404:
            driver.new_doc(match_id, filepath, day)
        link = driver.get_link()

        wp_links[match_id] = link

        with open('wp_links.json', 'w') as f:
            json.dump(wp_links, f)


class Driver:
    def __init__(self):
        chromeOptions = webdriver.ChromeOptions()
        chromeOptions.add_argument("--start-maximized")
        prefs = {"download.default_directory": 'dl'}
        chromeOptions.add_experimental_option("prefs", prefs)
        chromeOptions.add_argument("user-data-dir=cache1")
        chromedriver = 'chromedriver.exe'
        self.driver = webdriver.Chrome(executable_path=chromedriver, options=chromeOptions)

    def login(self, un, pw):
        self.driver.get('https://www.tennis.com.au/wp-admin/edit.php?post_type=document')

        try:
            u_name = self.find_element_by_xpath('//*[@id="user_login"]')
            u_name.send_keys(un)
        except selenium.common.exceptions.TimeoutException:
            return

        password = self.find_element_by_xpath('//*[@id="user_pass"]')
        password.send_keys(pw)

        self.find_element_by_xpath('//*[@id="rememberme"]').click()
        self.find_element_by_xpath('//*[@id="wp-submit"]').click()

    def find_element_by_xpath(self, xpath):
        elem = WebDriverWait(self.driver, 5).until(expected_conditions.presence_of_element_located((By.XPATH, xpath)))
        return elem

    def new_doc(self, match_id, filepath, day):
        self.driver.get('https://www.tennis.com.au/wp-admin/post-new.php?post_type=document')
        time.sleep(3)

        doc_name = self.find_element_by_xpath('//*[@id="title"]')
        doc_name.send_keys(f'AO2021 {match_id}')

        filepath = os.path.abspath(filepath)
        file_input = self.driver.find_element_by_id('ta_uploaded_document')
        file_input.send_keys(filepath)
        time.sleep(1)

        self.publish()

    def update_doc(self, match_id, filepath, day):
        self.driver.get(
            f'https://www.tennis.com.au/wp-admin/edit.php?s={match_id}&post_status=all&post_type=document&action=-1&m=0&paged=1&action2=-1')
        time.sleep(4)

        doc_elem = self.driver.find_element_by_class_name('row-title')
        # doc_elem = self.find_element_by_xpath('//*[@id="post-140324"]/td[1]/strong/a')
        doc_elem.click()
        time.sleep(3)

        filepath = os.path.abspath(filepath)
        file_input = self.driver.find_element_by_id('ta_uploaded_document')
        file_input.send_keys(filepath)
        time.sleep(1)

        self.publish()

    def publish(self):
        button = self.find_element_by_xpath('//*[@id="publish"]')
        button.click()
        time.sleep(10)

    def get_link(self):
        link_elem = self.find_element_by_xpath('//*[@id="sample-permalink"]/a')
        link = link_elem.get_attribute('href')
        return str(link)


def exit_handler():
    write_csv('output_wp_crashed.csv', output_data)


if __name__ == '__main__':
    atexit.register(exit_handler)
    try:
        new_main()
    except Exception as e:
        print(e, file=sys.stderr)
        write_csv('output_wp_crashed.csv', output_data)
        raise (e)
