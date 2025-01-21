import sqlite3

con = sqlite3.connect("database.sqlite")
cur = con.cursor()

cur.execute(
    """
            CREATE TABLE IF NOT EXISTS user(
                user_id INT PRIMARY KEY, 
                role_id INT DEFAULT NULL
            )"""
)

con.commit()
con.close()
