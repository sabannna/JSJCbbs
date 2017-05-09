import logging
import tornado.escape
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket
import os
import os.path
import uuid

from tornado.options import define, options
from datetime import datetime

from PIL import Image
import io

import random
import manager

import checklist 

import youtubehandler
import texthandler
import adrandom
import re


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", MainHandler),
            (r"/(?P<image>image)?", MainHandler),
            (r"/chatsocket", ChatSocketHandler),
            (r"/chatsocketfile", FileSocketHandler),
            (r"/chatsocketnum", WaiterSocketHandler),
            (r"/chatsocketlove", LoveSocketHandler),
            (r"/chatsocketthread", ThreadSocketHandler),
            (r"/chatsocketpersonal", PersonalSocketHandler),
            (r"/youtube", youtubehandler.YoutubeHandler),
            (r"/youtubesocket", youtubehandler.YoutubeSocketHandler),
            (r"/text", texthandler.TextHandler),
            (r"/text/(?P<text>.+)$", texthandler.TextHandler),
            (r"/textsocket", texthandler.TextSocketHandler),
        ]

        settings = dict(
            ui_modules = adrandom,
            cookie_secret="iiijjljjlkjljligoh",
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=True,
        )
        
        super(Application, self).__init__(handlers, **settings)

class MainHandler(tornado.web.RequestHandler):
    def get(self, image = None):
        if not self.get_secure_cookie("a"):
            self.set_secure_cookie(name="a", value=(str(uuid.uuid4())))
            logging.info("set secure coockie")
            lolv = 0
        else:
            useruuid = (self.get_secure_cookie("a").decode("utf-8"))[0:5]
            userinfo = manager.UserManager.get_user(useruuid)
            if not userinfo:
                manager.UserManager.set_user(useruuid)
                lolv = 0
            else:
                lolv = userinfo[0]["lolv"]

        roungeboard = manager.BoardManager.get_board("Rounge")
        imageboard = manager.BoardManager.get_board("ImageBoard")
        roungethread = manager.ThreadManager.get_board_thread(roungeboard[0]["boardname"])
        if image:
            imagethreads = manager.ThreadManager.get_board_thread(imageboard[0]["boardname"])
            boardname = "image"
        else:
            imagethreads = manager.ThreadManager.get_all_thread()
            boardname = "Top"
        #import pdb; pdb.set_trace()
        self.render("index.html", boardname = boardname, roungeboard = roungeboard[0], roungethread = roungethread[0], imagethreads = imagethreads, manager = manager, lolv=lolv)

class ChatSocketHandler(tornado.websocket.WebSocketHandler):
    waiters = set()
    cache_size = 200

    def get_compression_options(self):
        # Non-None enables compression with default options.
        return {}

    def open(self):
        ChatSocketHandler.waiters.add(self)

    def on_close(self):
        ChatSocketHandler.waiters.remove(self)

    @classmethod
    def send_updates(cls, chat):
        logging.info("sending message to %d waiters", len(cls.waiters))
        for waiter in cls.waiters:
            try:
                waiter.write_message(chat)
            except:
                logging.error("Error sending message", exc_info=True)

    def on_message(self, message):
        useruuid = (self.get_secure_cookie("a").decode("utf-8"))[0:5]
        manager.UserManager.set_user(useruuid)

        parsed = tornado.escape.json_decode(message)

        print(parsed)
        if parsed["imagefile"] == "true":
            #import pdb;pdb.set_trace()
            FileSocketHandler.requiredlolv = parsed["requiredlolv"]
            return

        if "body" in parsed:
            if parsed["body"] == "":
                logging.info("empty messge received")
                return
            else:
                a = re.match("http(s)?://", parsed["body"])
                d = re.match("delete=(?P<deleteid>[0-9]+)", parsed["body"])
                if a:
                    parsed["body"] = parsed["body"] + " もしかしてyoutube投稿?youtubeはyoutube板からお願い(ﾟДﾟ)"
                elif d:
                    self.deleteThread({"id": d.group("deleteid")}, force = True)
                    return

            username = ((parsed["name"] + "匿名")[0:5])
            if "random" in message:
                pseuduseruuid = str(uuid.uuid4())[0:5]
                manager.ResponseManager.set_response(parsed["id"], parsed["body"]
                    , pseuduseruuid, username)
            else:
                manager.ResponseManager.set_response(parsed["id"], parsed["body"]
                    , useruuid, username)

            chat = dict(manager.ResponseManager.get_thread_response(parsed["id"])[-1])

            #import pdb;pdb.set_trace()
            chat["html"] = tornado.escape.to_basestring(
                self.render_string("message.html", message = chat))

            chat["commentnum"] = manager.ResponseManager.get_thread_responsenum(parsed["id"])
            ChatSocketHandler.send_updates(chat)
            userinfo = manager.UserManager.get_user(useruuid)
            #lolv = userinfo[0]["lolv"] + 10
            #manager.UserManager.set_lolv(useruuid, lolv)
            #PersonalSocketHandler.send_updates(useruuid, lolv)

        elif "delete" in parsed:
            print("delete clicked\n\n\n")
            self.deleteThread(parsed)
        else:
            logging.info("empty messge received")


    def deleteThread(self, parsed, force = None) :
        useruuid = self.get_secure_cookie("a").decode("utf-8")[0:5]
        thread = manager.ThreadManager.get_thread(parsed["id"])
        userinfo = manager.UserManager.get_user(useruuid = useruuid) 
        if len(userinfo) == 0:
            #import pdb; pdb.set_trace()
            return

        if  thread[0]["userid"] == userinfo[0]["id"] or force is not None:
            originalFileName = "./static/" + thread[0]["imagename"]
            thumbnaileFileName = "./static/" + thread[0]["thumbnailname"]

            if originalFileName != "./static/NoImage.jpeg":
                try:
                    os.remove(originalFileName)
                except:
                    print("remove originalFile failed")
            if thumbnaileFileName != "./static/NoImage.jpeg":
                try:
                    os.remove(thumbnaileFileName)
                except:
                    print("remove originalFile failed")

            images = ("NoImage.jpeg", "NoImage.jpeg")
            manager.ThreadManager.set_newimagename(thread[0]["id"], images)
            selected = manager.ThreadManager.get_thread(thread[0]["id"])
            thread = dict(selected[0])
            #ress = manager.ResponseManager.get_thread_response(thread["id"])
            #ressnum = len(manager.ResponseManager.get_response(thread["id"])[0])
            ressnum = manager.ResponseManager.get_thread_responsenum(thread["id"])

            thread["html"] = tornado.escape.to_basestring(
                self.render_string("images.html", image = thread, ressnum = ressnum))

            FileSocketHandler.send_updates(thread)

