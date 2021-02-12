import datetime
import json
import smtplib
import time
import requests

from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from SendEmail import BaseEmail
from merge_photos import read_csv, write_csv

BaseEmail.host, BaseEmail.port = 'smtp.gmail.com', 587
BaseEmail.connect()
BaseEmail._server.login('fraserlangton56@gmail.com', 'Tennis2020')

RECIPIENTS = 'flangton@tennis.com.au,rchand@tennis.com.au'
# RECIPIENTS = 'flangton@tennis.com.au'

TENNIS_URL = 'https://www.google.com/search?q=tennis'


def main():
    print(f"CHECKING NOW {datetime.datetime.now()}")
    check_game_finished()
    check_one_box()


def get_game_notified():
    try:
        game_notified = [i[0] for i in read_csv('game_notified.csv')]
    except IndexError:
        game_notified = []
    return game_notified


def get_onebox_notified():
    try:
        onebox_notified = [i[0] for i in read_csv('onebox_notified.csv')]
    except IndexError:
        onebox_notified = []
    return onebox_notified


def check_game_finished():
    r = requests.get(
        f'https://prod-scores-api.ausopen.com/year/2021/period/MD/day/{(datetime.date.today() - datetime.date(2021,2,7)).days}/results',
    )
    data = r.json()

    completed_matches = [i for i in data['matches'] if i['match_state'] == 'Complete']
    game_notified = get_game_notified()

    for match in completed_matches:
        if match['match_id'] not in game_notified:
            notify_game(match, game_notified)
            # pass


def check_one_box():
    driver.get(TENNIS_URL)
    time.sleep(3)
    game_notified = get_game_notified()
    onebox_notified = get_onebox_notified()

    page_source = ''
    divs = [
        ('Men', 'Singles'),
        ('Women', 'Singles'),
        ('Men', 'Doubles'),
        ('Women', 'Doubles'),
        ('Mixed', 'Doubles'),
    ]
    for a, b in divs:
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, f"//span[@jsslot]//span//span[contains(., '{a}') and contains(., '{b}')]"))).click()
        time.sleep(1)
        page_source += driver.page_source

    for match_id in game_notified:
        if match_id in onebox_notified:
            continue
        if match_id in page_source.upper():
            notify_onebox(match_id, onebox_notified)


def notify_game(match, game_notified):
    print(f'GAME NOTIFY {match["match_id"]}')
    email = BaseEmail(
        'flangton@tennis.com.au',
        RECIPIENTS,
        f'{match["match_id"]} GAME FINISHED',
        json.dumps(match, indent=2),
    )
    try:
        email.send()
    except smtplib.SMTPSenderRefused:
        BaseEmail.connect()
        BaseEmail._server.login('fraserlangton56@gmail.com', 'Tennis2020')
        email.send()
    game_notified.append(match['match_id'])
    write_csv('game_notified.csv', [[i] for i in game_notified])


def notify_onebox(match_id, onebox_notified):
    print(f'ONEBOX NOTIFY {match_id}')
    email = BaseEmail(
        'flangton@tennis.com.au',
        RECIPIENTS,
        f'{match_id} ONEBOX UP',
        f'{match_id} just appeared on one box: {TENNIS_URL}',
    )
    try:
        email.send()
    except smtplib.SMTPSenderRefused:
        BaseEmail.connect()
        BaseEmail._server.login('fraserlangton56@gmail.com', 'Tennis2020')
        email.send()
    onebox_notified.append(match_id)
    write_csv('onebox_notified.csv', [[i] for i in onebox_notified])


if __name__ == '__main__':
    driver = webdriver.Chrome('chromedriver.exe')
    while True:
        main()
        time.sleep(10)
