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

    def put_even(self, element: int):
        self.enter()
        print("A1: wchodzędo monitora")
        print("A1: sprawdzam warunek", self._buffer)
        if (not self._prod_even_cond.can_do_action()):
            print("A1: zatrzymałem się")
            self.wait(self._prod_even_cond)
            print("A1: ruszam")

        self._buffer.append(element)
        print("A1: ", self._buffer)

        for cond in self._all_cond:
            if cond != self._prod_even_cond and cond.waiting_count > 0 and cond.can_do_action():
                print("A1: Inny spełnia warunek")
                self.signal(cond)
        print("A1: wychodzę z monitora")
        self.leave()

    def put_odd(self, element: int):
        self.enter()
        print("A2: Wchodzę do monitora")
        print("A2: sprawdzam warunek", self._buffer)
        if (not self._prod_odd_cond.can_do_action()):
            print("A2: zatrzymałem się")
            self.wait(self._prod_odd_cond)
            print("A2: ruszam")

        self._buffer.append(element)
        print("A2: ", self._buffer)

        for cond in self._all_cond:
            if cond != self._prod_even_cond and cond.waiting_count > 0 and cond.can_do_action():
                print("A2: Inny spełnia warunek")
                self.signal(cond)
        print("A2: wychodzę z monitora")
        self.leave()

    def get_all_even(self):
        pass

    def get_all_odd(self):
        pass


class prodEvenCond(Condition):

    def can_do_action(self):
        even_sum = sum(1 for x in self.monitor._buffer if x % 2 == 0)
        return even_sum < 10


class prodOddCond(Condition):

    def can_do_action(self):
        even_count = sum(1 for x in self.monitor._buffer if x % 2 == 0)
        odd_count = sum(1 for x in self.monitor._buffer if x % 2 != 0)
        return even_count > odd_count


class consEvenCond(Condition):
    pass


class consOddCond(Condition):
    pass


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


def cons_even():
    while (1):
        MyMonitor.get_all_even()
        time.sleep(1)


def cons_odd():
    while (1):
        MyMonitor.get_all_odd()
        time.sleep(1)


if __name__ == "__main__":
    monitor = MyMonitor()

    prod_a1_thread = threading.Thread(target=prod_even_mod_50, args=(monitor,))
    prod_a2_thread = threading.Thread(target=prod_odd_mod_50, args=(monitor,))

    prod_a1_thread.start()
    prod_a2_thread.start()

    prod_a1_thread.join()
    prod_a2_thread.join()


#     # BUFFOR_MAX_LEN = 30
#     # buffer = deque([i for i in range(BUFFOR_MAX_LEN)], maxlen=BUFFOR_MAX_LEN)
