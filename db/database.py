import sqlite3
from datetime import datetime, date, timedelta
from models.training import Training

conn = sqlite3.connect("trainings.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS trainings (
    id INTEGER PRIMARY KEY,
    category TEXT,
    description TEXT,
    date TEXT,
    start_time TEXT,
    end_time TEXT
)''')
conn.commit()

def add_training(t: Training):
    cursor.execute("INSERT INTO trainings (category, description, date, start_time, end_time) VALUES (?, ?, ?, ?, ?)",
                   (t.category, t.description, t.date.isoformat(), t.start_time.strftime("%H:%M"), t.end_time.strftime("%H:%M")))
    conn.commit()

def get_trainings_for_week(reference_date):
    start = reference_date - timedelta(days=reference_date.weekday())
    end = start + timedelta(days=6)
    cursor.execute("SELECT * FROM trainings WHERE date BETWEEN ? AND ?", (start.isoformat(), end.isoformat()))
    rows = cursor.fetchall()
    result = []
    for row in rows:
        result.append(Training(id=row[0], category=row[1], description=row[2],
                               date=date.fromisoformat(row[3]),
                               start_time=datetime.strptime(row[4], "%H:%M").time(),
                               end_time=datetime.strptime(row[5], "%H:%M").time()))
    return result

def get_trainings_for_month(year, month, category):
    start = date(year, month, 1)
    end = (start.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
    if category.lower() == "toutes":
        cursor.execute("SELECT * FROM trainings WHERE date BETWEEN ? AND ? ORDER BY date, start_time", (start.isoformat(), end.isoformat()))
    else:
        cursor.execute("SELECT * FROM trainings WHERE category=? AND date BETWEEN ? AND ? ORDER BY date, start_time", (category, start.isoformat(), end.isoformat()))
    rows = cursor.fetchall()
    return [Training(id=row[0], category=row[1], description=row[2],
                     date=date.fromisoformat(row[3]),
                     start_time=datetime.strptime(row[4], "%H:%M").time(),
                     end_time=datetime.strptime(row[5], "%H:%M").time()) for row in rows]

def delete_training(training_id):
    cursor.execute("DELETE FROM trainings WHERE id = ?", (training_id,))
    conn.commit()

def update_training(t: Training):
    cursor.execute("UPDATE trainings SET category=?, description=?, date=?, start_time=?, end_time=? WHERE id = ?",
                   (t.category, t.description, t.date.isoformat(), t.start_time.strftime("%H:%M"), t.end_time.strftime("%H:%M"), t.id))
    conn.commit()
