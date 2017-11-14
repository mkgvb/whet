import logging
from websocket import create_connection




#ws = create_connection("ws://localhost:7999/chat/websocket")


#result =  ws.recv()
#print("Received '%s'" % result)


def send(msg):
    try:
        ws.send(msg)
    except BrokenPipeError:
        print("***unable to send message! Trying to reconnect")
        try:
            ws.connect("ws://localhost:7999/chat/websocket")
        except ConnectionRefusedError:
            print("***Connection failed")


def close(msg):
    ws.close()

def on_message(ws, message):
    print(message)