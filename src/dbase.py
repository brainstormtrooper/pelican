import sqlite3
import uuid

"""
- Check that tables exist
- Check that model/columns are correct and up to date
- handles queries
"""

class db:

    schema_version = 1

    def __init__(self, cachepath):
        db = f"{cachepath}/pelican.db"
        self.con = sqlite3.connect(db)
        self.con.set_trace_callback(print)
        

    def isInit(self):
        cur = self.con.cursor()
        rows = cur.execute("SELECT name FROM sqlite_master WHERE name='version'")
        res = rows.fetchone() is not None
        cur.close()

        return res

    def initdb(self):
        cur = self.con.cursor()
        try:
            cur.execute("CREATE TABLE photos(id, filename, filepath, hash, takendate, device, lat, lon, alt, dir, name, town, state, country, notes, flag, lastopen, opencount, thumbnail)")
            cur.execute("CREATE INDEX name_index ON photos(filename)")
            cur.execute("CREATE INDEX id_index ON photos(id)")
            cur.execute("CREATE INDEX date_index ON photos(takendate)")
            cur.execute("CREATE TABLE collections(id, name, notes, auto)")
            cur.execute("CREATE TABLE members(photo_id, collection_id)")
            cur.execute("CREATE TABLE phrases(photo_id, phrase)")
            cur.execute("CREATE INDEX phrase_index ON phrases(phrase)")
            cur.execute("CREATE TABLE version(schema_version)")
            cur.execute(f"INSERT INTO version VALUES ({self.schema_version})")
            self.con.commit()
        except Exception as e:
            print(e)

        cur.close()

    def isphotoname(self, name):
        res = False
        cur = self.con.cursor()
        stmt = f"SELECT id FROM photos WHERE filename = ? LIMIT 1;"
        row = cur.execute(stmt, (name,)).fetchone()
        if row:
            res = True

        return res
    
    def insertphoto(self, values):
        cur = self.con.cursor()
        phid = str(uuid.uuid4())
        # fields = ['filename', 'filepath', 'hash', 'takendate', 'device', 'lat', 'lon', 'alt', 'dir', 'town', 'country']
        # vals = [f"'{v}'" for v in values]
        vals = (phid, *values)
        stmt = """
        INSERT INTO photos (id, filename, filepath, hash, takendate, device, lat, lon, alt, dir, thumbnail)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)
        """
        cur.execute(stmt, vals)
        self.con.commit()
        cur.close()

        return phid

    def addlocationtophoto(self, id, name, town, state, country):
        res = 0
        cur = self.con.cursor()
        stmt = "UPDATE photos SET name = ?, town = ?, state = ?, country = ? WHERE id = ?"
        cur.execute(stmt, (name, town, state, country, id))
        res = cur.rowcount
        self.con.commit()
        cur.close()

        return res

    def getphrase(self, photo_id):
        res = ''
        cur = self.con.cursor()
        stmt = "SELECT phrase FROM phrases WHERE photo_id = ?"
        row = cur.execute(stmt, (photo_id,)).fetchone()
        print(row)
        if row:
            res = row[0]
        cur.close()

        return res

    def updatephrase(self, photo_id, phrase):
        res = 0
        cur = self.con.cursor()
        stmt = "REPLACE INTO phrases(photo_id, phrase) VALUES (?, ?)"
        cur.execute(stmt, (photo_id, phrase))
        res = cur.rowcount
        self.con.commit()
        cur.close()
        
        return res

    def getpicspage(self, direction, startdate, limit):
        cur = self.con.cursor()
        dircond = '<' if direction == 'down' else '>'
        sortd = 'DESC' if direction == 'down' else 'ASC'
        stmt = f"SELECT id, filename, filepath, takendate, thumbnail, name, town FROM photos WHERE takendate {dircond} ? ORDER BY takendate {sortd} LIMIT ?"
        rows = []
        for row in cur.execute(stmt, (startdate, limit)):
            rows.append(row)
        print(rows)
        cur.close()

        return rows
