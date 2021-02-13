"""
fetch("https://prod-scores-api.ausopen.com/year/2021/period/MD/day/5/schedule", {
  "headers": {
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9",
    "if-none-match": "\"efd31ea89f53f677b52da1345d24a570\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site"
  },
  "referrer": "https://ausopen.com/",
  "referrerPolicy": "strict-origin-when-cross-origin",
  "body": null,
  "method": "GET",
  "mode": "cors",
  "credentials": "omit"
});
"""
import json
import os

import requests

from merge_photos import get_image_by_id


def get_schedule(day):
    r = requests.get(f"https://prod-scores-api.ausopen.com/year/2021/period/MD/day/{day}/schedule")
    data = r.json()

    return data


def get_matches(day):
    data = get_schedule(day)

    matches = {}

    teams = {i['uuid']: i for i in data['teams']}
    players = {i['uuid']: i for i in data['players']}

    for court in data['schedule']['courts']:
        for session in court['sessions']:
            for match in session['activities']:
                match['players'] = []
                match_teams = [teams.get(team['team_id']) for team in match['teams']]
                for team in match_teams:
                    match_players = [players.get(p) for p in team['players']]
                    match['players'].append(match_players)
                matches[match['match_id']] = match

    return matches


def check_images(data):
    with open('data_temp.json', 'w') as f:
        json.dump(data, f)

    teams = {i['uuid']: i for i in data['teams']}
    players = {i['uuid']: i for i in data['players']}

    with open('imgs/player-photo-mappings.json') as f:
        mapping = json.load(f)

    files = [str(f) for f in os.listdir('imgs')]

    for court in data['schedule']['courts']:
        for session in court['sessions']:
            for match in session['activities']:
                match_teams = [teams.get(team['team_id']) for team in match['teams']]
                for team in match_teams:
                    match_players = [players.get(p) for p in team['players']]
                    match_players_images = [get_image_by_id(p, files, mapping) for p in match_players]
                    if all([img is None for img in match_players_images]):
                        match_players_names = " / ".join([f"{p['first_name']} {p['last_name']}" for p in match_players])
                        print(match['match_id'], match_players_names)


def check_images_by_schedule():
    day = input("Day: ")
    # with open('data_temp.json') as f:
    #     data = json.load(f)
    data = get_schedule(day)
    check_images(data)


def check_images_by_winners():
    day = input("Day: ")
    # with open('data_temp.json') as f:
    #     data = json.load(f)
    data = get_schedule(int(day) - 2)

    for court in data['schedule']['courts']:
        for session in court['sessions']:
            for match in session['activities']:
                t1_score = len([i for i in match['teams'][0]['score'] if i['winner']])
                t2_score = len([i for i in match['teams'][1]['score'] if i['winner']])
                if t1_score > t2_score:
                    del match['teams'][1]
                else:
                    del match['teams'][0]

    check_images(data)


def check_match():
    match_id = input('Match ID: ').strip().upper()
    r = requests.get(
        f'https://itp-ao.infosys-platforms.com/api/match-beats/data/year/2021/eventId/580/matchId/{match_id}')
    data = r.json()
    with open('imgs/player-photo-mappings.json') as f:
        mapping = json.load(f)
    files = [str(f) for f in os.listdir('imgs')]
    for team in range(1, 3):
        match_players = []
        for player in range(1, 3):
            if not data['playerData'][f'tm{team}Ply{player}Id']:
                continue
            match_players.append({
                'player_id': data['playerData'][f'tm{team}Ply{player}Id'],
                'first_name': data['playerData'][f'tm{team}Ply{player}FirstName'],
                'last_name': data['playerData'][f'tm{team}Ply{player}LastName'],
            })
        match_players_images = [get_image_by_id(p, files, mapping) for p in match_players]
        print(
            data['matchId'],
            " / ".join([f"{p['first_name']} {p['last_name']}" for p in match_players]),
            '-', " / ".join([str(i) for i in match_players_images])
        )


if __name__ == '__main__':
    # get_matches(6)
    # check_match()
    # check_images_by_schedule()
    check_images_by_winners()
