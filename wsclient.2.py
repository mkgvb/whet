import websocket
import threading
import time

def on_message(ws, message):
    print(message)

def on_error(ws, error):
    print(error)

def on_close(ws):
    print("### closed ###")

def on_open(ws):
    def run(*args):
        for i in range(3):
            time.sleep(1)
            ws.send("Hello %d" % i)
        time.sleep(1)
        ws.close()
        print("thread terminating...")
    t = threading.Thread(target=run, args=())
    t.start()

def send(ws, msg):
    ws.send(msg)





    #     threads = []
    # for x in range(ls.get_number_of_channels()):
    #     t = threading.Thread(target=channel_worker, args=(x,))
    #     threads.append(t)
    #     t.start()      


if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("ws://localhost:8080/chat/websocket",
                              on_message = on_message,
                              on_error = on_error,
                              on_close = on_close)
    ws.on_open = on_open
    ws.run_forever()