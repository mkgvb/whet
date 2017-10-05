from websocket import create_connection

ws = create_connection("ws://localhost:8888/ws/")


def msg(msg):
    ws.send(msg)
    print("Sent")

def response():
    print( ws.recv() )

def close():
    ws.close()