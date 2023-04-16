import logging
import threading
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
        self.connections = []
        self.run()

    def run(self):
        log('(run)')
        log('Escuchando')
        mensaje,address = self.socket.receive()
        self.socket.address = address
        payload = mensaje.decode()
        log(f'Recibimos peticion: {payload}')
        # aca se hace el branch a un nuevo thread/socket para este nuevo cliente

        l = payload.split('|')

        log(f'Tipo operacion: {l[1]}')
        log(f'Nombre archivo: {l[2]}')
        log(f'Tamanio del archivo: {l[3]}')
        log(f'Tamanio de mensaje: {l[4]}')

        log('Aceptamos peticion. Enviamos CONECTADO')
        self.socket.send('CONECTADO'.encode())
        
        log('Esperamos recibir mas datos:')
        with open('server_'+l[2],'wb') as archivo:
            for i in range(ceil(int(l[3])/self.socket.buffer_size)):
                log(f'Recibiendo...{i}')
                mensaje,address = self.socket.receive()
                log(f'Recibimos: {mensaje}')
                log(f'De: {address}')
                archivo.write(mensaje)
                
                #log('enviamos ACK')
                #self.socket.send('ACK'.encode())
            
        log('Fin del archivo')

        log('Esperamos FIN')
        mensaje,address = self.socket.receive()
        # recibir mensajes hasta que llegue FIN
        if f'{mensaje.decode()}' == 'FIN':
            log('Enviavos FINACK')
            self.socket.send('FINACK'.encode())

        log('Esperamos ACK')
        # esperamos ACK final del cliente
        mensaje,address = self.socket.receive()
        log(f'Recibimos :{mensaje.decode()}')

        log('Fin server')
    
Server()