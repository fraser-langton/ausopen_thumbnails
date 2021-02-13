import difflib
import json
import os
from PIL import Image, ImageFont, ImageDraw
import csv


def main():
    # day = input("Day: ")
    day = 1
    round_ = (int(day) + 1) // 2

    with open('mappings.json') as f:
        mappings = json.load(f)

    logo = Image.open('logo.png')

    files = [str(f) for f in os.listdir('imgs')]
    try:
        os.mkdir(f'Output/Day {day}')
    except FileExistsError:
        pass

    data = read_day_csv(day)[1:]
    files = os.listdir(f'Output/Day {day}')
    for (
            _, _, _, _, _, match_id,
            t1_p1_l, t1_p1_f, _, t1_p2_l, t1_p2_f, _,
            t2_p1_l, t2_p1_f, _, t2_p2_l, t2_p2_f, _,
            *_, photo_link, wp_link
    ) in data:
        t1, t2 = (t1_p1_l, t1_p1_f, t1_p2_l, t1_p2_f), (t2_p1_l, t2_p1_f, t2_p2_l, t2_p2_f)

        p1_img_name = get_image_by_name(t1, files, mappings)
        p2_img_name = get_image_by_name(t2, files, mappings)

        p1_img = Image.open(f'imgs/{p1_img_name}')
        p2_img = Image.open(f'imgs/{p2_img_name}')
        merged = concat_left_right(p1_img, p2_img)
        add_logo(merged, logo)
        add_text(merged, p1, p2, round_)
        merged.save(f'Output/Day {day}/{match_id}.png')
    x = 1

    with open('mappings.json', 'w') as f:
        json.dump(mappings, f)


def read_csv(filename):
    with open(filename) as f:
        reader = csv.reader(f)
        data = [row for row in reader]
    return data


def read_day_csv(day):
    filename = f'Input/Schedule_202102{7 + int(day):02}.csv'
    data = read_csv(filename)
    for row in data:
        row += [''] * (22 - len(row))
    return data


def write_csv(filename, data):
    with open(filename, 'w', newline="") as f:
        writer = csv.writer(f)
        writer.writerows(data)


def concat_left_right(im1, im2):
    dst = Image.new('RGB', (im1.width + im2.width, im1.height))
    dst.paste(im1, (0, 0))
    dst.paste(im2, (im1.width, 0))
    return dst


def add_logo(img, logo):
    img.paste(logo, (0, 0), logo)


def add_text(img, p1, p2, round_):
    p1_last, p2_last = " ".join(p1.split()[1:]), " ".join(p2.split()[1:])

    font = ImageFont.truetype(r'‪C:\Windows\Fonts\micross.ttf', 150)

    back_colour = (0, 145, 210)
    margins = 60, 60, 20, 60  # l, r, u, d

    text = "HIGHLIGHTS"
    t_w, t_h = font.getsize(text)
    i_w, i_h = img.size
    y = i_h - t_h - 60
    x = margins[0]
    draw_text_w_background(img, (x, y), 'white', back_colour, text, font, margins)

    text = f"{p1_last.upper()} v {p2_last.upper()}"
    draw_text_w_background(img, (x, y - t_h - 1 * margins[2]), 'white', back_colour, text, font, margins)

    img.save('t.png')
    x = 1


def draw_text_w_background(img, xy, text_colour, back_colour, text, font, margins=(0, 0, 0, 0)):
    x, y = xy
    l, r, u, d = margins

    draw = ImageDraw.Draw(img)
    t_w, t_h = font.getsize(text)

    draw.rectangle((x - l, y - u, x + t_w + r, y + t_h + u), fill=back_colour)
    draw.text((x, y), text=text, fill=text_colour, font=font)


def key(team):
    p1_l, p1_f, p2_l, p2_f = team
    k = f'{p1_f} {p1_l}'
    if p2_f:
        k += f' / {p2_f} {p2_l}'
    return k


def get_image_by_name(team, files, mappings, ask=True):
    p1_l, p1_f, p2_l, p2_f = team

    img_name = mappings.get(key(team), None)
    if img_name is not None:
        return img_name

    img_names = [f for f in files if p1_f.lower() in f.lower() and p1_l.lower() in f.lower()]
    if p2_f:
        img_names += [f for f in files if p2_f.lower() in f.lower() and p2_l.lower() in f.lower()]

    if len(img_names) > 1:
        for (i, f) in enumerate(img_names):
            print(f'{i:<4}{f}')
        img_name = img_names[int(input(f'Which file for {key(team)}'))] if ask else None

    elif len(img_names) < 1:
        potential_matches = [f for f in files if p1_f.lower() in f.lower() or p1_l.lower() in f.lower()]
        if p2_f:
            potential_matches += [f for f in files if p2_f.lower() in f.lower() or p2_l.lower() in f.lower()]
        potential_matches += difflib.get_close_matches(f"{p1_f}_{p1_l}".upper(), files, n=3)
        if potential_matches:
            if ask:
                print(f"potential matches:")
                for m in potential_matches:
                    print(f'\t{m}')
            img_name = str(input(f'Enter EXACT filename for {key(team)}')) if ask else None
            img_name = img_name if img_name else None

    else:
        img_name = img_names[0]

    mappings[key(team)] = img_name

    return img_name


