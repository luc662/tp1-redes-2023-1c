# Python TCP Client A
from UDPSocketSnW import UDPSocketSnW as UDPSocket
import os
import struct
import socket

localIP     = "127.0.0.1"
server_address = "127.0.0.1"
server_port = 2001
host = socket.gethostname()
port = 2004
BUFFER_SIZE = 2000

print(f'client upload {host}:{port}')
print(f'buffersize: {BUFFER_SIZE}')

#client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#client_socket.bind((host,port)) # "opcional" (local)
client_socket = UDPSocket((server_address,server_port))
print('socket creado')

# enviar accion (upload)
nombre_archivo = 'test.txt'
print(f'archivo para upload: {nombre_archivo}')

# obtener tamaño del archivo
tamanio_archivo = 100 # os.path. getfilesize
mensaje = '|upload|'+nombre_archivo+'|'+str(tamanio_archivo)
tamanio_mensaje = str(len(mensaje))
payload = f'{mensaje,tamanio_mensaje}'
print(f'enviando: {payload}')

client_socket.send(payload.encode())
print('enviado')

print('esperando respuesta (ACK)')
# esperamos respuesta del server (ACK)
# por ej: tiene o no espacio para guardar el archivo
mensaje = client_socket.receive()
print(f'{mensaje.decode()}')

print('enviamos mas datos')
# enviamos datos
with open(nombre_archivo,'rb') as archivo:
    while True:
        bytes = archivo.read(64) # 64 bytes
        if not bytes:
            print('fin del archivo')
            break

        payload = str(bytes)+'|'+str(len(bytes))
        print(f'enviando: {payload}')
        client_socket.send(payload.encode())#, (server_address,server_port))

        # esperamos respuesta del server
        print('esperamos respuesta del server ')
        mensaje = client_socket.receive()
        print(f'respuesta del server: {mensaje.decode()}')

# enviamos FIN
print('enviamos FIN al servidor')
client_socket.close()
#payload = 'FIN'.encode()
#client_socket.send(payload)#,(server_address,server_port))

# esperamos FINACK
#mensaje = client_socket.receive()
#print(f'recibimos: {mensaje.decode()}')

#print('enviamos ACK')
#client_socket.send('ACK'.encode())#, (server_address,server_port))

print('fin del cliente')