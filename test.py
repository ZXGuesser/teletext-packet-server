import socket
import select
import sys
import time
import getopt

HOST, PORT = "localhost", 0

try:
    opts, args = getopt.getopt(sys.argv[1:],"p:l:")
except getopt.GetoptError as err:
    print(err)
    sys.exit(2)

for opt, arg in opts:
    if opt in ('-p'):
        try:
            PORT = int(arg)
        except:
            print("invalid port")
            sys.exit(2)

if PORT <= 1024 or PORT > 65535:
    print("invalid port, use -p <port>")
    sys.exit(2)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

sock.connect((HOST, PORT))
try:
    sock.sendall(bytes("HELO", "utf-8"))

    starttime = time.time()

    while(True):
        inputready, outputready, exceptready = select.select([sock], [], [], 0 )
        if inputready:
            received = sock.recv(672)
            sys.stdout.buffer.write(received)
        time.sleep(0.02 - ((time.time() - starttime) % 0.02))
except:
    sock.close()
    raise