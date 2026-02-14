import datetime
import json
import sqlite3
import utils
import requests
import os
from dotenv import load_dotenv
from datetime import datetime, timezone

con = sqlite3.connect('stats.sqlite')
con.row_factory = sqlite3.Row
load_dotenv()
API_KEY = os.getenv('API_KEY')
MOVIE_POINTS = 50
EPISODE_POINTS = 20

def get_users_api():
    params = {
        'api_key' : API_KEY
    }
    response = requests.get('https://jelly.yannictoulouse.de/Users', params=params)
    return response.json()

def insert_user(user):
    cur = con.cursor()
    cur.execute('INSERT OR IGNORE INTO users (id, name) VALUES (?, ?)', (user['Id'], user['Name']))
    con.commit()

def get_users():
    cur = con.cursor()
    return cur.execute('SELECT * FROM users ORDER BY upper(name) ASC').fetchall()

def get_plays_api(userid):
    params = {
        'api_key' : API_KEY,
        'SortBy' : 'DatePlayed',
        'SortOrder' : 'Descending',
        'IncludeItemTypes' : 'Movie,Episode',
        'Recursive' : 'true',
        'Limit' : 200
    }
    response = requests.get('https://jelly.yannictoulouse.de/Users/' + userid + '/Items', params=params)
    return response.json()

def insert_plays(userid, plays):
    cur = con.cursor()
    last_processed = cur.execute('SELECT last_processed_played_date FROM users WHERE id = ?', (userid,)).fetchone()[0]
    max_last_played = datetime.fromtimestamp(0, tz=timezone.utc)

    if last_processed:
        last_processed = utils.parse_jellyfin_date(last_processed.replace('Z', '+00:00'))
        max_last_played = last_processed
    else:
        last_processed = datetime.fromtimestamp(0, tz=timezone.utc)

    for item in plays['Items']:
        last_played = utils.parse_jellyfin_date(item.get('UserData', {}).get('LastPlayedDate', '1970-01-01T00:00:00Z').replace('Z', '+00:00'))
        if last_played <= last_processed:
            break

        is_played = item.get('UserData', {}).get('Played', None)
        completion_ratio = item['UserData']['PlaybackPositionTicks'] / item['RunTimeTicks']
        if is_played and last_played > last_processed:
            cur.execute('INSERT OR IGNORE INTO plays (user_id, item_id, date_played, completion_ratio) VALUES (?, ?, ?, ?)', (userid, item['Id'], last_played.isoformat(), completion_ratio))
            insert_item(item)
            if last_played > max_last_played:
                max_last_played = last_played
    con.commit()
    return max_last_played

def insert_item(item):
    cur = con.cursor()
    cur.execute('INSERT OR IGNORE INTO items (id, name, type, runtime_ticks) VALUES (?, ?, ?, ?)', (item['Id'], item['Name'], item['Type'], item['RunTimeTicks']))
    con.commit()

def insert_points(userid):
    cur = con.cursor()
    last_processed = cur.execute('SELECT last_processed_played_date FROM users WHERE id = ?', (userid,)).fetchone()[0]
    cur.execute('SELECT id, user_id, item_id, date_played FROM plays WHERE user_id = ? AND date(date_played) > date(?)', (userid, last_processed))
    plays = cur.fetchall()
    for play in plays:
        item_type = cur.execute('SELECT type from items WHERE id = ?', (play['item_id'],)).fetchone()[0]
        if item_type == 'Movie':
            points = MOVIE_POINTS
            cur.execute('INSERT INTO points_ledger (user_id, play_id, reason, points) VALUES (?, ?, ?, ?)', (userid, play['id'], 'Watched a movie', points))
        elif item_type == 'Episode':
            points = EPISODE_POINTS
            cur.execute('INSERT INTO points_ledger (user_id, play_id, reason, points) VALUES (?, ?, ?, ?)', (userid, play['id'], 'Watched an episode', points))
    con.commit()

