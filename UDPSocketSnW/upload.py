import os
import logging
from math import ceil
from logging import debug as db

logging.basicConfig(level=logging.DEBUG, format='%(message)s')
from UDPSocketSnW import UDPSocketSnW as UDPSocket


def log(msg):
    db(f'[Client] {msg}')


class Upload:

    def __init__(self, server_ip="10.0.0.1", server_port=2001, filename='server_test.txt'):
        log('start')
        self.server_address = server_ip
        self.server_port = server_port
        self.socket = UDPSocket((self.server_address, self.server_port))
        self.filename = filename
        self.run()

    def cerrar(self):
        log('cerrar')
        payload = 'CERRAR'
        try:
            self.socket.send(payload.encode())
        except:
            return

        while True:
            mensaje, address = self.socket.recieve()
            if mensaje:
                break

        assert mensaje.decode() == 'CERRAROK'
        log(f'(cerrar) recibimos: {mensaje.decode()}')

        payload = 'ACK'
        try:
            self.socket.send(payload.encode())
        except:
            log('No se recibio el ultimo ACK. Cerrando conexion')

        log('fin cliente')

    def run(self):
        log('upload')
        operacion = 'upload'
        tamanio_archivo = os.stat(self.filename).st_size
        mensaje = f'{operacion}|{self.filename}|{str(tamanio_archivo)}'
        log('Armando Peticion al Servidor')
        self.socket.send(mensaje.encode())
        log('Peticion enviada')

        self.socket.expected_sequence_num = 0
        self.socket.sequence_number = 0
        log(f'Esperando respuesta del Servidor {self.socket.address}')
        while True:
            mensaje, address = self.socket.recieve()
            if mensaje:
                break
        log(f'Recibimos respuesta de: {address}')
        self.socket.address = address

        assert mensaje.decode() == 'CONECTADO'

        log('Abriendo archivo para lectura')
        with open(self.filename, 'rb') as archivo:
            iters = ceil(tamanio_archivo / (self.socket.buffer_size - self.socket.header_size))
            log(f'Cantidad de paquetes a enviar: {iters}')
            for i in range(iters):
                log(f'Enviando paquete {i + 1}/{iters}')
                bytes = archivo.read(self.socket.buffer_size - self.socket.header_size)
                self.socket.send(bytes)

        log('Fin del archivo')

        self.cerrar()


#Upload()
