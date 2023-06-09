import os
import logging
from math import ceil
from logging import debug as db
from OrdenadorDePaquetes import OrdenadorDePaquetes

logging.basicConfig(level=logging.DEBUG, format='%(message)s')
from UDPSocketSelectiveRepeat import UDPSocketSelectiveRepeat as UDPSocket


def log(msg):
    db(f'[Client] {msg}')


class Download:

    def __init__(self, server_ip="10.0.0.1", server_port=2001, filename='server_test.txt', path='/.'):
        log('start')
        self.server_address = server_ip
        self.server_port = server_port
        self.socket = UDPSocket((self.server_address, self.server_port))
        self.filename = filename
        self.path = path
        self.run()

    def run(self):
        log('(run)')
        operacion = 'download'
        log(f'Armando mensaje de capa de app:')
        mensaje = f'{operacion}|{self.filename}'
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

        log(f'Recibimos respuesta de: {address}')
        self.socket.address = address
        #self.socket.sequence_number = 0

        [status, filename, filesize] = mensaje.decode().split('|')
        log(f'Respuesta del servidor: {mensaje.decode()}')

        assert status == 'CONECTADO'
        assert filename == self.filename

        log('Continuamos en el upload')

        with open(f'{self.path+self.filename}', 'wb') as archivo:
            iters = ceil(int(filesize) / (self.socket.buffer_size - 8))

            ordenadorDePaquetes = OrdenadorDePaquetes(ceil(int(filesize) / (self.socket.buffer_size - 8)))

            while not ordenadorDePaquetes.is_full():
                log(f'Recibiendo... {ordenadorDePaquetes.blocks_occupied}/{ordenadorDePaquetes.blocks}')
                mensaje, address, seq_number = self.socket.receive()
                #fix para evitar escribir encabezado si fallaba en llegar el ack al servidor
                if mensaje and 'CONECTADO|' in mensaje.decode():
                    log('el cliente volvió a recibir CONECTADO\nenviando ACK')
                    import struct
                    ack_packet = struct.pack('II', seq_number, 0)
                    # send UDP puro
                    self.socket.socket.sendto(ack_packet, address)
                    continue
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

        log('Fin de la transmision del archivo')
        log('Comenzamos cierre de conexion')
        print('Fin del cliente')