def update_last_processed(userid, last_processed):
    cur = con.cursor()
    cur.execute('UPDATE users SET last_processed_played_date = ? WHERE id = ?', (last_processed.isoformat(), userid))
    con.commit()

def get_points(userid):
    cur = con.cursor()
    cur.execute('SELECT SUM(points) FROM points_ledger WHERE user_id = ?', (userid,))
    total_points = cur.fetchone()[0]
    return total_points if total_points else 0

def update_monthly_totals():
    cur = con.cursor()
    users = cur.execute('SELECT id FROM users').fetchall()
    for user in users:
        user_id = user['id']
        cur.execute('SELECT SUM(points) FROM points_ledger WHERE user_id = ? AND date(created_at) >= date("now", "start of month")', (user_id,))
        monthly_points = cur.fetchone()[0]
        if monthly_points is None:
            monthly_points = 0
        cur.execute('INSERT INTO monthly_totals (user_id, year, month, points) VALUES (?, ?, ?, ?) ON CONFLICT(user_id, year, month) DO UPDATE SET points = excluded.points', (user_id, datetime.now().year, datetime.now().month, monthly_points))
    con.commit()

def insert_daily_stats(users):
    cur = con.cursor()
    for user in users:
        playtime = 0
        user_id = user['Id']
        response = cur.execute('SELECT SUM(items.runtime_ticks) as total_runtime, COUNT(plays.item_id) as item_count FROM plays JOIN items ON plays.item_id = items.id WHERE user_id = ? AND date(date_played) >= date("now", "start of day") AND date(date_played) < date("now", "+1 day", "start of day")', (user_id,)).fetchall()
        items_completed = response[0]['item_count'] or 0
        playtime += (response[0]['total_runtime'] or 0) / 10000000 / 60
        cur.execute('INSERT OR IGNORE INTO daily_stats (user_id, date, watch_minutes, items_completed) VALUES (?, date("now", "start of day"), ?, ?)', (user_id, playtime, items_completed))
    con.commit()

def create_json():
    cur = con.cursor()
    users = get_users()
    users_dict = {}
    for user in users:
        user_id = user['id']
        daily_stats = cur.execute('SELECT * FROM daily_stats WHERE user_id = ? AND date(date) >= date("now", "start of day")', (user_id,)).fetchone()
        points_ledger = cur.execute('SELECT SUM(reason = "Watched a movie") as movies_completed, SUM(reason = "Watched an episode") as episodes_completed FROM points_ledger WHERE user_id = ?', (user_id,)).fetchone()
        monthly_totals = cur.execute('SELECT * FROM monthly_totals WHERE user_id = ?', (user_id,)).fetchall()
        users_dict[user_id] = {
            'name': user['Name'],
            'points' : get_points(user_id),
            'daily_stats': {
                'date' : daily_stats['date'],
                'watch_minutes' : daily_stats['watch_minutes'],
                'items_completed' : daily_stats['items_completed'],
            },
            'points_ledger': {
                'movies_watched' : points_ledger['movies_completed'],
                'episodes_completed' : points_ledger['episodes_completed'],
            },
            'monthly_totals': {}
        }

        for total in monthly_totals:
            year = total['year']
            month = total['month']

            if year not in users_dict[user_id]['monthly_totals']:
                users_dict[user_id]['monthly_totals'][year] = {}

            users_dict[user_id]['monthly_totals'][year][month] = {
                'points': total['points']
            }
    json.dump(users_dict, open('../data/users.json', 'w'), indent=2)

def main():
    users = get_users_api()
    for user in users:
        insert_user(user)
        last_processed = insert_plays(user['Id'], get_plays_api(user['Id']))
        insert_points(user['Id'])
        update_last_processed(user['Id'], last_processed)
        print(user['Name'] + ': ' + str(get_points(user['Id'])) + ' Points')
    update_monthly_totals()
    insert_daily_stats(users)
    create_json()


if __name__ == '__main__':
    main()