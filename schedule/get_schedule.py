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
import requests


def get_schedule(day):
    r = requests.get(f"https://prod-scores-api.ausopen.com/year/2021/period/MD/day/{day}/schedule")
    data = r.json()

    return data
