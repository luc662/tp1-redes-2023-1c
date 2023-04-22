# This is a sample Python script.

# Press Mayús+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import threading
import queue
from threading import Lock
import logging


class ManejadorDeVentanas:

    def __init__(self, cantidad_de_ventanas, pila_respuestas):
        self._pilas_respuestas = pila_respuestas
        self.respuestas_escuchadas = 0
        self._lock = Lock()
        self._cantidad_de_ventanas_maxima = cantidad_de_ventanas
        self._cantidad_de_ventanas_abiertas = 0
        self.ventanas = [(False, None)] * cantidad_de_ventanas

    def agregar_ventana(self, index, ventana):
        self.ventanas[index] = (False, ventana)
        self._cantidad_de_ventanas_abiertas += 1

    def pushear_a_ventana(self, index, valor, pila_respuestas):
        (se_envio, ventana) = self.ventanas[index]
        if not se_envio and ventana:
            with self._lock:
                logging.debug(f'(VENTANAS) _____MANEJADOR DE VENTANAS {index}')
                pila_respuestas.put("agrego un valor a la pila" + str(index))
                self.respuestas_escuchadas += 1
                self.ventanas[index] = (True, ventana)
                ventana.put(valor)
                logging.debug(f'(VENTANAS) _____Salgo de MANEJADOR DE VENTANAS {index}')

    def cerrar_ventana(self, index):
        (esta_abierta, ventana) = self.ventanas[index]
        if ventana and esta_abierta:
            self.ventanas[index] = (False, ventana)

    def finalizo(self):
        return self.respuestas_escuchadas == self._cantidad_de_ventanas_maxima

'''
# esto simula a los threads que se quedan escuchando a una pila hasta que se libere
def envio_bloque(pila, numero):
    # envio paquete
    intentos = 0
    while intentos < 3:
        try:
            # espero que llegue el paquete y que haya ack al manejador
            valor = pila.get(block=True, timeout=0.1)
            # mando mensaje a la ventana principal
            print("escucho desde la pila numero :", numero, " el valor:", valor)
        except queue.Empty:
            print("timout en la pila :", numero)
            intentos += 1
            # reintenar llamar al manejador y re-iterar


# esta parte simula la llegada de acks a la estructura

def enviar_acks(manejador_de_ventanas):
    for i in range(100):
        index_ventana = i % 10
        manejador_de_ventanas.pushear_a_ventana(index_ventana, i)


if __name__ == '__main__':

    threads = []
    my_queue_respuestas = queue.Queue()
    manejador_de_ventanas = manejador_de_ventanas(10, my_queue_respuestas)
    for i in range(10):
        my_queue = queue.Queue()
        manejador_de_ventanas.agregar_ventana(i, my_queue)
        thread = threading.Thread(target=envio_bloque, args=(my_queue, i))
        threads.append(thread)
        thread.start()
    thread_que_escucha_acks_y_envia_a_pila = threading.Thread(target=enviar_acks, args=(manejador_de_ventanas,))
    threads.append(thread_que_escucha_acks_y_envia_a_pila)
    thread_que_escucha_acks_y_envia_a_pila.start()

    # el thread principal maneja cuantas ventanas abren y si se libera una ventana,
    # la cierra y abre la siguiente disponible
    while True:
        try:
            valor = my_queue_respuestas.get(block=True, timeout=0.1)
            print("mensaje de respuesta :", valor)
            # if valor == 'FIN' #condicion de no envio mas mensajes
            #    break
        # esto no pasa nunca
        except queue.Empty:
            print("timout en la pila principal")
            break

    for t in threads:
        t.join()
'''