import socket
import threading
import struct
from UDPSocketSnW import UDPSocketSnW as UDPSocket

# Multithreaded Python server : UDP Server Socket Program Stub
UDP_IP = '127.0.0.1'
UDP_PORT = 2001
BUFFER_SIZE = 2000  # Usually 1024, but we need quick response

#server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#server_socket.bind((UDP_IP, UDP_PORT))
server_socket = UDPSocket(None)
server_socket.bind((UDP_IP, UDP_PORT))

#while True:
print("inicio")
#server_socket.listen(1)
#print("Multithreaded Python server : Waiting for connections from UDP clients...")
mensaje = server_socket.receive()
print(f'recibimos peticion: {mensaje.decode()}')
# aca se hace el branch a un nuevo thread/socket para este nuevo cliente

# enviamos ACK al cliente
#print('enviamos ACK')
#server_socket.send('ACK'.encode())#,address)


# loop para recibir los datos
print('recibimos mas datos')
while True:
    mensaje = server_socket.receive()
    print(f'recibimos: {mensaje.decode()}')

    # recibir mensajes hasta que llegue FIN
    if f'{mensaje.decode()}' == 'FIN':
        # enviar ACK
        server_socket.send('FINACK'.encode())#,address)
        break

    print('enviamos ACK')
    server_socket.send('ACK'.encode())

# esperamos ACK final del cliente
mensaje = server_socket.receive()
print(f'{mensaje.decode()}')

