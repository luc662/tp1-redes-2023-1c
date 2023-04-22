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
        self.server_address = "10.0.0.1"
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
            i = 0
            while i < iters:
                log(f'Recibiendo paquete {i+1}/{iters}')
                bytes, address = self.socket.recieve()
                if bytes:
                    i+=1
                    log(f'Recibiendo: {bytes}')
                    archivo.write(bytes)
        
        self.cerrar()

    def cerrar(self):
        log('cerrar')
        #payload = 'FIN'
        #self.socket.send(payload.encode())
        #mensaje, address = self.socket.recieve()
        #log(f'(cerrar) recibimos: {mensaje}')
        #self.socket.send('ACK'.encode())

    def run(self):
        log('upload')
        nombre_archivo = 'test.txt'
        operacion = 'upload'
        tamanio_archivo = os.stat(nombre_archivo).st_size
        mensaje = f'{operacion}|{nombre_archivo}|{str(tamanio_archivo)}'
        log('Armando Peticion al Servidor')
        log(f'>{mensaje}')
        self.socket.send(mensaje.encode())
        log('Peticion enviada')

        log('Esperando respuesta del Servidor')
        mensaje, address = self.socket.recieve()

        log(f'Recibimos: {mensaje}')
        assert mensaje.decode() == 'CONECTADO'

        log('Abriendo archivo para lectura')
        with open(nombre_archivo, 'rb') as archivo:
            iters = ceil(tamanio_archivo / (self.socket.buffer_size - self.socket.header_size))
            log(f'Cantidad de paquetes a enviar: {iters}')
            for i in range(iters):
                log(f'Enviando paquete {i}/{iters}')
                bytes = archivo.read(self.socket.buffer_size - self.socket.header_size)
                log(f'Enviando: {bytes}')
                self.socket.send(bytes)

        log('Fin del archivo')
        self.cerrar()


Client()
