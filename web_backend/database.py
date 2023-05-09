import psycopg2 as db
import hashlib
from config import *

class Database:
    def __init__(self):
        self.con = db.connect(host=host, port=port, user=user, password=password, database=dbname)
        self.cur = self.con.cursor()

    def close(self):
        self.cur.close()
        self.con.close()

    """
    for user table
    """
    def list_users(self):
        self.cur.execute("SELECT uid, fullname, email, affiliation, type_name FROM users as u INNER JOIN user_type as ut on u.user_type = ut.utid")
        result = self.cur.fetchall()
        self.close()
        return result

    def get_user(self, uid):
        self.cur.execute("SELECT uid, fullname, username, email, affiliation, type_name FROM users as u INNER JOIN user_type as ut on u.user_type = ut.utid WHERE uid = %i", (uid, ) )
        results = self.cur.fetchall()
        self.close()
        if results and len(results) > 0:
            return results[0]
        return None

    def check_duplicate_user(self, username):
        if not username:
             return None
        # select psword from DB
        self.cur.execute("SELECT uid, username, psword FROM users WHERE username = %s", (username,))
        result = self.cur.fetchall()
        self.close()
        if result and len(result) > 0:
             return result[0]
        return None
    
    def check_login(self, username, psword):
        if not username or not psword:
             return None
        # select psword from DB
        self.cur.execute("SELECT uid, fullname, username, psword FROM users WHERE username = %s", (username,))
        result = self.cur.fetchall()
        self.close()
        pw_hash = hashlib.sha256(psword.encode())
        pw_hash = pw_hash.hexdigest()
        if result and len(result) > 0 and pw_hash == result[0][3]:
             return result[0]
        return None

    def insert_user(self, fullname, user_type, username, psword, email, affiliation):
        self.cur.execute("INSERT INTO users(fullname, user_type, username, psword, email, affiliation) VALUES (%s, %s, %s, %s, %s, %s)", (fullname, user_type, username, psword, email, affiliation))
        self.con.commit()
        self.close()
        return self.cur.rowcount

    def update_user(self, uid, fullname, user_type, psword, email, affiliation):
        if psword:
            self.cur.execute("UPDATE users SET fullname = %s, user_type = %s, psword = %s, email = %s, affiliation = %s WHERE uid = %s", (fullname, user_type, psword, email, affiliation, uid))
        else:
            self.cur.execute("UPDATE users SET fullname = %s, user_type = %s, email = %s, affiliation = %s WHERE uid = %s", (fullname, user_type, email, affiliation, uid))
        self.con.commit()
        self.close()
        num_row = self.cur.rowcount
        return num_row

    def delete_user(self, uid):
        num_row = self.cur.execute("DELETE FROM userss WHERE uid = %s", (uid,))
        self.con.commit()
        self.close()
        return num_row
    
    """
    for song table
    """
    def list_songs(self, offset_start, page_size):
        self.cur.execute("SELECT s.*, c.composer_name, g.genre_name FROM song as s \
                         LEFT JOIN genre as g on s.genre = g.gid \
                         LEFT JOIN composer as c on s.composer = c.cid \
                         LIMIT %s OFFSET %s", (page_size, offset_start))
        result = self.cur.fetchall()
        self.close()
        return result
    
    def get_song(self, uid):
        self.cur.execute("SELECT s.* FROM song as s \
                         INNER JOIN composer as c on s.cid = c.cid \
                         WHERE sid = %i", (uid, ) )
        results = self.cur.fetchall()
        self.close()
        if results and len(results) > 0:
            return results[0]
        return None

    def insert_song(self, songname, composer, genre):
        self.cur.execute("INSERT INTO song(song_name, composer, genre) VALUES (%s, %s, %s)", (songname, composer, genre))
        self.con.commit()
        self.close()
        return self.cur.rowcount
    
    def update_song(self, sid, songname, composer, genre):
        self.cur.execute("UPDATE song SET song_name = %s, composer = %s, genre = %s WHERE sid = %s", (songname, composer, genre, sid))
        self.con.commit()
        self.close()
        num_row = self.cur.rowcount
        return num_row

    def delete_song(self, sid):
        num_row = self.cur.execute("DELETE FROM song WHERE sid = %s", (sid,))
        self.con.commit()
        self.close()
        return num_row
    
    """
    for composer table
    """
    def list_composers(self):
        self.cur.execute("SELECT * FROM composer")
        result = self.cur.fetchall()
        self.close()
        return result
    
    def get_composer(self, uid):
        self.cur.execute("SELECT c.* FROM composer as c \
                         WHERE cid = %i", (uid, ) )
        results = self.cur.fetchall()
        self.close()
        if results and len(results) > 0:
            return results[0]
        return None
    
    def insert_composer(self, composer, description):
        self.cur.execute("INSERT INTO composer(composer_name, description) VALUES (%s, %s)", (composer, description))
        self.con.commit()
        self.close()
        return self.cur.rowcount
    
    def update_composer(self, cid, composer, description):
        self.cur.execute("UPDATE composer SET composer_name = %s, description = %s WHERE cid = %s", (composer, description, cid))
        self.con.commit()
        self.close()
        num_row = self.cur.rowcount
        return num_row

    def delete_composer(self, cid):
        num_row = self.cur.execute("DELETE FROM composer WHERE cid = %s", (cid,))
        self.con.commit()
        self.close()
        return num_row
    
    """
    for genre table
    """
    def list_genres(self):
        self.cur.execute("SELECT * FROM genre")
        result = self.cur.fetchall()
        self.close()
        return result
    
    def get_genre(self, uid):
        self.cur.execute("SELECT g.* FROM genre as g \
                         WHERE gid = %i", (uid, ) )
        results = self.cur.fetchall()
        self.close()
        if results and len(results) > 0:
            return results[0]
        return None
    
    def insert_genre(self, genre, description):
        self.cur.execute("INSERT INTO genre(genre_name, description) VALUES (%s, %s)", (genre, description))
        self.con.commit()
        self.close()
        return self.cur.rowcount
    
    def update_genre(self, gid, genre, description):
        self.cur.execute("UPDATE genre SET genre_name = %s, description = %s WHERE gid = %s", (genre, description, gid))
        self.con.commit()
        self.close()
        num_row = self.cur.rowcount
        return num_row

    def delete_genre(self, gid):
        num_row = self.cur.execute("DELETE FROM genre WHERE gid = %s", (gid,))
        self.con.commit()
        self.close()
        return num_row
    
    """
    for user_type table
    """
    def list_user_types(self):
        self.cur.execute("SELECT * FROM users_type")
        result = self.cur.fetchall()
        self.close()
        return result
    
    def get_user_type(self, uid):
        self.cur.execute("SELECT u.* FROM users_type as u WHERE u.utid = %s", (str(uid), ) )
        results = self.cur.fetchall()
        self.close()
        if results and len(results) > 0:
            return results[0]
        return None
    
    def insert_user_type(self, user_type, description):
        self.cur.execute("INSERT INTO user_type(type_name, description) VALUES (%s, %s)", (user_type, description))
        self.con.commit()
        self.close()
        return self.cur.rowcount
    
    def update_user_type(self, utid, user_type, description):
        self.cur.execute("UPDATE user_type SET type_name = %s, description = %s WHERE utid = %s", (user_type, description, utid))
        self.con.commit()
        self.close()
        num_row = self.cur.rowcount
        return num_row

    def delete_user_type(self, utid):
        num_row = self.cur.execute("DELETE FROM users_type WHERE utid = %s", (utid,))
        self.con.commit()
        self.close()
        return num_row
    

    """
    for practice table
    """
    def list_practices(self):
        self.cur.execute("SELECT * FROM practice")
        result = self.cur.fetchall()
        self.close()
        return result
    
    def get_practice(self, uid):
        self.cur.execute("SELECT p.*, s.song_name, s.sid, u.uid, u.fullname FROM practice as p "
                         + " INNER JOIN song as s on p.sid = s.sid "
                         + " INNER JOIN user as u on p.uid = u.uid "
                         + " WHERE pid = %i", (uid, ) )
        results = self.cur.fetchall()
        self.close()
        if results and len(results) > 0:
            return results[0]
        return None

    def insert_practice(self, sid, uid, timestamp, midi_path):
        self.cur.execute("INSERT INTO practice(sid, uid, timestamp, midi_path) VALUES (%s, %s, %s, %s)", (sid, uid, timestamp, midi_path))
        self.con.commit()
        self.close()
        return self.cur.rowcount
    
    def update_practice(self, pid, sid, uid, timestamp, midi_path):
        self.cur.execute("UPDATE practice SET sid = %s, uid = %s, timestamp = %s, midi_path = %s WHERE pid = %s", (sid, uid, timestamp, midi_path, pid))
        self.con.commit()
        self.close()
        num_row = self.cur.rowcount
        return num_row

    def delete_practice(self, pid):
        num_row = self.cur.execute("DELETE FROM practice WHERE pid = %s", (pid,))
        self.con.commit()
        self.close()
        return num_row
    

    """
    for practice_result table
    """
    def list_practice_results(self):
        self.cur.execute("SELECT * FROM practice_result")
        result = self.cur.fetchall()
        self.close()
        return result
    
    def insert_practice_result(self, pid, start_time, end_time, preds):
        self.cur.execute("INSERT INTO practice_result(pid, start_time, end_time, preds) VALUES (%s, %s, %s, %s)", (pid, start_time, end_time, preds))
        self.con.commit()
        self.close()
        return self.cur.rowcount
    
    def update_practice_result(self, prid, pid, start_time, end_time, preds):
        self.cur.execute("UPDATE practice_result SET pid = %s, start = %s, end = %s, preds = %s WHERE prid = %s", (pid, start_time, end_time, preds, prid))
        self.con.commit()
        self.close()
        num_row = self.cur.rowcount
        return num_row

    def delete_practice_result(self, prid):
        num_row = self.cur.execute("DELETE FROM practice_result WHERE pid = %s", (prid,))
        self.con.commit()
        self.close()
        return num_row
    
    """
    for grading table
    """
    def list_gradings(self):
        self.cur.execute("SELECT * FROM grading")
        result = self.cur.fetchall()
        self.close()
        return result
    
    def get_grading(self, uid):
        self.cur.execute("SELECT g.*, p.midi_path, s.sid, s.song_name, u.uid, u.fulname FROM grading as g \
                         INNER JOIN practice as p on g.pid = p.pid \
                         INNER JOIN song as s on p.sid = s.sid \
                         INNER JOIN user as u on p.uid = u.uid \
                         WHERE gid = %i", (uid, ) )
        results = self.cur.fetchall()
        self.close()
        if results and len(results) > 0:
            return results[0]
        return None
    
    def insert_grading(self, pid, start_time, end_time, labels, comments):
        self.cur.execute("INSERT INTO grading(pid, start_time, end_time, labels, comments) VALUES (%s, %s, %s, %s, %s)", (pid, start_time, end_time, labels, comments))
        self.con.commit()
        self.close()
        return self.cur.rowcount
    
    def update_grading(self, gid, pid, start_time, end_time, labels, comments):
        self.cur.execute("UPDATE grading SET pid = %s, start = %s, end = %s, labels = %s, comments = %s \
                        WHERE gid = %s", (pid, start_time, end_time, labels, comments, gid))
        self.con.commit()
        self.close()
        num_row = self.cur.rowcount
        return num_row

    def delete_grading(self, gid):
        num_row = self.cur.execute("DELETE FROM grading WHERE gid = %s", (gid,))
        self.con.commit()
        self.close()
        return num_row