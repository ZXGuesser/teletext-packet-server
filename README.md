Teletext TCP Packet Server
--------------------------

packet-server.py takes a teletext packet stream and serves it to multiple clients.  
The script attempts to consume <lines per field> 42 byte packets from stdin every 20ms

test.py is a test client which connects to the server and outputs packets to stdout

The port is set using the -p argument, and the number of lines per field by -l

The server can be tested using example.t42:  
`cat example.t42 | python packet-server.py -p 19761 -l 16`

A suitable packet stream can be generated using https://github.com/peterkvt80/vbit2  
For example: `~/vbit2/vbit2 --dir ~/teletext | python packet-server.py -p 19761 -l 16`