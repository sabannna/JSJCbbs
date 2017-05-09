import sqlite3
import sys
from datetime import datetime
import resize
import logging

dbname = 'database.db'

class DBManager:
    def __init__(self):
        self.conn = sqlite3.connect(dbname)
        self.conn.row_factory = sqlite3.Row

    def __dest__(self):
        self.conn.close()

db = DBManager()

class UserManager():
    def __init__(self):
       c = db.conn.cursor()
       c.execute('''select * from users where useruuid == 'root' ''') 
       selected = c.fetchall()
       if len(selected) == 0:
           UserManager.set_user('root')
  
    @classmethod
    def set_user(cls, useruuid):
        c = db.conn.cursor()
        user = cls.get_user(useruuid)
        if len(user) == 0:
            c.execute('''insert into users (useruuid, lolv) values (?,?) ''', (useruuid, 0))
            db.conn.commit()
        else:
            pass

    @classmethod
    def set_lolv(cls, useruuid, lolv):
        c = db.conn.cursor()
        try:
            update = '''update users set lolv = ? where useruuid = ?'''
            c.execute(update, (lolv, useruuid))
            db.conn.commit()
        except:
            print('''error occuring at set_lolv of UserManager''')

    @classmethod
    def get_user(cls, useruuid):
        try: 
            c = db.conn.cursor()
            c.execute('''select * from users where useruuid = ?''', (useruuid,) )
            ret = c.fetchall()
            return ret

        except:
            print(''' error occuring at get_user of UserManager''')
            return None

    @classmethod
    def get_all_user(cls):
        c = db.conn.cursor()
        c.execute('''select * from users''')
        ret = c.fetchall()
        return ret

class ResponseManager:

    @classmethod
    def get_thread_response(cls, threadid, order = None):
        if order == "reverse":
            c = db.conn.cursor()
            c.execute('''select * from ress where threadid = ? order by id DESC''', (threadid, ))
            selected = c.fetchall()
            return selected
        else:
            c = db.conn.cursor()
            c.execute('''select * from ress where threadid = ? ''', (threadid, ))
            selected = c.fetchall()
            return selected

    @classmethod
    def set_response(cls, threadid, message, userid, username):
        c = db.conn.cursor()
        c.execute('''select * from ress where threadid''')
        now = c.fetchall()
        time =  datetime.now().strftime('%Y/%m/%d %H:%M:%S'),
        #import pdb; pdb.set_trace()
        c.execute('''insert into ress (threadid, userid, username, number, time, text) values (?,?,?,?,?,?)'''
        , (threadid, userid, username, len(now) + 1, time[0], message))
        #板の最終更新countの更新
        c.execute('''update threads set lastupdate = ((select max(lastupdate) from threads)+1) where id == ?''', (threadid,))
        db.conn.commit()

        #c.execute('''select * from users where useruuid == ?''', (userid,))
        #userinfo = c.fetchall()
        #if len(userinfo) != 0 :
        #    import pdb; pdb.set_trace()
        #    from chatdemo import PersonalSocketHandler
        #    PersonalSocketHandler.send_updates(userinfo[0]["username"], userinfo[0]["lolv"])

    @classmethod
    def get_response(cls, responseid):
        c = db.conn.cursor()
        c.execute('''select * from ress where id = ?''', (responseid,))
        ret = c.fetchall()
        return None

    @classmethod
    def get_thread_responsenum(cls, threadid):
        try: 
            c = db.conn.cursor()
            c.execute('''select count(*) from ress where threadid = ? ''', (threadid,))
            ret = c.fetchone()
            return ret[0]
        except:
            print("error occur at get_responsenum")

