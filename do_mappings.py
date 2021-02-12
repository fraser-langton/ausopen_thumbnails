import json
import os

from merge_photos import read_csv, get_img_by_name, read_day_csv

day = input("Day: ")

with open('mappings.json') as f:
    mappings = json.load(f)

files = [str(f) for f in os.listdir('imgs')]
data = read_day_csv(day)[1:]

for (
        _, _, _, _, _, match_id,
        t1_p1_l, t1_p1_f, _, t1_p2_f, t1_p2_l, _,
        t2_p1_l, t2_p1_f, _, t2_p2_f, t2_p2_l, _,
        *_, photo_link, wp_link
) in data:
    t1, t2 = (t1_p1_l, t1_p1_f, t1_p2_l, t1_p2_f), (t2_p1_l, t2_p1_f, t2_p2_l, t2_p2_f)
    ask = True
    get_img_by_name(t1, files, mappings, ask=ask)
    get_img_by_name(t2, files, mappings, ask=ask)

with open('mappings.json', 'w') as f:
    json.dump(mappings, f)
