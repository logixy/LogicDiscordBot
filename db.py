import sqlite3

sb = sqlite3.connect("users.db")
cur = sb.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name VARCHAR(255), money REAL NOT NULL);")
while True:
    user = input("User: ")
    money = input("Money: ")
    #cur.execute("INSERT INTO users (name, money) VALUES (?, ?)", [user, money])
    sb.execute("UPDATE users SET money=money+? WHERE name=?", [money, user])
    sb.commit()
    data = sb.execute("SELECT money FROM users WHERE name=?", [user])
    money = data.fetchone()
    print(str(money))