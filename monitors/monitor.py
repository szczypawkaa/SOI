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
        self._iter_even = 0
        self._iter_odd = 1

    def _run(self, choosen_cond: Condition, action: callable, thread_id=5):
        self.enter()
        # print(f"{choosen_cond}: Wchodzę do monitora")
        if (not choosen_cond.can_do_action()):
            print(f"{choosen_cond}: zatrzymałem się")
            self.wait(choosen_cond)

        action()
        # action(element)
        print(f"{choosen_cond} {thread_id}: ", self._buffer)

        for cond in self._all_cond:
            if cond != choosen_cond and cond.waiting_count > 0 and cond.can_do_action():
                print(f"{cond}: ruszam ponownie")
                self.signal(cond)
        # print(f"{choosen_cond}: Wychodzę z monitora")
        self.leave()

    # def _prod_action(self, element):
    #     self._buffer.append(element)

    # def _cons_action(self, element):
    #     self._buffer.popleft()

    def _prod_even_action(self):
        self._buffer.append(self._iter_even)
        self._iter_even = (self._iter_even + 2) % 50

    def _prod_odd_action(self):
        self._buffer.append(self._iter_odd)
        self._iter_odd = (self._iter_odd + 2) % 50

    def _cons_action(self):
        self._buffer.popleft()

    def put_even(self, thread_id):
        self._run(self._prod_even_cond, self._prod_even_action, thread_id)

    def put_odd(self, thread_id):
        self._run(self._prod_odd_cond, self._prod_odd_action, thread_id)

    def get_even(self, thread_id):
        self._run(self._cons_even_cond, self._cons_action)

    def get_odd(self, thread_id):
        self._run(self._cons_odd_cond, self._cons_action)


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
        return len(self.monitor._buffer) >= 3 and self.monitor._buffer[0] % 2 == 0

    def __str__(self):
        return "B1"


class consOddCond(Condition):
    def can_do_action(self):
        return len(self.monitor._buffer) >= 7 and self.monitor._buffer[0] % 2 != 0

    def __str__(self):
        return "B2"

#########################Functions######################################


def prod_even_mod_50(monitor, thread_id):
    # i = 0
    while (1):
        monitor.put_even(thread_id)
        # i = (i + 2) % 50
        # print(f"A1 {thread_id}", monitor._buffer)
        time.sleep(1)


def prod_odd_mod_50(monitor, thread_id):
    # i = 1
    while (1):
        monitor.put_odd(thread_id)
        # i = (i + 2) % 50
        # print(f"A2 {thread_id}", monitor._buffer)
        time.sleep(1)


def cons_even(monitor, thread_id):
    while (1):
        monitor.get_even(thread_id)
        # print(f"B1 {thread_id}", monitor._buffer)
        time.sleep(1)


def cons_odd(monitor, thread_id):
    while (1):
        monitor.get_odd(thread_id)
        # print(f"B2 {thread_id}", monitor._buffer)
        time.sleep(1)


if __name__ == "__main__":
    monitor = MyMonitor()

    prod_a1_thread = threading.Thread(target=prod_even_mod_50, args=(monitor, 1))
    prod_a2_thread = threading.Thread(target=prod_odd_mod_50, args=(monitor, 1))
    cons_b1_thread = threading.Thread(target=cons_even, args=(monitor, 1))
    cons_b2_thread = threading.Thread(target=cons_odd, args=(monitor, 1))

    prod_a1_thread_v2 = threading.Thread(target=prod_even_mod_50, args=(monitor, 2))
    prod_a2_thread_v2 = threading.Thread(target=prod_odd_mod_50, args=(monitor, 2))
    cons_b1_thread_v2 = threading.Thread(target=cons_even, args=(monitor, 2))
    cons_b2_thread_v2 = threading.Thread(target=cons_odd, args=(monitor, 2))

    prod_a1_thread.start()
    prod_a1_thread_v2.start()
    prod_a2_thread.start()
    prod_a2_thread_v2.start()
    cons_b1_thread.start()
    cons_b1_thread_v2.start()
    cons_b2_thread.start()
    cons_b2_thread_v2.start()

    prod_a1_thread.join()
    prod_a1_thread_v2.join()
    prod_a2_thread.join()
    prod_a2_thread_v2.join()
    cons_b1_thread.join()
    cons_b1_thread_v2.join()
    cons_b2_thread.join()
    cons_b2_thread_v2.join()


#     # BUFFOR_MAX_LEN = 30
#     # buffer = deque([i for i in range(BUFFOR_MAX_LEN)], maxlen=BUFFOR_MAX_LEN)
