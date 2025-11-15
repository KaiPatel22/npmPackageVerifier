import sqlite3

connect = sqlite3.connect("database/legitimate.db")
cursor = connect.cursor()

def setupDatabase():
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS legitimate(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                packageName TEXT UNIQUE NOT NULL,
                weeklyDownloads INTEGER NOT NULL,
                monthlyDownloads INTEGER NOT NULL,
                lastUpdate TIMESTAMP NOT NULL)
                ''')
    connect.commit()
    connect.close()
    print("Database setup complete.")

def addPackageToDatabase(packageName : str, weeklyDownloads : int, monthlyDownloads : int, lastUpdate : str):
    connect = sqlite3.connect("database/legitimate.db")
    cursor = connect.cursor()

    try:
        cursor.execute('INSERT OR REPLACE INTO legitimate (packageName, weeklyDownloads, monthlyDownloads, lastUpdate) VALUES (?, ?, ?, ?) ', (packageName, weeklyDownloads, monthlyDownloads, lastUpdate))
        connect.commit()
        print(f"Package {packageName} added successfully.")
    except sqlite3.IntegrityError as e:
        cursor.execute('UPDATE legitimate SET weeklyDownloads = ?, monthlyDownloads = ?, lastUpdate = ? WHERE packageName = ?', (weeklyDownloads, monthlyDownloads, lastUpdate, packageName))
        connect.commit()
        print(f"Updated {packageName} in database")
    finally:
        connect.commit()
        connect.close()

def getPackageInfo(packageName : str):
    connect = sqlite3.connect("database/legitimate.db")
    cursor = connect.cursor()

    cursor.execute('SELECT * FROM legitimate WHERE packageName = ? ', (packageName,))
    result = cursor.fetchone()
    connect.close()
    return result