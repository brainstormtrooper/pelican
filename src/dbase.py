import sqlite3
import uuid
import os

"""
- Check that tables exist
- Check that model/columns are correct and up to date
- handles queries
"""

class db:

    schema_version = 1

    def __init__(self, cachepath=None):
        defpath = os.path.join(os.path.expanduser("~"), ".cache/pelican")
        mycachepath = cachepath if None != cachepath else defpath
        db = f"{mycachepath}/pelican.db"
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
            cur.execute("CREATE TABLE photos(id, filename, filepath, hash, takendate, device, lat, lon, alt, dir, name, town, state, country, notes, flag, lastopen, opencount)")
            cur.execute("CREATE INDEX name_index ON photos(filename)")
            cur.execute("CREATE INDEX path_index ON photos(filepath)")
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

    def getphotosbyhash(self, hash):
        res = []
        cur = self.con.cursor()
        stmt = f"SELECT id FROM photos WHERE hash = ?;"
        for row in cur.execute(stmt, (name,)):
            res.append(row)
        cur.close()

        return res


    def isphoto(self, ppath, pname):
        res = False
        cur = self.con.cursor()
        stmt = f"SELECT id FROM photos WHERE filename = ? AND filepath = ? LIMIT 1;"
        row = cur.execute(stmt, (pname, ppath)).fetchone()
        if row:
            res = True
        cur.close()

        return res
    
    def insertphoto(self, values):
        cur = self.con.cursor()
        phid = str(uuid.uuid4())
        # fields = ['filename', 'filepath', 'hash', 'takendate', 'device', 'lat', 'lon', 'alt', 'dir', 'town', 'country']
        # vals = [f"'{v}'" for v in values]
        vals = (phid, *values)
        stmt = """
        INSERT INTO photos (id, filename, filepath, hash, takendate, device, lat, lon, alt, dir)
        VALUES (?,?,?,?,?,?,?,?,?,?)
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
        stmt = f"SELECT id, filename, filepath, takendate, name, town FROM photos WHERE takendate {dircond} ? ORDER BY takendate {sortd} LIMIT ?"
        rows = []
        for row in cur.execute(stmt, (startdate, limit)):
            rows.append(row)
        print(rows)
        cur.close()

        return rows

    def getPicsWithLocs(self):
        cur = self.con.cursor()
        stmt = "SELECT filename, filepath, lat, lon FROM photos WHERE lat NOT NULL"
        rows = []
        for row in cur.execute(stmt):
            rows.append(row)
        print(rows)
        cur.close()

        return rows

    def deletePic(self, photo_id):
        cur = self.con.cursor()
        stmt1 = "DELETE FROM photos WHERE id = ?;"
        stmt2 = "DELETE FROM phrases WHERE photo_id = ?;"
        stmt3 = "DELETE FROM members WHERE photo_id = ?;"
        cur.execute(stmt1, (photo_id,))
        r1 = cur.rowcount
        cur.execute(stmt2, (photo_id,))
        r2 = cur.rowcount
        cur.execute(stmt3, (photo_id,))
        r3 = cur.rowcount
        self.con.commit()
        cur.close()

        return (r1, r2, r3)

    def getPicsInBox(self, nw, ne, sw, se):
        cur = self.con.cursor()
        lat_l = ne[0]
        lat_r = sw[0]
        lon_t = ne[1]
        lon_b = sw[1]
        stmt = f"""
        SELECT * FROM photos p
        WHERE (
        {lon_t} <= {lon_b} AND ({lon_t} <= p.lon AND p.lon <= {lon_b}) OR
        {lon_t} >  {lon_b} AND ({lon_t} <= p.lon OR  p.lon <= {lon_b})
        ) AND (
        {lat_l} >= {lat_r} AND ({lat_l} >= p.lat AND p.lat >= {lat_r}) OR
        {lat_l} <  {lat_r} AND ({lat_l} >= p.lat OR  p.lat >= {lat_r})
        );
        """
        rows = []
        for row in cur.execute(stmt):
            rows.append(row)
        print(rows)
        cur.close()

        return rows

