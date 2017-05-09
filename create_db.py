import sqlite3
import sys

dbname = 'database.db'

conn = sqlite3.connect(dbname)

c = conn.cursor()

try:
    c.execute("DROP TABLE IF EXISTS users")    
    create_usertable = '''create table users (id integer primary key, useruuid varchar(5), lolv int)'''
    c.execute(create_usertable)
except:
    print(sys.exc_info())
    print("create_usertable\n")

try:
    c.execute("DROP TABLE IF EXISTS boards")    
    create_boardtable = '''create table boards(id integer primary key, boardname varchar(15))'''
    c.execute(create_boardtable)
except:
    print(sys.exc_info())
    print("create_boardtable\n")

try :
    c.execute("DROP TABLE IF EXISTS threads")    
    create_threadtable = '''create table threads (id integer primary key, imagename varchar(20) , thumbnailname varchar(20) , threadname varchar(20), userid int, boardname varchar(15), love int, time varchar(32), requiredlolv int, lastupdate int)'''
    c.execute(create_threadtable)
except:
    print(sys.exc_info())
    print("create_threadtable\n")

try:
    c.execute("DROP TABLE IF EXISTS ress")    
    create_responsetable = '''create table ress (id integer primary key, threadid int, userid int, username varchar(5), number int, time varchar(32), text varchar(1000))''' 
    c.execute(create_responsetable)
except:
    print(sys.exc_info())
    print("create_responsetable\n")

try:
    c.execute("DROP TABLE IF EXISTS abuses")    
    create_responsetable = '''create table abuses (id integer primary key, threadid int, useruuid int)''' 
    c.execute(create_responsetable)
except:
    print(sys.exc_info())
    print("create_responsetable\n")


conn.commit()

conn.close()
