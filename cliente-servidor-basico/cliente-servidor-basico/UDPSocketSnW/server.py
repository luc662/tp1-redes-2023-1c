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
        log('(start)')
        UDP_IP = '127.0.0.1'
        UDP_PORT = 2001
    
        self.socket = UDPSocket(None)
        self.socket.bind((UDP_IP, UDP_PORT))
        self.operacion = {'upload':self.upload,'download':self.download}
        self.connections = []
        self.run()

    def download(self, parametros):
        [nombre_archivo] = parametros

        tamanio_archivo = os.stat(nombre_archivo).st_size
        log('Aceptamos peticion. Enviamos CONECTADO')
        self.socket.send(f'CONECTADO|{nombre_archivo}|{str(tamanio_archivo)}'.encode())
        
        log('Esperamos recibir mas datos:')
        with open(f'{nombre_archivo}','rb') as archivo:
            
            iters = ceil(tamanio_archivo/(self.socket.buffer_size-self.socket.header_size))
            for i in range(iters):
                log(f'Enviando... {i+1}/{iters}')
                bytes = archivo.read(self.socket.buffer_size-self.socket.header_size)
                self.socket.send(bytes)
            
        log('Fin del archivo')

        self.cerrar()

    def cerrar(self):
        log('Esperamos FIN')
        mensaje,address = self.socket.recieve()
        # recibir mensajes hasta que llegue FIN
        if f'{mensaje.decode()}' == 'FIN':
            log('Enviavos FINACK')
            self.socket.send('FINACK'.encode())

        log('Esperamos ACK')
        # esperamos ACK final del cliente
        mensaje, address = self.socket.recieve()
        log(f'Recibimos: {mensaje.decode()}')

        log('Fin server')

    def listen(self):
        log('(run)')
        log('Escuchando')
        mensaje, address = self.socket.recieve()
        log(f'Recibimos peticion: {mensaje}')
        self.socket.address = address
        payload = mensaje.decode()
        log(f'Recibimos peticion: {payload}')
        # aca se hace el branch a un nuevo thread/socket para este nuevo cliente

        l = payload.split('|')
        tipo_operacion = l[0]

        if tipo_operacion == 'upload':
            nombre_archivo = l[1]
            tamanio_archivo = l[2]
            tamanio_paquete = l[3]

            log(f'Tipo operacion: {tipo_operacion}')
            log(f'Nombre archivo: {nombre_archivo}')
            log(f'Tamanio del archivo: {tamanio_archivo}')
            log(f'Tamanio de paquete: {tamanio_paquete}')
            return tipo_operacion,[nombre_archivo,tamanio_archivo]
        elif tipo_operacion == 'download':
            nombre_archivo = l[1]
            log(f'Tipo operacion: {tipo_operacion}')
            log(f'Nombre archivo: {nombre_archivo}')
            return tipo_operacion,[nombre_archivo]

    def run(self):
        operacion, parametros = self.listen()
        log(f'fin listen. la operacion es: {operacion}')
        return self.operacion[operacion](parametros)

    def upload(self,parametros):
        [nombre_archivo,tamanio_archivo] = parametros
        log('Aceptamos peticion. Enviamos CONECTADO')
        self.socket.send('CONECTADO'.encode())
        
        log('Esperamos recibir mas datos:')
        with open(f'server_{nombre_archivo}','wb') as archivo:
            iters = ceil(int(tamanio_archivo)/(self.socket.buffer_size-8))
            for i in range(iters):
                log(f'Recibiendo... {i+1}/{iters}')
                while True:
                    mensaje, address = self.socket.recieve()
                    # si leo el mensaje, corto este ciclo y voy a leer el siguiente bloque de archivo
                    if mensaje:
                        log(f'Recibimos: {mensaje}')
                        log(f'De: {address}')
                        log(f'Tamanio: {len(mensaje)}')
                        archivo.write(mensaje)
                        break
                    # sino pregunto por el mismo archivo
            
        log('Fin del archivo')
        self.cerrar()
        
    
Server()