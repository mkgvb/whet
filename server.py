# -*- coding: utf-8 -*-
# kill -9 $(lsof -ti tcp:8080)
"""
    Simple sockjs-tornado chat application. By default will listen on port 8080.
"""
import tornado.ioloop
import tornado.web
import sockjs.tornado


import json


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
        self.broadcast(self.participants, message)

    def on_close(self):
        # Remove client from the clients list and broadcast leave message
        self.participants.remove(self)
        json_msg = {'type': 'user', 'server_message': 'Someone left'}
        self.broadcast(self.participants, json.dumps(json_msg))

if __name__ == "__main__":
    import logging
    logging.getLogger().setLevel(logging.DEBUG)

    # 1. Create chat router
    ChatRouter = sockjs.tornado.SockJSRouter(ChatConnection, '/chat')

    # 2. Create Tornado application
    app = tornado.web.Application(
            [
                (r"/", IndexHandler),
                (r"/web/(.*)",tornado.web.StaticFileHandler,{"path":r"web/"})
            ] 
            + ChatRouter.urls, debug=True


            #tornado.web.StaticFileHandler, {"path":r"../web/"}),]) 
    )

    # 3. Make Tornado app listen on port 8080
    app.listen(8080)

    # 4. Start IOLoop
    tornado.ioloop.IOLoop.instance().start()