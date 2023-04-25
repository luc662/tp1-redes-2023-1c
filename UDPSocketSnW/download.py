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
        self.filename = 'server_test.txt'
        self.run()

    def run(self):
        log('download')

        operacion = 'download'
        mensaje = f'{operacion}|{self.filename}'
        self.socket.send(mensaje.encode())

        self.socket.sequence_number = 0
        self.socket.expected_sequence_num = 0
        mensaje, address = self.socket.recieve()
        self.socket.address = address
        [status,filename,filesize] = mensaje.decode().split('|')

        log(f'status: {status}')

        assert status == 'CONECTADO'
        assert filename == self.filename

        with open(f'client_{self.filename}', 'wb') as archivo:
            iters = ceil(int(filesize) / (self.socket.buffer_size - self.socket.header_size))
            i = 0
            while i < iters:
                log(f'Recibiendo paquete {i+1}/{iters}')
                bytes, address = self.socket.recieve()
                if bytes:
                    i += 1
                    archivo.write(bytes)
        
        self.cerrar()

    def cerrar(self):
        log('cerrar')
        payload = 'CERRAR'
        try:
            self.socket.send(payload.encode())
        except Exception:
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
        except Exception:
            log('No se recibio el ultimo ACK. Cerrando conexion')

        log('fin cliente')

Client()
