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
        self.socket = UDPSocket((self.server_address,self.server_port))
        print('socket creado')
        self.run()

    def run(self):
        log('(run)')
        nombre_archivo = 'file.txt'
        log(f'archivo: {nombre_archivo}')

        # obtener tamaño del archivo
        tamanio_archivo = os.stat(nombre_archivo).st_size
        log(f'El tamanio del archivo es: {tamanio_archivo}')
        log(f'Armando mensaje de capa de app:')
        mensaje = '|upload|'+nombre_archivo+'|'+str(tamanio_archivo)+'|'
        tamanio_mensaje = str(len(mensaje))
        payload = f'{mensaje,tamanio_mensaje}'
        log(f'Mensaje: {payload}')
        log('Enviando')
        self.socket.send(payload.encode())
        log('Enviado!')

        log('Esperando respuesta del Servidor')
        log('Esperamos que nos diga CONECTADO (a nivel capa de app)')
        mensaje,address = self.socket.receive()
        log(f'Respuesta del servidor: {mensaje.decode()}')

        if mensaje.decode() != 'CONECTADO':
            log('No llego el CONECTADO del servidor')
            exit()

        log('Continuamos en el upload')
        with open(nombre_archivo,'rb') as archivo:
            log(f'Abriendo archivo: {nombre_archivo}')
            # El 8 de aca abajo esta hardcodeado, es el tamaño del header
            iters = ceil(tamanio_archivo/(self.socket.buffer_size-8))
            #while True: # cabiar por un for
            for i in range(iters):
                log(f'Leer {self.socket.buffer_size-8}B {i}/{iters}')
                bytes = archivo.read(self.socket.buffer_size-8) 
                #if not bytes:
                #    log('Fin del archivo!')
                #    break
                
                payload = '|'+str(bytes)+'|'+str(len(bytes))+'|'
                log(f'Mensaje: {payload}')
                log('Enviando')
                self.socket.send(payload.encode())
                log('Enviado!')

                # esperamos respuesta del server
                #print('esperamos respuesta del server ')
                #mensaje = socket.receive()
                #print(f'respuesta del server: {mensaje.decode()}')

            log('Cerrar archivo')

        #self.socket.send()

        log('Fin de la transmision del archivo')
        log('Comenzamos cierre de conexion')

        # enviamos FIN
        log('enviamos FIN al servidor')
        #socket.close()
        payload = 'FIN'
        self.socket.send(payload.encode())

        # esperamos FINACK
        mensaje,address = self.socket.receive()
        print(f'recibimos: {mensaje.decode()}')

        print('enviamos ACK')
        self.socket.send('ACK'.encode())

        print('fin del cliente')

Client()