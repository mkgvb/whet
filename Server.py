# -*- coding: utf-8 -*-
# kill -9 $(lsof -ti tcp:8080)
"""
    Simple sockjs-tornado chat application. By default will listen on port 8080.
"""
import tornado.ioloop
import tornado.web
import sockjs.tornado
import logging
from threading import Thread
import json

light_schedule_file = 'json/schedule.json'
light_schedule_file2 = 'json/schedule2.json'
settings_file = 'json/settings.json'

class IndexHandler(tornado.web.RequestHandler):
    """Regular HTTP handler to serve the chatroom page"""
    def get(self):
        self.render('web/index.html')



class ChatConnection(sockjs.tornado.SockJSConnection):
    """Chat connection implementation"""
    # Class level variable
    participants = set()

    def on_open(self, info):
        # Send that someone joined
        json_msg = {'type': 'user', 'server_message': 'Someone joined'}
        self.broadcast(self.participants, json.dumps(json_msg))

        # Add client to the clients list
        self.participants.add(self)

    def on_message(self, message):
        # Broadcast message

        j_obj = json.loads('{"error":"Malformed json received"}')
        try:
            j_obj = json.loads(message)
        except (ValueError):
            logging.info("Malformed json received")

        if "channels" in j_obj:
            print("update")

        if "request" in j_obj:
            request = j_obj["request"]
            if request == "light_schedule": #rename to channel_properties
                with open(light_schedule_file, 'r') as data_file:
                    self.broadcast(self.participants, data_file.read())
            if request == "settings":
                with open(settings_file, 'r') as data_file:
                    self.broadcast(self.participants, data_file.read())

        if "update" in j_obj:
            update = j_obj["update"]
            if "channels" in update:
                with open(light_schedule_file, 'w') as data_file:
                    data_file.write(json.dumps(update, indent=4))
            if "settings" in update:
                with open(settings_file, 'w') as data_file:
                    data_file.write(json.dumps(update, indent=4))



        self.broadcast(self.participants, message)

    def on_close(self):
        # Remove client from the clients list and broadcast leave message
        self.participants.remove(self)
        json_msg = {'type': 'user', 'server_message': 'Someone left'}
        self.broadcast(self.participants, json.dumps(json_msg))

class Server(Thread):

    def __init__(self):
        super(Server, self).__init__(name="Server")
        import logging
        logging.getLogger().setLevel(logging.DEBUG)

        # 1. Create chat router
        ChatRouter = sockjs.tornado.SockJSRouter(ChatConnection, '/chat')

        # 2. Create Tornado application
        app = tornado.web.Application(
                [
                    #(r"/", IndexHandler),
                    (r"/web/(.*)",tornado.web.StaticFileHandler,{"path":r"web/", "default_filename": "index.html"})
                ] 
                + ChatRouter.urls, debug=True


                #tornado.web.StaticFileHandler, {"path":r"../web/"}),]) 
        )

        # 3. Make Tornado app listen on port 8080
        app.listen(8080)

    def run(self):
        # 4. Start IOLoop
        tornado.ioloop.IOLoop.instance().start()

    def stop(self):
        '''stops IOLoop'''
        tornado.ioloop.IOLoop.instance().stop()
