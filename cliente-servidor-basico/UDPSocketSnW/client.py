import os
import logging
from math import ceil
from UDPSocketSnW import UDPSocketSnW

class Client:
    def __init__(self):
        logging.basicConfig(level=logging.DEBUG, format='%(message)s')
        logging.debug('(start)')
        self.server_address = "127.0.0.1"
        self.server_port = 2001
        self.socket = UDPSocketSnW((self.server_address, self.server_port))
        logging.debug('Socket creado')
        self.run()

    def run(self):
        logging.debug('(run)')
        nombre_archivo = 'file.txt'
        logging.debug(f'archivo: {nombre_archivo}')

        # obtener tamaño del archivo
        tamanio_archivo = os.stat(nombre_archivo).st_size
        logging.debug(f'El tamanio del archivo es: {tamanio_archivo}')
        logging.debug(f'Armando mensaje de capa de app:')
        mensaje = f'upload|{nombre_archivo}|{str(tamanio_archivo)}'
        mensaje += f'|{str(len(mensaje))}'
        logging.debug(f'Mensaje: {mensaje}')
        logging.debug('Enviando')
        self.socket.send(mensaje.encode())
        logging.debug('Enviado!')

        logging.debug('Esperando respuesta del Servidor')
        logging.debug('Esperamos que nos diga CONECTADO (a nivel capa de app)')
        mensaje, address = self.socket.receive()
        logging.debug(f'Respuesta del servidor: {mensaje.decode()}')

        if mensaje.decode() != 'CONECTADO':
            logging.debug('No llego el CONECTADO del servidor')
            exit()

        logging.debug('Continuamos en el upload')
        with open(nombre_archivo,'rb') as archivo:
            logging.debug(f'Abriendo archivo: {nombre_archivo}')
            header_size = 8
            iters = ceil(tamanio_archivo/(self.socket.buffer_size-header_size))
            for i in range(iters):
                logging.debug(f'Leer {self.socket.buffer_size-header_size}B {i}/{iters}')
                bytes = archivo.read(self.socket.buffer_size-header_size) 
                
                payload = '|'+str(bytes)+'|'+str(len(bytes))+'|'
                logging.debug(f'Mensaje: {payload}')
                logging.debug('Enviando')
                self.socket.send(payload.encode())
                logging.debug('Enviado!')

            logging.debug('Cerrar archivo')

        logging.debug('Fin de la transmision del archivo')
        logging.debug('Comenzamos cierre de conexion')

        # enviamos FIN
        logging.debug('Enviamos FIN al servidor')
        #socket.close()

        payload = 'FIN'
        self.socket.send(payload.encode())

        # esperamos FINACK
        mensaje, address = self.socket.receive()
        print(f'Recibimos: {mensaje.decode()}')

        print('Enviamos ACK')
        self.socket.send('ACK'.encode())

        print('Fin del cliente')

Client()