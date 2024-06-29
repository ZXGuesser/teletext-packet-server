#!/usr/bin/env python3

import socket
import threading
import queue
import time
import sys
import getopt

clientQueues = []

class client(object):
    def clientConected(clientsocket, addr, q):
        clientQueues.append(q)
        print(clientsocket)
        while True:
            try:
                clientsocket.sendall(q.get())
            except OSError as e:
                break # close
        clientQueues.remove(q)
        clientsocket.close()

def server(PORT):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 672)
    sock.bind(("0.0.0.0",PORT))
    sock.listen()
    while True:
        conn, addr = sock.accept()
        q = queue.Queue()
        cthread = threading.Thread(target=client.clientConected, args=(conn,addr,q))
        cthread.start()
    sock.close()

def server6(PORT):
    sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 672)
    # Python2.7.3 on Windows does not define IPPROTO_IPV6,
    # see http://bugs.python.org/issue6926.
    try:
        sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 1)
    except AttributeError:
        pass
    sock.bind(("::",PORT))
    sock.listen()
    while True:
        conn, addr = sock.accept()
        q = queue.Queue()
        cthread = threading.Thread(target=client.clientConected, args=(conn,addr,q))
        cthread.start()
    sock.close()

if __name__ == "__main__":
    PORT = 0
    linesPerField = 0
    inputfile = sys.stdin
    
    try:
        opts, args = getopt.getopt(sys.argv[1:],"p:l:i:")
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
        elif opt in ('-l'):
            try:
                linesPerField = int(arg)
            except:
                print("invalid lines per field")
                sys.exit(2)
        elif opt in ('-i'):
            try:
                inputfile = open(arg, "r")
            except:
                print("failed to open file")
                sys.exit(2)
    
    if PORT <= 1024 or PORT > 65535:
        print("invalid port, use -p <port>")
        sys.exit(2)
    
    if linesPerField <= 0 or linesPerField > 16:
        print("invalid lines per field, use -l <lines per field>")
        sys.exit(2)
    
    thread = threading.Thread(target = server, args=(PORT,))
    thread.daemon = True
    thread.start()
    
    thread6 = threading.Thread(target = server6, args=(PORT,))
    thread6.daemon = True
    thread6.start()
    
    starttime=time.time()
    
    while(True):
        data = bytearray(inputfile.buffer.read(42 * linesPerField))
        if not data:
            inputfile.seek(0) # loop input file
            continue
        if (linesPerField < 16):
            data.extend(bytearray(42*(16-linesPerField)))
        data.extend(bytearray(inputfile.buffer.read(42 * linesPerField)))
        if (linesPerField < 16):
            data.extend(bytearray(42*(16-linesPerField)))
        for q in clientQueues[:]:
            if q.qsize() > 4: # allow 4 fields of buffering
                with q.mutex:
                    q.queue.clear()
            q.put(data)
        time.sleep(0.04 - ((time.time() - starttime) % 0.04))