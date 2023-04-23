import socket
import threading


# Multithreaded Python server : TCP Server Socket Thread Pool
class ClientThread():

    def __init__(self, ip, port, conn):

        thread = threading.Thread(target=self.run, args=[conn])
        thread.start()
        self.ip = ip
        self.port = port
        print("[+] New server socket thread started for " + ip + ":" + str(port))

    def run(self, conn):
        while True:
            data = conn.recv(2048)
            if data:
                msg = data.decode()
                print("Server received data:", msg)
                conn.send(data)  # echo
            else:
                print("se cerro la coneccion")
                break
        conn.close()



# Multithreaded Python server : TCP Server Socket Program Stub
TCP_IP = '0.0.0.0'
TCP_PORT = 2004
BUFFER_SIZE = 20  # Usually 1024, but we need quick response

tcpServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcpServer.bind((TCP_IP, TCP_PORT))
threads = []

while True:
    print("inicio")
    tcpServer.listen(1)
    print("Multithreaded Python server : Waiting for connections from TCP clients...")
    (conn, (ip, port)) = tcpServer.accept()
    newthread = ClientThread(ip, port, conn)


for t in threads:
    t.join()
