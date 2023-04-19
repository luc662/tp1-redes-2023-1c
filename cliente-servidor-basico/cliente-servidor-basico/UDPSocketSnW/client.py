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
        log('(start)')
        self.server_address = "127.0.0.1"
        self.server_port = 2001
        self.socket = UDPSocket((self.server_address, self.server_port))
        log('Socket creado')
        self.run()

    def run(self):
        log('(run)')
        nombre_archivo = 'test.txt'
        log(f'archivo: {nombre_archivo}')

        # obtener tamaño del archivo
        operacion = 'upload'
        tamanio_archivo = os.stat(nombre_archivo).st_size
        log(f'El tamanio del archivo es: {tamanio_archivo}')
        log(f'Armando mensaje de capa de app:')
        mensaje = f'{operacion}|{nombre_archivo}|{str(tamanio_archivo)}'
        mensaje += f'|{str(len(mensaje))}'
        log(f'Mensaje: {mensaje}')
        log('Enviando')
        self.socket.send(mensaje.encode())
        log('Enviado!')

        log('Esperando respuesta del Servidor')
        log('Esperamos que nos diga CONECTADO (a nivel capa de app)')
        mensaje, address = self.socket.receive()
        log(f'Respuesta del servidor: {mensaje.decode()}')

        if mensaje.decode() != 'CONECTADO':
            log('No llego el CONECTADO del servidor')
            exit()

        log('Continuamos en el upload')
        with open(nombre_archivo, 'rb') as archivo:
            log(f'Abriendo archivo: {nombre_archivo}')
            header_size = 8
            iters = ceil(tamanio_archivo / (self.socket.buffer_size - header_size))
            for i in range(iters):
                log(f'Leer {self.socket.buffer_size - header_size}B {i}/{iters}')
                bytes = archivo.read(self.socket.buffer_size - header_size)
                log(f'leo: {bytes.decode()}')
                #payload = f'{bytes.decode()}|{str(len(bytes))}'
                log(f'Mensaje: {bytes.decode()}')
                log('Enviando')
                self.socket.send(bytes)
                log('Enviado!')

            log('Cerrar archivo')

        log('Fin de la transmision del archivo')
        log('Comenzamos cierre de conexion')

        # enviamos FIN
        log('Enviamos FIN al servidor')
        # socket.close()

        payload = 'FIN'
        self.socket.send(payload.encode())

        # esperamos FINACK
        mensaje, address = self.socket.receive()
        print(f'Recibimos: {mensaje.decode()}')

        print('Enviamos ACK')
        self.socket.send('ACK'.encode())

        print('Fin del cliente')


Client()
