import logging
import threading
from math import ceil
from UDPSocketSnW import UDPSocketSnW

class Server:

    def __init__(self):
        logging.basicConfig(level=logging.DEBUG, format='%(message)s')
        logging.debug('(start)')
        UDP_IP = '127.0.0.1'
        UDP_PORT = 2001
    
        self.socket = UDPSocketSnW(None)
        self.socket.bind((UDP_IP, UDP_PORT))
        self.connections = []
        self.run()

    def run(self):
        logging.debug('(run)')
        logging.debug('Escuchando')
        mensaje, address = self.socket.receive()
        self.socket.address = address
        payload = mensaje.decode()
        logging.debug(f'Recibimos peticion: {payload}')
        # aca se hace el branch a un nuevo thread/socket para este nuevo cliente

        l = payload.split('|')
        tipo_operacion = l[0]
        nombre_archivo = l[1]
        tamanio_archivo = l[2]

        logging.debug(f'Tipo operacion: {tipo_operacion}')
        logging.debug(f'Nombre archivo: {nombre_archivo}')
        logging.debug(f'Tamanio del archivo: {tamanio_archivo}')
        logging.debug(f'Tamanio de mensaje: {l[3]}')

        logging.debug('Aceptamos peticion. Enviamos CONECTADO')
        self.socket.send('CONECTADO'.encode())
        
        logging.debug('Esperamos recibir mas datos:')
        with open(f'server_{nombre_archivo}','wb') as archivo:
            iters = ceil(int(tamanio_archivo)/(self.socket.buffer_size-8))
            for i in range(iters):
                logging.debug(f'Recibiendo... {i+1}/{iters}')
                mensaje, address = self.socket.receive()
                logging.debug(f'Recibimos: {mensaje}')
                logging.debug(f'De: {address}')
                logging.debug(f'Tamanio: {len(mensaje)}')
                archivo.write(mensaje)
            
        logging.debug('Fin del archivo')

        logging.debug('Esperamos FIN')
        mensaje, address = self.socket.receive()
        if f'{mensaje.decode()}' == 'FIN':
            logging.debug('Enviavos FINACK')
            self.socket.send('FINACK'.encode())

        logging.debug('Esperamos ACK')
        mensaje, address = self.socket.receive()
        logging.debug(f'Recibimos: {mensaje.decode()}')

        logging.debug('Fin server')
    
Server()