class ThreadManager():
    def __init__(self):
        c = db.conn.cursor()
        c.execute('''select id from threads where threadname = 'Rounge' ''')
        roungeid = c.fetchone()   
        #import pdb; pdb.set_trace()
        if roungeid is None:
            ThreadManager.set_thread("Rounge", None, "Rounge", "root", 0)

    @classmethod
    def set_love(cls, threadid, love):
        c = db.conn.cursor()
        update = '''update threads set love = ? where id = ?'''
        selected = (love, threadid)
        c.execute(update, selected)
        db.conn.commit()

    @classmethod
    def set_requiredlolv(cls, requiredlolv):
        c = db.conn.cursor()
        update = '''update threads set requiredlolv = ? where id = (select max(id) from threads)'''
        selected = (requiredlolv,)
        c.execute(update, selected)
        db.conn.commit()

    @classmethod
    def set_newimagename(cls, threadid, imagenames):
        c = db.conn.cursor()
        update = '''update threads set imagename = ?, thumbnailname = ? where id = ?'''
        selected = (imagenames[0], imagenames[1], threadid)
        c.execute(update, selected)
        db.conn.commit()

    @classmethod
    def get_thread(cls, threadid):
        try:
            c = db.conn.cursor()
            c.execute('''select * from threads where id = ?''', (threadid,))
            selected = c.fetchall()
            return selected

        except:
            print("get thread error occur \n")
            return None

    @classmethod
    def get_board_thread(cls, boardname, order=None):
        try:
            if order is None:
                c = db.conn.cursor()
                c.execute('''select * from threads where boardname = ?''', (boardname,))
                selected = c.fetchall()
                #import pdb; pdb.set_trace()
                return selected
            else :
                c = db.conn.cursor()
                c.execute('''select * from threads where boardname = ? order by lastupdate''', (boardname,))
                selected = c.fetchall()
                #import pdb; pdb.set_trace()
                return selected

        except:
            print("get board thread error occur \n")
            return None

    @classmethod
    def get_all_thread(cls):
        try:
            c = db.conn.cursor()
            c.execute('''select * from threads''')
            selected = c.fetchall()
            return selected
        except:
            print("get all thread error occur \n")
            return None


    @classmethod
    def set_image(cls, imagedata):
        c = db.conn.cursor()
        c.execute('''select MAX(id) from threads''')
        maxid = c.fetchall()

        #define image name
        #import pdb;pdb.set_trace()
        threadid = str(maxid[0][0] + 1)
        originalname = ("original" + threadid + ".jpg")
        secondname = ("thumbnaile" + threadid + ".jpg")

        #make image thumbnail and save images
        resize.cropimage(imagedata, originalname, secondname)
        return (originalname, secondname)

    @classmethod
    def set_thread(cls, boardname, imagenames, threadname, username, requiredlolv):
        #import pdb; pdb.set_trace()
        if imagenames is None:
            originalname = "NoImage.jpeg"
            thumbnailname = "NoImage.jpeg"
        else:
            originalname = imagenames[0]
            thumbnailname = imagenames[1]

        c = db.conn.cursor()
        c.execute('''select * from users where useruuid == ?''', (username,))
        userinfo = c.fetchall()
        if userinfo is None or len(userinfo) == 0 :
            print("user is not enrolled")
            return None

        time =  datetime.now().strftime('%Y/%m/%d %H:%M:%S')
        add_command = '''insert into threads (imagename, thumbnailname, threadname, userid, boardname, love, time, requiredlolv, lastupdate) values (?,?,?,?,?,?,?,?,?)'''
        add_parameter = (originalname, thumbnailname, threadname, userinfo[0]["id"], boardname, 0, time, requiredlolv, 0)
        c.execute(add_command, add_parameter)
        db.conn.commit()
            
        c.execute("select * from threads where threadname = ?", (threadname,))
        selected = c.fetchall()
        #import pdb; pdb.set_trace()
        return selected


class BoardManager():

    def __init__(self):
        c = db.conn.cursor()
        c.execute('''select * from boards where boardname == 'Rounge' ''')
        selected = c.fetchall()
        if len(selected) == 0:
            BoardManager.add_board('Rounge')
            print("add_board")
        
        c.execute('''select * from boards where boardname == 'ImageBoard' ''')
        selected = c.fetchall()
        if len(selected) == 0:
            BoardManager.add_board('ImageBoard')
            print("add_board")

        c.execute('''select * from boards where boardname == 'YoutubeBoard' ''')
        selected = c.fetchall()
        if len(selected) == 0:
            BoardManager.add_board('YoutubeBoard')
            print("add_youtube_board")

        c.execute('''select * from boards where boardname == 'TextBoard' ''')
        selected = c.fetchall()
        if len(selected) == 0:
            BoardManager.add_board('TextBoard')
            print("add_text_board")


        c.execute('''select * from boards''')
        selected = c.fetchall()
        print("all boards")
        for r in selected:
            print(r["boardname"])
        print("finish all boards")

    @classmethod
    def add_board(cls, boardname):
        c = db.conn.cursor()
        c.execute("insert into boards (boardname) values(?)", (boardname,))
        db.conn.commit()

    @classmethod
    def get_board(cls, boardname):
        c = db.conn.cursor()
        c.execute('''select * from boards where boardname = ? ''', (boardname,))
        selected = c.fetchall()
        return selected

    @classmethod
    def get_all_board(cls):
        c = db.conn.cursor()
        c.execute('''select * from boards''')
        selected = c.fetchall()
        return selected

class AbuseManager:

    @classmethod
    def set_abuse(cls, threadid, useruuid):
        c = db.conn.cursor()
        c.execute('''insert into abuses (threadid, useruuid) values (?, ?) if exists (select * from threads where id = threadid''', (threadid,useruuid)) 
        db.conn.commit()

