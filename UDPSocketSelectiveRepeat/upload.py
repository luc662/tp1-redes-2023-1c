import os
import logging
from math import ceil
from logging import debug as db

logging.basicConfig(level=logging.DEBUG, format='%(message)s')
from UDPSocketSelectiveRepeat import UDPSocketSelectiveRepeat as UDPSocket


def log(msg):
    db(f'[Client] {msg}')


class Upload:

    def __init__(self, server_ip="10.0.0.1", server_port=2001, filename='server_test.txt', path='/.'):
        log('start')


        self.server_address = server_ip
        self.server_port = server_port
        log((self.server_address, self.server_port))
        self.socket = UDPSocket((self.server_address, self.server_port))
        self.filename = filename
        self.path = path
        return
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
        # borrar esto de abajo, y arreglar en server (upload)
        mensaje += f'|{str(len(mensaje))}'
        log(f'Mensaje: {mensaje}')
        log('Enviando')
        self.socket.send_and_wait_for_ack(mensaje.encode())
        log('Enviado!')

        log('Esperando respuesta del Servidor')
        log('Esperamos que nos diga CONECTADO (a nivel capa de app)')
        while True:
            mensaje, address, seq_number = self.socket.receive()
            if mensaje:
                break

        assert mensaje.decode() == 'CONECTADO'
        log(f'Respuesta de: {address}')
        self.socket.address = address

        log('Continuamos en el upload')

        with open(self.path + nombre_archivo, 'rb') as archivo:
            log(f'Abriendo archivo: {nombre_archivo}')
            self.socket.enviar_archivo(tamanio_archivo, archivo)

            log('Cerrar archivo')

        log('Fin de la transmision del archivo')
        log('Comenzamos cierre de conexion')

        print('Fin del cliente')