# SuperFastPython.com
# example of a thread-safe list
from threading import Thread
from threading import Lock

import signal


# custom class wrapping a list in order to make it thread safe
class OrdenadorDePaquetes():

    # constructor
    def __init__(self, blocks):
        # initialize the list
        self._list = list()
        # initialize the lock
        self._lock = Lock()
        self.blocks = blocks
        self.blocks_occupied = 0

        for i in range(blocks):
            self._list.append(None)

    # add a value to the list
    def add(self, id, value):
        # acquire the lock
        with self._lock:
            # append the value
            if not self._list[id]:
                self._list[id] = value
                self.blocks_occupied += 1

    # remove and return the last value from the list
    def pop(self):
        # acquire the lock
        with self._lock:
            # pop a value from the list
            # self.blocks_occupied -= 1
            return self._list.pop()

    # read a value from the list at an index
    def get(self, index):
        # acquire the lock
        with self._lock:
            # read a value at the index
            return self._list[index]

    # return the number of items in the list
    def length(self):
        # acquire the lock
        with self._lock:
            return len(self._list)

    def is_full(self):
        return self.blocks_occupied == self.blocks

    def is_empty(self):
        return self.blocks_occupied == 0


# add items to the list
def add_items(lista):
    for i in range(10000):
        lista.add(i,i)
        print("SCOTLAND FOREVER:",i)


def remove_items(lista):
    for i in range(10000):
        lista.get(i)
        print("Hacemos un pop:", i)


''' 
# create the thread safe list
safe_list = OrdenadorDePaquetes(10000)
# configure threads to add to the list
thread1 = Thread(target=add_items, args=(safe_list,))
thread2 = Thread(target=remove_items, args=(safe_list,))
# start threads

thread1.start()
thread2.start()
# wait for all threads to terminate
print('Main waiting for threads...')
thread1.join()
thread2.join()

# report the number of items in the list
print(f'List size: {safe_list.length()}')
'''
