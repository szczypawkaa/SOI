from base_classes import Monitor, Condition
from collections import deque
import threading
import time


class MyMonitor(Monitor):
    def __init__(self):
        super().__init__()
        self._buffer = deque()
        self._prod_even_cond = prodEvenCond(self)
        self._prod_odd_cond = prodOddCond(self)
        self._cons_even_cond = consEvenCond(self)
        self._cons_odd_cond = consOddCond(self)
        self._all_cond: list[Condition] = [
            self._prod_even_cond,
            self._prod_odd_cond,
            self._cons_even_cond,
            self._cons_odd_cond
        ]

    def _run(self, choosen_cond: Condition, action: callable, element=None):
        self.enter()
        print(f"{choosen_cond}: Wchodzę do monitora")
        if (not choosen_cond.can_do_action()):
            print(f"{choosen_cond}: zatrzymałem się")
            self.wait(choosen_cond)

        action(element)
        print(f"{choosen_cond}: ", self._buffer)

        for cond in self._all_cond:
            if cond != choosen_cond and cond.waiting_count > 0 and cond.can_do_action():
                print(f"{cond}: ruszam ponownie")
                self.signal(cond)
        print(f"{choosen_cond}: Wychodzę z monitora")
        self.leave()

    def _prod_action(self, element):
        self._buffer.append(element)

    def _cons_even_action(self, element):
        if self._buffer[-1] % 2 == 0:
            self._buffer.pop()

    def _cons_odd_action(self, element):
        if self._buffer[-1] % 2 != 0:
            self._buffer.pop()

    def put_even(self, element: int):
        self._run(self._prod_even_cond, self._prod_action, element)

    def put_odd(self, element: int):
        self._run(self._prod_odd_cond, self._prod_action, element)

    def get_even(self):
        self._run(self._cons_even_cond, self._cons_even_action)

    def get_odd(self):
        self._run(self._cons_odd_cond, self._cons_odd_action)


class prodEvenCond(Condition):

    def can_do_action(self):
        even_sum = sum(1 for x in self.monitor._buffer if x % 2 == 0)
        return even_sum < 10

    def __str__(self):
        return "A1"


class prodOddCond(Condition):

    def can_do_action(self):
        even_count = sum(1 for x in self.monitor._buffer if x % 2 == 0)
        odd_count = sum(1 for x in self.monitor._buffer if x % 2 != 0)
        return even_count > odd_count

    def __str__(self):
        return "A2"


class consEvenCond(Condition):
    def can_do_action(self):
        return len(self.monitor._buffer) >= 3

    def __str__(self):
        return "B1"


class consOddCond(Condition):
    def can_do_action(self):
        return len(self.monitor._buffer) >= 7

    def __str__(self):
        return "B2"

#########################Functions######################################


def prod_even_mod_50(monitor):
    i = 0
    while (1):
        monitor.put_even(i)
        i = (i + 2) % 50
        time.sleep(1)


def prod_odd_mod_50(monitor):
    i = 1
    while (1):
        monitor.put_odd(i)
        i = (i + 2) % 50
        time.sleep(1)


def cons_even(monitor):
    while (1):
        monitor.get_even()
        time.sleep(1)


def cons_odd(monitor):
    while (1):
        monitor.get_odd()
        time.sleep(1)


if __name__ == "__main__":
    monitor = MyMonitor()

    prod_a1_thread = threading.Thread(target=prod_even_mod_50, args=(monitor,))
    prod_a2_thread = threading.Thread(target=prod_odd_mod_50, args=(monitor,))
    cons_b1_thread = threading.Thread(target=cons_even, args=(monitor,))
    cons_b2_thread = threading.Thread(target=cons_odd, args=(monitor,))

    prod_a1_thread.start()
    prod_a2_thread.start()
    cons_b1_thread.start()
    cons_b2_thread.start()

    prod_a1_thread.join()
    prod_a2_thread.join()
    cons_b1_thread.join()
    cons_b2_thread.join()


#     # BUFFOR_MAX_LEN = 30
#     # buffer = deque([i for i in range(BUFFOR_MAX_LEN)], maxlen=BUFFOR_MAX_LEN)
