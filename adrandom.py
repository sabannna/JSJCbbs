import logging
import tornado.escape
import tornado.ioloop
import tornado.options
import tornado.web
import random

class AdRandom(tornado.web.UIModule):
    def render(self):
        return self.render_string("adrandom.html", random = random.randint(0,33))

