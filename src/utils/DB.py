import sqlite3


class Database:
    def __init__(self, db_name="config/database.sqlite"):
        self.db_name = db_name

    def execute(self, query, params=()):
        con = sqlite3.connect(self.db_name)
        cur = con.cursor()

        try:
            cur.execute(query, params)

            if query.strip().lower().startswith("select"):
                result = cur.fetchall()
            else:
                con.commit()
                result = None

        except sqlite3.Error as e:
            print(f"Database error: {e}")
            result = None

        finally:
            con.close()

        return result
