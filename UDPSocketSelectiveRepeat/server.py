import logging
import threading
from math import ceil
from logging import debug as db
logging.basicConfig(level=logging.DEBUG, format='%(message)s')
from UDPSocketSelectiveRepeat import UDPSocketGBN as UDPSocket
from OrdenadorDePaquetes import OrdenadorDePaquetes

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
        mensaje, address, seq_number = self.socket.receive()
        self.socket.address = address
        payload = mensaje.decode()
        log(f'Recibimos peticion: {payload}')
        # aca se hace el branch a un nuevo thread/socket para este nuevo cliente

        l = payload.split('|')
        tipo_operacion = l[0]
        nombre_archivo = l[1]
        tamanio_archivo = l[2]
        tamanio_paquete = l[3]

        log(f'Tipo operacion: {tipo_operacion}')
        log(f'Nombre archivo: {nombre_archivo}')
        log(f'Tamanio del archivo: {tamanio_archivo}')
        log(f'Tamanio de paquete: {tamanio_paquete}')

        log('Aceptamos peticion. Enviamos CONECTADO')
        self.socket.send_and_wait_for_ack('CONECTADO'.encode())
        
        log('Esperamos recibir mas datos:')
        with open(f'server_{nombre_archivo}','wb') as archivo:
            iters = ceil(int(tamanio_archivo)/(self.socket.buffer_size-8))

            ordenadorDePaquetes = OrdenadorDePaquetes(ceil(int(tamanio_archivo)/(self.socket.buffer_size-8)))

            while not ordenadorDePaquetes.is_full():
                log(f'Recibiendo... /{iters}')
                mensaje, address, seq_number = self.socket.receive()
                # si leo el mensaje, corto este ciclo y voy a leer el siguiente bloque de archivo
                if mensaje:
                    log(f'De: {address}')
                    log(f'Tamanio: {len(mensaje)}')
                    log(f'seq_number: {seq_number}')
                    ordenadorDePaquetes.add(seq_number - 1, mensaje)
                    break
                    # sino pregunto por el mismo archivo

                else:
                    log(f'No Hubo Mensaje: {mensaje}')

            # escribo el archivo
            for i in range(iters):
                valor = ordenadorDePaquetes.get(i)
                if not valor:
                    log(f'No Hubo Mensaje: {i}')
                    #raise Exception
                else:
                    archivo.write(ordenadorDePaquetes.get(i))

        log('Fin del archivo')
        '''
         log('Esperamos FIN')
            mensaje,address = self.socket.receive()
             recibir mensajes hasta que llegue FIN
            if f'{mensaje.decode()}' == 'FIN':
                log('Enviavos FINACK')
                self.socket.send('FINACK'.encode())
    
            #log('Esperamos ACK')
            # esperamos ACK final del cliente
            #mensaje,address = self.socket.receive()
            #log(f'Recibimos: {mensaje.decode()}')
        '''
        log('Fin server')
    
Server()