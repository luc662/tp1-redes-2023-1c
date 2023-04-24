import logging
import threading
import os
from math import ceil
from logging import debug as db

from OrdenadorDePaquetes import OrdenadorDePaquetes

logging.basicConfig(level=logging.DEBUG, format='%(message)s')
from UDPSocketSelectiveRepeat import UDPSocketGBN as UDPSocket


def logCT(msg):
    db(f'[CThread] {msg}')

def log(msg):
    db(f'[Server] {msg}')

class ClientThread:
    def __init__(self, socket, operacion, params):
        logCT('start')
        self.thread = threading.Thread(target=self.run, args=[operacion, params])
        self.socket = socket
        ip = self.socket.address[0]
        port = self.socket.address[1]
        self.operacion = {
            'upload': self.upload, 
            'download': self.download
        }
        logCT(f'Nuevo cliente en {ip}:{port}')
        self.thread.start()

    def run(self, operacion, params):
        logCT('run')
        if operacion in self.operacion:
            self.operacion[operacion](params)
        else: 
            raise Exception
    
    def download(self, parametros):
        log('Aceptamos peticion. Enviamos CONECTADO')
        nombre_archivo = params[1]
        log(f'Nombre archivo: {nombre_archivo}')
        tamanio_archivo = os.stat(nombre_archivo).st_size

        data = self.socket.send_and_wait_for_ack(f'CONECTADO|{nombre_archivo}|{str(tamanio_archivo)}'.encode())

        log(f'El tamanio del archivo es: {tamanio_archivo}')
        log(f'Armando mensaje de capa de app:')

        with open(nombre_archivo, 'rb') as archivo:
            log(f'Abriendo archivo: {nombre_archivo}')
            # esto lo movemos un paso mas adentro al socket
            header_size = 8
            iters = ceil(tamanio_archivo / (self.socket.buffer_size - header_size))
            self.socket.enviar_archivo(tamanio_archivo, archivo)

            log('Cerrar archivo')

        log('Fin de la transmision del archivo')
        log('Comenzamos cierre de conexion')

        log('Fin server')

    def cerrar(self):
        logCT('cerrar')
        while True:
            mensaje, address = self.socket.recieve()
            if mensaje:
                break
        
        assert mensaje.decode() == 'CERRAR'

        self.socket.send('CERRAROK'.encode())

        while True:
            mensaje, address = self.socket.recieve()
            if mensaje and mensaje.decode() != 'ACK':
                break

    def upload(self, parametros):
        nombre_archivo = parametros[0]
        tamanio_archivo = parametros[1]
        log(f'Nombre archivo: {nombre_archivo}')
        log(f'Tamanio del archivo: {tamanio_archivo}')

        log('Aceptamos peticion. Enviamos CONECTADO')
        data = self.socket.send_and_wait_for_ack('CONECTADO'.encode())

        log('Esperamos recibir mas datos:')
        with open(f'server_{nombre_archivo}', 'wb') as archivo:
            iters = ceil(int(tamanio_archivo) / (self.socket.buffer_size - 8))

            ordenadorDePaquetes = OrdenadorDePaquetes(ceil(int(tamanio_archivo) / (self.socket.buffer_size - 8)))

            while not ordenadorDePaquetes.is_full():
                log(f'Recibiendo... {ordenadorDePaquetes.blocks_occupied}/{ordenadorDePaquetes.blocks}')
                mensaje, address, seq_number = self.socket.receive()
                # si leo el mensaje, corto este ciclo y voy a leer el siguiente bloque de archivo
                if mensaje is not None and seq_number is not None:
                    log(f'De: {address}')
                    log(f'Tamanio: {len(mensaje)}')
                    log(f'seq_number: {seq_number}')
                    ordenadorDePaquetes.add(seq_number - 1, mensaje)

            while True:
                mensaje, address, seq_number = self.socket.receive()
                if mensaje.decode() == 'FINALDEARCHIVO':
                    break

            # escribo el archivo
            for i in range(iters):
                valor = ordenadorDePaquetes.get(i)
                if not valor:
                    log(f'No Hubo Mensaje: {i}')

                else:
                    archivo.write(ordenadorDePaquetes.get(i))

        log('Fin del archivo')
        log('Fin server')

class Server:

    def __init__(self):
        log('start')
        UDP_IP = '10.0.0.1'
        UDP_PORT = 2001

        self.socket = UDPSocket(None)
        self.socket.bind((UDP_IP, UDP_PORT))
        self.threads = {}

        self.run()

    def cerrar(self):
        log('cerrar')
        log('Esperando a que terminen los threads:')
        #for thread in self.threads:
        #    thread.join()
        log('Threads cerrados!')

    def listen(self):
        log('listen')
        while True:
            mensaje, address = self.socket.recieve()
            log(f'(listen) mensaje recibido {address}')
            if mensaje and address not in self.threads:
                self.socket.expected_sequence_num = 0
                self.socket.sequence_number = 0
                break
            log('Recibimos None como peticion. Repitiendo')

        log(f'Conexion iniciada por Cliente: {address}')
        log('Creando socket')
        client_socket = UDPSocket(address)
        log('Socket creado')

        log('Interpretando pedido')
        payload = mensaje.decode()
        l = payload.split('|')
        tipo_operacion = l[0]
        params = []

        log(f'Operacion: {tipo_operacion}')
        if tipo_operacion == 'upload':
            nombre_archivo = l[1]
            tamanio_archivo = int(l[2])
            params = [nombre_archivo, tamanio_archivo]
        elif tipo_operacion == 'download':
            nombre_archivo = l[1]
            params = [nombre_archivo]

        log('Iniciando thread')
        client = ClientThread(client_socket, tipo_operacion, params)
        self.threads[address] = client
        log('Iniciado')

    def run(self):
        log('run')
        running = True
        while running:
            self.listen()

        self.cerrar()
        log('Fin')

Server()