class FileSocketHandler(tornado.websocket.WebSocketHandler):
    ''' FileSockertHandlerクラス 
        ファイルの受信イベントを担当。ファイルを受信するとそれに基づいて画像を保存する"
    '''

    waiters = set()

    def get_compression_options(self):
        # Non-None enables compression with default options.
        return {}

    def open(self):
        FileSocketHandler.waiters.add(self)
        #import pdb; pdb.set_trace()

    def on_close(self):
        FileSocketHandler.waiters.remove(self)

    def on_message(self, message):
        useruuid = (self.get_secure_cookie("a").decode("utf-8"))[0:5]
        manager.UserManager.set_user(useruuid)
        if type(message) is not bytes:
            parsed = tornado.escape.json_decode(message)
            selected = manager.ThreadManager.set_thread(
                parsed["boardname"], None, parsed["threadname"], useruuid, 0)

            userinfo = manager.UserManager.get_user(useruuid)
            lolv = userinfo[0]["lolv"] + 1000
            manager.UserManager.set_lolv(useruuid, lolv)
            PersonalSocketHandler.send_updates(useruuid, lolv)

        else:
            names = manager.ThreadManager.set_image(message)

            #import pdb;pdb.set_trace()
            selected = manager.ThreadManager.set_thread("ImageBoard", names, names[0], useruuid, FileSocketHandler.requiredlolv)

            thread = dict(selected[0])
            ress = manager.ResponseManager.get_response(thread["id"])
            #ressnum = len(manager.ResponseManager.get_response(thread["id"])[0])
            ressnum = manager.ResponseManager.get_thread_responsenum(thread["id"])

            thread["html"] = tornado.escape.to_basestring(
                self.render_string("images.html", image=thread, ressnum=ressnum))
            FileSocketHandler.send_updates(thread)
            userinfo = manager.UserManager.get_user(useruuid)
            lolv = userinfo[0]["lolv"] + 1000
            manager.UserManager.set_lolv(useruuid, lolv)
            PersonalSocketHandler.send_updates(useruuid, lolv)

    @classmethod
    def send_updates(cls, thread):
        logging.info("sending image to %d waiters ", len(FileSocketHandler.waiters))
        #import pdb; pdb.set_trace() 
        for waiter in cls.waiters:
            try:
                waiter.write_message(thread)
            except:
                logging.error("Error sending message", exc_info=True)

class WaiterSocketHandler(tornado.websocket.WebSocketHandler):
    ''' Waiter Socket Handler class
        現在閲覧中の人数を表示するための情報受け渡しクラス '''
    waiters = set()

    def get_compression_options(self):
        # Non-None enables compression with default options.
        return {}

    def open(self):
        WaiterSocketHandler.waiters.add(self)
        if random.randint(0,9) > 0:
            message = {"html": tornado.escape.to_basestring(
                self.render_string("waiternum.html", num = len(WaiterSocketHandler.waiters) + 6))}
            WaiterSocketHandler.send_updates(message)

    def on_close(self):
        WaiterSocketHandler.waiters.remove(self)
        if random.randint(0,9) > 0:
            message = {"html": tornado.escape.to_basestring(
                self.render_string("waiternum.html", num = len(WaiterSocketHandler.waiters) + 6))}
            WaiterSocketHandler.send_updates(message)

    def on_message(self, message):
        pass

    @classmethod
    def send_updates(cls, message):
        #logging.info("sending waiternum to %d waiters", len(cls.waiters))
        for waiter in cls.waiters:
            try:
                waiter.write_message(message)
            except:
                logging.error("Error sending n1um message", exc_info=True)

