import logging
import threading
import os
from math import ceil
from logging import debug as db
logging.basicConfig(level=logging.DEBUG, format='%(message)s')
from UDPSocketSnW import UDPSocketSnW as UDPSocket

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
            raise Exception('ÑÑÑÑÑ')
    
    def download(self, parametros):
        logCT('download')
        [nombre_archivo] = parametros
        tamanio_archivo = os.stat(nombre_archivo).st_size
        logCT('Aceptando conexion del Cliente')
        logCT(f'{nombre_archivo}: {tamanio_archivo}')
        self.socket.send(f'CONECTADO|{nombre_archivo}|{str(tamanio_archivo)}'.encode())

        logCT('Abro archivo para empezar a leer')
        with open(f'{nombre_archivo}','rb') as archivo:
            iters = ceil(tamanio_archivo/(self.socket.buffer_size - self.socket.header_size))
            logCT(f'Cantidad de paquetes a enviar: {iters}')
            for i in range(iters):
                logCT(f'Enviando paquete {i+1}/{iters}')
                bytes = archivo.read(self.socket.buffer_size-self.socket.header_size)
                self.socket.send(bytes)
                logCT('Enviado')

    def upload(self, parametros):
        logCT('upload')
        [nombre_archivo, tamanio_archivo] = parametros
        logCT('Aceptando conexion del Cliente')
        self.socket.send('CONECTADO'.encode())

        logCT('Abro archivo para empezar a escribir')
        with open(f'server_{nombre_archivo}','wb') as archivo:
            iters = ceil(tamanio_archivo/(self.socket.buffer_size - self.socket.header_size))
            logCT(f'Cantidad de paquetes a recibir: {iters}')
            i = 0
            while i < iters:
                logCT(f'Recibiendo paquete {i+1}/{iters}')
                mensaje, address = self.socket.recieve()
                if mensaje:
                    i += 1
                    #logCT(f'Recibiendo: {mensaje}')
                    archivo.write(mensaje)

class Server:

    def __init__(self):
        log('start')
        UDP_IP = '127.0.0.1'
        UDP_PORT = 2001

        self.socket = UDPSocket(None)
        self.socket.bind((UDP_IP, UDP_PORT))
        self.threads = []

        self.run()

    def cerrar(self):
        log('cerrar')
        log('Esperando a que terminen los threads:')
        #for thread in self.threads:
        #    thread.join()
        log('Threads cerrados!')

    def listen(self):
        log('listen')
        mensaje_invalido = True
        while mensaje_invalido:
            mensaje, address = self.socket.recieve()
            if mensaje:
                mensaje_invalido = False

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
        self.threads.append(client)
        log('Iniciado')

    def run(self):
        log('run')
        running = True
        while running:
            self.listen()

        self.cerrar()
        log('Fin')

Server()