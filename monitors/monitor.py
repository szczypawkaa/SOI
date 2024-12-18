from base_classes import Monitor, Semaphore, Condition
from collections import deque
import threading
import time


class MyMonitor(Monitor):
    def __init__(self):
        super().__init__()
        self._buffer = deque()
        self._prod_even_cond = prodEvenCond()
        # self._prod_odd_cond = prodOddCond()
        # self._cons_even_cond = consEvenCond()
        # self._cons_odd_cond = consOddCond()
        # self._all_cond: list[Condition] = [
        #     self._prod_even_cond,
        #     self._prod_odd_cond,
        #     self._cons_even_cond,
        #     self._cons_odd_cond
        # ]

    def put_even(self, element: int):
        self.enter()
        if (not self._prod_even_cond.can_do_action(self._buffer)):
            self._prod_even_cond.waiting_count += 1
            self._prod_even_cond.wait()
            self._prod_even_cond.waiting_count -= 1

        self._buffer.append(element)
        print("Buffor: ", self._buffer)
        # for cond in self._all_cond:
        #     if (cond.waiting_count > 0 and cond.can_do_action(self._buffer)):
        #         cond.signal()

        self.leave()

    def put_odd(self, element: int):
        pass

    def get_all_even(self):
        pass

    def get_all_odd(self):
        pass


class prodEvenCond(Condition):
    def can_do_action(self, buffer):
        return sum(1 for x in buffer if x % 2 == 0) < 10


class prodOddCond(Condition):
    pass


class consEvenCond(Condition):
    pass


class consOddCond(Condition):
    pass

#########################Functions######################################


def prod_even_mod_50():
    i = 0
    while (1):
        monitor.put_even(i)
        i = (i + 2) % 50
        time.sleep(1)


def prod_odd_mod_50():
    i = 1
    while (1):
        MyMonitor.put_odd(i)
        i = (i + 2) % 50
        time.sleep(1)


def cons_even():
    while (1):
        MyMonitor.get_all_even()
        time.sleep(1)


def cons_odd():
    while (1):
        MyMonitor.get_all_odd()
        time.sleep(1)


if __name__ == "__main__":
    # BUFFOR_MAX_LEN = 30
    # buffer = deque([i for i in range(BUFFOR_MAX_LEN)], maxlen=BUFFOR_MAX_LEN)

    monitor = MyMonitor()

    prod_a1_thread = threading.Thread(target=prod_even_mod_50)
    prod_a2_thread = threading.Thread(target=run, args=(prod_a2, all, 1))
    # cons_b1_thread = threading.Thread(target=run, args=(cons_b1, all, 1))
    # cons_b2_thread = threading.Thread(target=run, args=(cons_b2, all, 1))

    prod_a1_thread.start()
    # cons_b1_thread.start()
    # prod_a2_thread.start()
    # cons_b2_thread.start()

    prod_a1_thread.join()
    # cons_b1_thread.join()
    # prod_a2_thread.join()
    # cons_b2_thread.join()