def get_image_by_id(player, files, mappings, ask=False):
    example_player = {
        'uuid': '2c09c0ce-a47d-459d-addd-1490477b449b',
        'nid': '5729',
        'player_id': 'ATPA853',
        'tour_id': 'ATPA853',
        'first_name': 'Marcelo',
        'last_name': 'Arevalo',
        'full_name': 'Marcelo Arevalo',
        'short_name': 'M. Arevalo',
        'gender': 'M',
        'nationality': {
            'uuid': '78ab5d65-9bbd-4bc2-b8c2-acba8a2fadbc',
            'name': 'El Salvador',
            'code': 'ESA',
            'flag': {
                'url': 'https://ausopen.com/sites/default/files/styles/flag_icon/public/2017-11/ESA_f.gif?itok=PaQRWrDN'
            }
        },
        'hero_image': {
            'url': 'https://ausopen.com/sites/default/files/styles/420x/public/2019_Marcelo_Arevalo_pp_h.png?itok=J3f3xvKI'
        },
        'hero_image_144': {
            'url': 'https://ausopen.com/sites/default/files/styles/144x144/public/2019_Marcelo_Arevalo_pp_h.png?itok=hBo3Bb9f'
        },
        'hero_image_240': {
            'url': 'https://ausopen.com/sites/default/files/styles/240x240/public/2019_Marcelo_Arevalo_pp_h.png?itok=P6AuOrPE'
        },
        'profile_image_104': {
            'url': 'https://ausopen.com/sites/default/files/styles/104x104/public/2019_Marcelo_Arevalo_pp_h.png?itok=IzZE-Vjf'
        },
        'profile_image_32': {
            'url': 'https://ausopen.com/sites/default/files/styles/32x32/public/2019_Marcelo_Arevalo_pp_h.png?itok=GEyFaYFP'
        },
        'image': {
            'url': 'https://ausopen.com/sites/default/files/styles/420x/public/2019_Marcelo_Arevalo_pp_t.png?itok=RPnUSZkF'
        },
        'player_icon': {
            'url': 'https://ausopen.com/sites/default/files/styles/96x96/public/2019_Marcelo_Arevalo_pp_t.png?itok=uKzs6WqD'
        },
        'rankings': [
            {
                'event': 'cb9599e0-4478-4b4e-98aa-996a54313df6',
                'ranking': '452'
            },
            {
                'event': '7639a625-a364-40e7-b958-5dac8a23d3f8',
                'ranking': '52'
            }
        ],
        'birth_place': 'Sonsonate, El Salvador',
        'dob': 'Sonsonate, El Salvador',
        'career_loses': '20',
        'career_prize_money': '746077',
        'career_titles': '0',
        'career_wins': '26',
        'coach': 'Yari Bernardo & Carlos Teixeira',
        'player_height': '76',
        'player_weight': '190',
        'turned_pro': '2012',
        'resident_of': 'Sonsonate, El Salvador',
        'events_contested': [
            'a86451f8-5e18-45f8-9f5d-a8f8f3a2bfa2',
            'b7b29bc2-c6ff-485a-b7df-e7fa50d69a81',
            '2cb3e363-b3db-4332-a05e-b25b54e9b45f',
            'b98061a1-47b2-431b-b6f4-5f75ec95b4a4'
        ],
        'profile_link': 'https://ausopen.com/players/el-salvador/marcelo-arevalo'
    }
    image_name = mappings.get(player['player_id'], None)
    if image_name is not None:
        return image_name

    team = player['last_name'], player['first_name'], None, None

    with open('mappings.json') as f:
        name_mappings = json.load(f)
    name_mappings = {}
    img_name = get_image_by_name(team, files, name_mappings, ask=ask)
    mappings[player['player_id']] = img_name

    return img_name


def highlight(element, effect_time=3, color="blue", border=5):
    """Highlights (blinks) a Selenium Webdriver element"""
    driver = element._parent

    def apply_style(s):
        driver.execute_script("arguments[0].setAttribute('style', arguments[1]);",
                              element, s)

    original_style = element.get_attribute('style')
    apply_style("border: {0}px solid {1};".format(border, color))
    time.sleep(effect_time)
    apply_style(original_style)


if __name__ == '__main__':
    main()
