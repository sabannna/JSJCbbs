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

import re


class TextHandler(tornado.web.RequestHandler):
    def get(self, text=None):
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
        imageboard = manager.BoardManager.get_board("TextBoard")
        roungethread = manager.ThreadManager.get_board_thread(roungeboard[0]["boardname"])
        imagethreads = manager.ThreadManager.get_board_thread(imageboard[0]["boardname"], order="lastupdate")
        #import pdb; pdb.set_trace()
        
        self.render("textboard.html", roungeboard = roungeboard[0], roungethread = roungethread[0], textthreads = imagethreads, manager = manager, lolv = lolv)

class TextSocketHandler(tornado.websocket.WebSocketHandler):
    waiters = set()

    def get_compression_options(self):
        # Non-None enables compression with default options.
        return {}

    def open(self):
        TextSocketHandler.waiters.add(self)

    def on_close(self):
        TextSocketHandler.waiters.remove(self)

    def on_message(self, message):
        useruuid = (self.get_secure_cookie("a").decode("utf-8"))[0:5]
        manager.UserManager.set_user(useruuid)

        parsed = tornado.escape.json_decode(message)
        if "body" in parsed:
            if parsed["body"] == "" :
                logging.info("empty messge received")
                return
            else :
                username = ((parsed["name"] + "匿名")[0:5])
                parsed["body"] = parsed["body"].replace("\n", "[[newlines_@@_]]")

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
                    self.render_string("message.html", message = chat)).replace("[[newlines_@@_]]", "<br>")
                chat["commentnum"] = manager.ResponseManager.get_thread_responsenum(parsed["id"])
                TextSocketHandler.send_updates(self, chat, sendtype = "newress")
 
        elif "threadname" in parsed:
            if parsed["threadname"] != "" :
                userinfo = manager.UserManager.get_user(useruuid)
                if userinfo[0]["lolv"] < int(100):
                    return

                selected = manager.ThreadManager.set_thread("TextBoard"
                , (parsed["threadname"], (str(uuid.uuid4()))[0:10])
                , parsed["threadname"]
                , useruuid, 0)

                TextSocketHandler.send_updates(self, selected[0], sendtype ="thread")

                from chatdemo import PersonalSocketHandler
                lolv = max(userinfo[0]["lolv"] - 100, 0)
                manager.UserManager.set_lolv(useruuid, lolv)
                PersonalSocketHandler.send_updates(useruuid, lolv)
                return

        elif "delete" in parsed:
            print("delete clicked\n\n\n")
            self.deleteThread(parsed)
        else:
            logging.info("empty messge received")

    @classmethod
    def send_updates(cls, self, selected, sendtype):
        if sendtype == "thread":
            #from chatdemo import FileSocketHandler
            thread = dict(selected)
            ress = manager.ResponseManager.get_response(thread["id"])
            ressnum = manager.ResponseManager.get_thread_responsenum(thread["id"])

            thread["html"] = tornado.escape.to_basestring(
                self.render_string("texts.html", text=thread, ressnum = ressnum))            
        else:
            thread = selected

        thread["type"] = sendtype
            
        logging.info("sending text to %d waiters ", len(cls.waiters))
        #import pdb; pdb.set_trace() 
        for waiter in cls.waiters:
            try:
                waiter.write_message(thread)
            except:
                logging.error("Error sending message", exc_info=True)


    def deleteThread(self, parsed, force=None) :
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

            images = ("/static/NoImage.jpeg", "/static/NoImage.jpeg")
            manager.ThreadManager.set_newimagename(thread[0]["id"], images)
            selected = manager.ThreadManager.get_thread(thread[0]["id"])
            TextSocketHandler.send_updates(self, selected)
            #thread = dict(selected[0])
            #ress = manager.ResponseManager.get_thread_response(thread["id"])
            #ressnum = len(manager.ResponseManager.get_response(thread["id"])[0])
            #ressnum = manager.ResponseManager.get_thread_responsenum(thread["id"])

            #thread["html"] = tornado.escape.to_basestring(
            #    self.render_string("texts.html", youtube = thread, ressnum = ressnum))

            #from chatdemo import FileSocketHandler
            #FileSocketHandler.send_updates(thread)
