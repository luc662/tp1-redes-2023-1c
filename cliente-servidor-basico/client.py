# Python TCP Client A
import socket

host = socket.gethostname()
port = 2004
BUFFER_SIZE = 2000
MESSAGE = input("tcpClientA: Enter message/ Enter exit:")

tcpClientA = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
tcpClientA.connect((host, port))
if MESSAGE == 'exit':
    tcpClientA.sendto(MESSAGE.encode(), (host, port))

while MESSAGE != 'exit':
    tcpClientA.sendto(MESSAGE.encode(), (host, port))
    data = tcpClientA.recv(BUFFER_SIZE)
    print (" Client2 received data:", data.decode())
    MESSAGE = input("tcpClientA: Enter message to continue/ Enter exit:")

