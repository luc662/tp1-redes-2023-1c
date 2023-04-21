import os
import logging
from math import ceil
from logging import debug as db

logging.basicConfig(level=logging.DEBUG, format='%(message)s')
from UDPSocketSnW import UDPSocketSnW as UDPSocket

def log(msg):
    db(f'[Client] {msg}')

class Client:
    def __init__(self):
        log('start')
        self.server_address = "127.0.0.1"
        self.server_port = 2001
        self.socket = UDPSocket((self.server_address, self.server_port))
        self.filename = 'test.txt'
        self.download()

    def download(self):
        log('download')

        nombre_archivo = 'server_test.txt'
        operacion = 'download'
        mensaje = f'{operacion}|{nombre_archivo}'
        log(f'>{mensaje}')
        self.socket.send(mensaje.encode())

        mensaje, address = self.socket.recieve()
        [status,filename,filesize] = mensaje.decode().split('|')

        log(f'status: {status}')

        assert status == 'CONECTADO'
        assert filename == nombre_archivo

        with open(f'client_{filename}', 'wb') as archivo:
            iters = ceil(int(filesize) / (self.socket.buffer_size - self.socket.header_size))
            for i in range(iters):
                bytes, address = self.socket.recieve()
                archivo.write(bytes)
        
        self.cerrar()

    def cerrar(self):
        log('cerrar')
        payload = 'FIN'
        self.socket.send(payload.encode())
        mensaje, address = self.socket.recieve()
        log(f'(cerrar) recibimos: {mensaje}')
        self.socket.send('ACK'.encode())

    def run(self):
        log('upload')
        nombre_archivo = 'test.txt'
        operacion = 'upload'
        tamanio_archivo = os.stat(nombre_archivo).st_size
        mensaje = f'{operacion}|{nombre_archivo}|{str(tamanio_archivo)}'
        log(f'>{mensaje}')
        self.socket.send(mensaje.encode())

        mensaje, address = self.socket.recieve()
        assert mensaje.decode() != 'CONECTADO'

        with open(nombre_archivo, 'rb') as archivo:
            header_size = 8
            iters = ceil(tamanio_archivo / (self.socket.buffer_size - header_size))
            for i in range(iters):
                bytes = archivo.read(self.socket.buffer_size - header_size)
                self.socket.send(bytes)

        self.cerrar()


Client()
