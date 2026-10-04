"""Activity 20: show that one recv() call can return several requests at once."""

import socket
import time

PORT = 17000                                     # the course's usual service port

server = socket.create_server(("127.0.0.1", PORT))       # server: listen
client = socket.create_connection(("127.0.0.1", PORT))   # client: connect
conn, _ = server.accept()                        # server: accept the connection

# The client makes three separate sends. The third is only part of a request.
client.sendall(b'{"type":"query","request_id":"a","query":[1,2,3]}\n')
client.sendall(b'{"type":"query","request_id":"b","query":[3,1,1]}\n')
client.sendall(b'{"type":"query","request_id":"c","query":[0,')
time.sleep(0.2)                                  # give the bytes time to arrive

data = conn.recv(4096)                           # the server makes ONE receive call
print("recv() returned", len(data), "bytes:")
print(data)
with open("results/stream-bytes.bin", "wb") as f:
    f.write(data)                                # saved for Step 4

for s in (conn, client, server):
    s.close()
