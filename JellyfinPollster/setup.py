import sqlite3

DB_PATH = 'stats.sqlite'

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,           -- Jellyfin user ID
    name TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    last_processed_played_date TEXT
);

CREATE TABLE IF NOT EXISTS items (
    id TEXT PRIMARY KEY,           -- Jellyfin item ID
    name TEXT,
    type TEXT,                     -- Movie or Episode
    genre TEXT,
    runtime_ticks INTEGER,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS plays (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    item_id TEXT NOT NULL,
    date_played TEXT NOT NULL,
    completion_ratio REAL,
    direct_play INTEGER DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(item_id) REFERENCES items(id),
    UNIQUE(user_id, item_id, date_played)
);

CREATE TABLE IF NOT EXISTS points_ledger (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    play_id INTEGER,
    reason TEXT NOT NULL,
    points INTEGER NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(play_id) REFERENCES plays(id)
);

CREATE TABLE IF NOT EXISTS daily_stats (
    user_id TEXT NOT NULL,
    date TEXT NOT NULL,
    watch_minutes INTEGER DEFAULT 0,
    items_completed INTEGER DEFAULT 0,
    PRIMARY KEY(user_id, date)
);

CREATE TABLE IF NOT EXISTS monthly_totals (
    user_id TEXT NOT NULL,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    points INTEGER DEFAULT 0,
    PRIMARY KEY(user_id, year, month)
);
"""

def main():
    con = sqlite3.connect(DB_PATH)
    con.executescript(SCHEMA)
    con.commit()
    con.close()
    print(f'Database initialised at {DB_PATH}')

if __name__ == '__main__':
    main()