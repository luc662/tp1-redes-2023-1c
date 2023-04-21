import logging
import threading
import os
from math import ceil
from logging import debug as db
logging.basicConfig(level=logging.DEBUG, format='%(message)s')
from UDPSocketSnW import UDPSocketSnW as UDPSocket

def log(msg):
    db(f'[Server] {msg}')

class Server:

    def __init__(self):
        log('start')
        UDP_IP = '127.0.0.1'
        UDP_PORT = 2001

        self.socket = UDPSocket(None)
        self.socket.bind((UDP_IP, UDP_PORT))
        self.operacion = {'upload':self.upload, 'download':self.download}
        self.connections = []
        self.run()

    def download(self, parametros):
        log('download')
        [nombre_archivo] = parametros
        tamanio_archivo = os.stat(nombre_archivo).st_size
        self.socket.send(f'CONECTADO|{nombre_archivo}|{str(tamanio_archivo)}'.encode())

        with open(f'{nombre_archivo}','rb') as archivo:
            iters = ceil(tamanio_archivo/(self.socket.buffer_size-self.socket.header_size))
            for i in range(iters):
                bytes = archivo.read(self.socket.buffer_size-self.socket.header_size)
                self.socket.send(bytes)

    def cerrar(self):
        log('cerrar')
        mensaje,address = self.socket.recieve()
        if f'{mensaje.decode()}' == 'FIN':
            self.socket.send('FINACK'.encode())
        mensaje, address = self.socket.recieve()

    def listen(self):
        log('listen')
        mensaje, address = self.socket.recieve()
        if not mensaje:
            return 'retry',[]

        log(f'>{mensaje}')
        self.socket.address = address
        payload = mensaje.decode()
        l = payload.split('|')
        tipo_operacion = l[0]

        if tipo_operacion == 'upload':
            nombre_archivo = l[1]
            tamanio_archivo = l[2]
            return tipo_operacion,[nombre_archivo,tamanio_archivo]
        elif tipo_operacion == 'download':
            nombre_archivo = l[1]
            return tipo_operacion,[nombre_archivo]

    def run(self):
        log('run')
        while True:
            operacion, parametros = self.listen()
            if operacion != 'retry':
                break

        self.operacion[operacion](parametros)
        self.cerrar()
        log('Fin')

    def upload(self,parametros):
        log('upload')
        [nombre_archivo,tamanio_archivo] = parametros
        self.socket.send('CONECTADO'.encode())
        with open(f'server_{nombre_archivo}','wb') as archivo:
            iters = ceil(int(tamanio_archivo)/(self.socket.buffer_size-8))
            for i in range(iters):
                mensaje, address = self.socket.recieve()
                archivo.write(mensaje)

Server()