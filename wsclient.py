from websocket import create_connection
ws = create_connection("ws://localhost:8080/chat/websocket")
print("Sending 'Hello, World'...")
ws.send("Hello, World")
print("Sent")
print("Receiving...")
result =  ws.recv()
print("Received '%s'" % result)

def send(msg):
    ws.send(msg)


def close(msg):
    ws.close()


# i = 0
# while ( i < 100):
#     print("Sending")
#     ws.send(str(i))
#     print("Sent")
#     print("Receiving...")
#     result =  ws.recv()
#     print("Received '%s'" % result)
#     i += 1
#     time.sleep(1)