class LoveSocketHandler(tornado.websocket.WebSocketHandler):
    waiters = set()

    def get_compression_options(self):
        # Non-None enables compression with default options.
        return {}

    def open(self):
        LoveSocketHandler.waiters.add(self)

    def on_close(self):
        LoveSocketHandler.waiters.remove(self)

    def on_message(self, message):
        parsed = tornado.escape.json_decode(message)
        thread = manager.ThreadManager.get_thread(parsed["id"])
        love = thread[0]["love"]
        love = min(int(love*1.01 + 1), 100000000000000)
        manager.ThreadManager.set_love(parsed["id"], love)
        message = {
            "id": parsed["id"],
            "lovenum": love
        }
        LoveSocketHandler.send_updates(message)

    @classmethod
    def send_updates(cls, message):
        logging.info("sending Love to %d waiters", len(cls.waiters))
        for waiter in cls.waiters:
            try:
                waiter.write_message(message)
            except:
                logging.error("Error sending message", exc_info=True)

class ThreadSocketHandler(tornado.websocket.WebSocketHandler):
    ''' ThreaedSocketHandler class
        スレッドのリアルタイム表示に対応するためのクラス
    '''
    waiters = set()

    def get_compression_options(self):
        # Non-None enables compression with default options.
        return {}

    def open(self):
        ThreadSocketHandler.waiters.add(self)

    def on_close(self):
        ThreadSocketHandler.waiters.remove(self)

    def on_message(self, message):
        parsed = tornado.escape.json_decode(message)
        thread = manager.ThreadManager.get_thread(parsed["id"])
        useruuid = self.get_secure_cookie("a")[0:5].decode("utf-8")
        userinfo = manager.UserManager.get_user(useruuid)
        if userinfo[0]["lolv"] < int(thread[0]["requiredlolv"]):
            return

        if parsed["type"] == "image":
            #import pdb; pdb.set_trace()
            parsed["html"] = tornado.escape.to_basestring(
                self.render_string("imagethread.html"
                , thread = thread[0], manager = manager))
            try: 
                self.write_message(parsed)
            except:
                logging.error("Eror sending Thread", exc_info=True)
        elif parsed["type"] == "youtube":
            #import pdb; pdb.set_trace()
            parsed["html"] = tornado.escape.to_basestring(
                self.render_string("youtubethread.html"
                , thread = thread[0], manager = manager))
            try: 
                self.write_message(parsed)
            except:
                logging.error("Eror sending Thread", exc_info=True)

        elif parsed["type"] == "text":
            parsed["html"] = tornado.escape.to_basestring(
                self.render_string("textthread.html"
                , thread = thread[0], manager = manager)).replace("[[newlines_@@_]]", "<br>")
            try: 
                self.write_message(parsed)
            except:
                logging.error("Eror sending Thread", exc_info=True)

        lolv = max(userinfo[0]["lolv"] - 10, 0)
        manager.UserManager.set_lolv(useruuid, lolv)
        PersonalSocketHandler.send_updates(useruuid, lolv)
            

class PersonalSocketHandler(tornado.websocket.WebSocketHandler):
    waiters = dict()

    def get_compression_options(self):
        # Non-None enables compression with default options.
        return {}

    def open(self):
        useruuid = self.get_secure_cookie("a")[0:5].decode("utf-8")
        if useruuid not in PersonalSocketHandler.waiters:
            PersonalSocketHandler.waiters[useruuid] = dict()
            PersonalSocketHandler.waiters[useruuid]["session"] = set() 

        PersonalSocketHandler.waiters[useruuid]["session"].add(self) 

    def on_close(self):
        useruuid = self.get_secure_cookie("a")[0:5].decode("utf-8")
        PersonalSocketHandler.waiters[useruuid]["session"].remove(self)

    def on_message(self, message):
        pass

    @classmethod
    def send_updates(cls, useruuid, lolv):
        #import pdb; pdb.set_trace()
        parsed = dict() #tornado.escape.json_decode(message)
        parsed["lolv"] = lolv
        if useruuid in cls.waiters.keys() :
            for waiter in cls.waiters[useruuid]["session"]:
                try: 
                    waiter.write_message(parsed)
                except:
                    logging.error("Error sending Personal Info", exc_info=True)

def main():
    define("port", default=8888, help="run on the given port", type=int)
    um = manager.UserManager()
    tm = manager.ThreadManager()
    bm = manager.BoardManager()

    tornado.options.parse_command_line()
    app = Application()
    app.listen(options.port)
    tornado.ioloop.IOLoop.current().start()
