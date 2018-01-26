# -*- coding: utf-8 -*-
# kill -9 $(lsof -ti tcp:7999)
"""
    Simple sockjs-tornado chat application. By default will listen on port 7999.
"""
import logging
import json
from threading import Thread
import tornado.ioloop
import tornado.web
import sockjs.tornado

LIGHT_SCHEDULE_FILE = 'json/schedule.json'
SETTINGS_FILE = 'json/whet_settings.json'
OUTLET_FILE = 'outlet/outlet_schedule.json'
logger = logging.getLogger('__main__')

class RedirectHandler(tornado.web.RequestHandler):
    """Regular HTTP handler"""
    def get(self):
        self.redirect('web/')


class ChatConnection(sockjs.tornado.SockJSConnection):
    """Chat connection implementation"""
    # Class level variable
    participants = set()

    def on_open(self, info):
        self.participants.add(self)

    def on_message(self, message):
        # Broadcast message

        j_obj = json.loads('{"error":"Malformed json received"}')
        try:
            j_obj = json.loads(message)
        except ValueError:
            logger.info("Malformed json received %s", message)

        if "request" in j_obj:
            request = j_obj["request"]
            if request == "light_schedule": #rename to channel_properties
                with open(LIGHT_SCHEDULE_FILE, 'r') as data_file:
                    self.broadcast(self.participants, data_file.read())
            if request == "settings":
                with open(SETTINGS_FILE, 'r') as data_file:
                    self.broadcast(self.participants, data_file.read())
            if request == "outlet_schedule":
                with open(OUTLET_FILE, 'r') as data_file:
                    self.broadcast(self.participants, data_file.read())

        if "update" in j_obj:
            update = j_obj["update"]
            if "channels" in update:
                with open(LIGHT_SCHEDULE_FILE, 'w') as data_file:
                    data_file.write(json.dumps(update, indent=4))
            if "settings" in update:
                with open(SETTINGS_FILE, 'w') as data_file:
                    data_file.write(json.dumps(update, indent=4))
            if "outlet_schedule" in update:
                with open(OUTLET_FILE, 'w') as data_file:
                    data_file.write(json.dumps(update, indent=4))


        self.broadcast(self.participants, message)

    def on_close(self):
        # Remove client from the clients list and broadcast leave message
        self.participants.remove(self)

class Server(Thread):

    def __init__(self):
        super(Server, self).__init__(name="Server")

        # 1. Create chat router
        ChatRouter = sockjs.tornado.SockJSRouter(ChatConnection, '/chat')

        # 2. Create Tornado application
        app = tornado.web.Application(
                [
                    (r"/", RedirectHandler),
                    (r"/web", RedirectHandler),
                    (r"/web/(.*)",tornado.web.StaticFileHandler,{"path":r"web/", "default_filename": "index.html"})
                ]
                + ChatRouter.urls, debug=True


                #tornado.web.StaticFileHandler, {"path":r"../web/"}),]) 
        )

        # 3. Make Tornado app listen on port 7999
        # kill -9 $(lsof -ti tcp:7999)
        app.listen(7999)

    def run(self):
        # 4. Start IOLoop
        tornado.ioloop.IOLoop.instance().start()

    def stop(self):
        #'''stops IOLoop'''
        tornado.ioloop.IOLoop.instance().stop()
