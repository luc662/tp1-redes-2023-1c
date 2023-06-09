import logging
import threading
import os
from math import ceil
from logging import debug as db

from OrdenadorDePaquetes import OrdenadorDePaquetes

logging.basicConfig(level=logging.DEBUG, format='%(message)s')
from UDPSocketSelectiveRepeat import UDPSocketSelectiveRepeat as UDPSocket


def logCT(msg):
    db(f'[CThread] {msg}')

def log(msg):
    db(f'[Server] {msg}')

class ClientThread:
    def __init__(self, socket, operacion, path, params):
        logCT('start')
        self.thread = threading.Thread(target=self.run, args=[operacion, params])
        self.socket = socket
        self.path = path
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
    
    def download(self, params):
        logCT('Aceptamos peticion. Enviamos CONECTADO')
        self.filename = params[0]
        logCT(f'Nombre archivo: {self.filename}')
        archivo = self.path + self.filename
        tamanio_archivo = os.stat(archivo).st_size

        data = self.socket.send_and_wait_for_ack(f'CONECTADO|{self.filename}|{str(tamanio_archivo)}'.encode())

        logCT(f'El tamanio del archivo es: {tamanio_archivo}')
        logCT(f'Armando mensaje de capa de app:')

        nombre_archivo = self.path + self.filename

        with open(f'{nombre_archivo}', 'rb') as archivo:
            logCT(f': {nombre_archivo}')
            # esto lo movemos un paso mas adentro al socket
            header_size = 8
            iters = ceil(tamanio_archivo / (self.socket.buffer_size - header_size))
            self.socket.enviar_archivo(tamanio_archivo, archivo)

            log('Cerrar archivo')

        logCT('Fin de la transmision del archivo')
        logCT('Comenzamos cierre de conexion')

        logCT('Fin client thread')

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
        filename = parametros[0]
        tamanio_archivo = parametros[1]
        logCT(f'Nombre archivo: {filename}')
        logCT(f'Tamanio del archivo: {tamanio_archivo}')

        logCT('Aceptamos peticion. Enviamos CONECTADO')
        try:
            data = self.socket.send_and_wait_for_ack('CONECTADO'.encode())
        except Exception:
            return

        logCT('Esperamos recibir mas datos:')
        with open(f'{self.path+filename}', 'wb') as archivo:
            iters = ceil(int(tamanio_archivo) / (self.socket.buffer_size - 8))

            ordenadorDePaquetes = OrdenadorDePaquetes(ceil(int(tamanio_archivo) / (self.socket.buffer_size - 8)))

            while not ordenadorDePaquetes.is_full():
                logCT(f'Recibiendo... {ordenadorDePaquetes.blocks_occupied}/{ordenadorDePaquetes.blocks}')
                mensaje, address, seq_number = self.socket.receive()
                # si leo el mensaje, corto este ciclo y voy a leer el siguiente bloque de archivo
                if mensaje is not None and seq_number is not None:
                    logCT(f'De: {address}')
                    logCT(f'Tamanio: {len(mensaje)}')
                    logCT(f'seq_number: {seq_number}')
                    ordenadorDePaquetes.add(seq_number - 1, mensaje)

            while True:
                mensaje, address, seq_number = self.socket.receive()
                if mensaje.decode() == 'FINALDEARCHIVO':
                    break

            # escribo el archivo
            for i in range(iters):
                valor = ordenadorDePaquetes.get(i)
                if not valor:
                    logCT(f'No Hubo Mensaje: {i}')
                else:
                    archivo.write(ordenadorDePaquetes.get(i))

        logCT('Fin del archivo')
        logCT('Fin client thread')

class Server:

    def __init__(self, ip, port, path='./'):
        log('start')

        self.socket = UDPSocket(None)
        self.socket.bind((ip, port))
        self.threads = {}
        self.path = path

        self.run()

    def cerrar(self):
        log('cerrar')
        log('Esperando a que terminen los threads:')

        log('Threads cerrados!')

    def listen(self):
        log('listen')
        while True:
            mensaje, address, seq_num = self.socket.receive()
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
            self.filename = l[1]
            tamanio_archivo = int(l[2])
            params = [self.filename, tamanio_archivo]
        elif tipo_operacion == 'download':
            self.filename = l[1]
            params = [self.filename]

        log('Iniciando thread')
        client = ClientThread(client_socket, tipo_operacion, self.path , params)
        self.threads[address] = client
        log('Iniciado')

    def run(self):
        log('run')
        running = True
        while running:
            self.listen()

        self.cerrar()
        log('Fin')
