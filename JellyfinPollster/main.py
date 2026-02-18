import datetime
import json
import sqlite3
import requests
import os
from dotenv import load_dotenv
from datetime import datetime, timezone

con = sqlite3.connect('stats.sqlite')
con.row_factory = sqlite3.Row
load_dotenv()
API_KEY = os.getenv('API_KEY')
JELLY_DOMAIN = os.getenv('JELLY_DOMAIN')
MOVIE_POINTS = 50
EPISODE_POINTS = 20

def get_users_api():
    params = {
        'api_key' : API_KEY
    }
    response = requests.get(JELLY_DOMAIN + '/Users', params=params)
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
    response = requests.get(JELLY_DOMAIN + '/Users/' + userid + '/Items', params=params)
    return response.json()

def insert_plays(userid, plays):
    cur = con.cursor()
    last_processed = cur.execute('SELECT last_processed_played_date FROM users WHERE id = ?', (userid,)).fetchone()[0]
    if last_processed is None:
        last_processed = datetime.fromtimestamp(0, tz=timezone.utc).isoformat()
    max_last_played = datetime.fromtimestamp(0, tz=timezone.utc).isoformat()

    if last_processed:
        max_last_played = last_processed
    else:
        last_processed = datetime.fromtimestamp(0, tz=timezone.utc).isoformat()

    for item in plays['Items']:
        last_played = datetime.fromisoformat(item.get('UserData', {}).get('LastPlayedDate', '1970-01-01T00:00:00Z').replace('Z', '+00:00')).isoformat()
        if last_played <= last_processed:
            break

        is_played = item.get('UserData', {}).get('Played', None)
        completion_ratio = item['UserData']['PlaybackPositionTicks'] / item['RunTimeTicks']
        if is_played and last_played > last_processed:
            cur.execute('INSERT OR IGNORE INTO plays (user_id, item_id, date_played, completion_ratio) VALUES (?, ?, ?, ?)', (userid, item['Id'], last_played, completion_ratio))
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
    if last_processed is None:
        last_processed = datetime.fromtimestamp(0, tz=timezone.utc).isoformat()
    cur.execute('SELECT items.runtime_ticks as "runtime_ticks", plays.id, user_id, item_id, date_played FROM plays JOIN items ON items.id = plays.item_id WHERE user_id = ? AND date(date_played) > date(?)', (userid, last_processed))
    plays = cur.fetchall()
    for play in plays:
        points = round(play['runtime_ticks'] / 10000000 / 60 * 0.5, 0)
        cur.execute('INSERT INTO points_ledger (user_id, play_id, reason, points) VALUES (?, ?, ?, ?)', (userid, play['id'], "Watched an Item", points))
    con.commit()

def update_last_processed(userid, last_processed):
    cur = con.cursor()
    cur.execute('UPDATE users SET last_processed_played_date = ? WHERE id = ?', (last_processed, userid))
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
        response = cur.execute('SELECT SUM(items.runtime_ticks) as total_runtime, COUNT(plays.item_id) as item_count FROM plays JOIN items ON plays.item_id = items.id WHERE user_id = ? AND date(date_played) >= date("now", "start of day") AND date(date_played) < date("now", "+1 day", "start of day")', (user_id,)).fetchone()
        items_completed = response['item_count'] or 0
        playtime += (response['total_runtime'] or 0) / 10000000 / 60
        cur.execute('INSERT INTO daily_stats (user_id, date, watch_minutes, items_completed) VALUES (?, date("now", "start of day"), ?, ?) ON CONFLICT(user_id, date) DO UPDATE SET watch_minutes = excluded.watch_minutes, items_completed = excluded.items_completed', (user_id, playtime, items_completed))
    con.commit()

def get_weekly_stats(user_id):
    cur = con.cursor()
    current_date = datetime.now(timezone.utc).isoformat()
    weekly_points = cur.execute('SELECT SUM(points) FROM points_ledger WHERE strftime("%Y-%W", created_at) = strftime("%Y-%W", ?) AND user_id = ?', (current_date, user_id)).fetchone()[0] or 0
    daily_stats = cur.execute('SELECT SUM(watch_minutes) as watch_minutes, SUM(items_completed) as items_completed FROM daily_stats WHERE strftime("%Y-%W", date) = strftime("%Y-%W", ?) AND user_id = ?', (current_date, user_id)).fetchone() or 0

    weekly_stats = {
        'points' : weekly_points,
        'watch_minutes' : daily_stats['watch_minutes'],
        'items_completed' : daily_stats['items_completed']
    }

    return weekly_stats

def get_streak(user_id):
    cur = con.cursor()
    daily_stats = cur.execute('SELECT items_completed, date FROM daily_stats WHERE user_id = ? ORDER BY date DESC', (user_id,)).fetchall()
    streak = 0
    for item in daily_stats:
        if item['items_completed'] > 0:
            streak += 1
        elif item['date'] >= datetime.now().date().isoformat():
            continue
        else:
            break
    return streak

def create_json():
    cur = con.cursor()
    users = get_users()
    users_dict = {
        'last_updated': datetime.now(tz=timezone.utc).isoformat(),
        'users': {}
    }
    for user in users:
        if get_points(user['id']) == 0:
            continue
        user_id = user['id']
        daily_stats = cur.execute('SELECT * FROM daily_stats WHERE user_id = ? AND date(date) >= date("now", "start of day")', (user_id,)).fetchone()
        points_ledger = cur.execute('SELECT SUM(reason = "Watched a movie") as movies_completed, SUM(reason = "Watched an episode") as episodes_completed FROM points_ledger WHERE user_id = ?', (user_id,)).fetchone()
        monthly_totals = cur.execute('SELECT * FROM monthly_totals WHERE user_id = ?', (user_id,)).fetchall()
        runtime_ticks_response = cur.execute('SELECT SUM(items.runtime_ticks) as total_runtime_ticks FROM plays JOIN items ON plays.item_id = items.id WHERE user_id = ?', (user_id,)).fetchone()
        total_watchtime = runtime_ticks_response['total_runtime_ticks'] / 10000000 / 60
        last_activity = cur.execute('SELECT items.name as item_name, plays.date_played as date FROM plays JOIN items ON plays.item_id = items.id WHERE user_id = ? ORDER BY date_played DESC', (user_id,)).fetchone()
        weekly_stats = get_weekly_stats(user_id)
        streak = get_streak(user_id)

        users_dict['users'][user_id] = {
            'name': user['Name'],
            'last_activity': last_activity['date'],
            'total_watchtime': total_watchtime,
            'points' : get_points(user_id),
            'streak': streak,
            'last_watched' : last_activity['item_name'],
            'daily_stats': {
                'date' : daily_stats['date'],
                'watch_minutes' : daily_stats['watch_minutes'],
                'items_completed' : daily_stats['items_completed'],
            },
            'weekly_stats' : weekly_stats,
            'points_ledger': {
                'movies_watched' : points_ledger['movies_completed'],
                'episodes_completed' : points_ledger['episodes_completed'],
            },
            'monthly_totals': {}
        }

        for total in monthly_totals:
            year = total['year']
            month = total['month']

            if year not in users_dict['users'][user_id]['monthly_totals']:
                users_dict['users'][user_id]['monthly_totals'][year] = {}

            users_dict['users'][user_id]['monthly_totals'][year][month] = {
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