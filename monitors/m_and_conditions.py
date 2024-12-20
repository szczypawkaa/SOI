from __future__ import annotations
from base_classes import Monitor, Condition
from collections import deque


class MyMonitor(Monitor):
    BUFFOR_MAX_LEN = 30

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

    def set_buffer_as_full(self):
        self._buffer = deque(
            [i for i in range(MyMonitor.BUFFOR_MAX_LEN)],
            maxlen=MyMonitor.BUFFOR_MAX_LEN
            )

    def put_even(self, thread_id):
        self._run(self._prod_even_cond, self._prod_even_action, thread_id)

    def put_odd(self, thread_id):
        self._run(self._prod_odd_cond, self._prod_odd_action, thread_id)

    def get_even(self, thread_id):
        self._run(self._cons_even_cond, self._cons_action, thread_id)

    def get_odd(self, thread_id):
        self._run(self._cons_odd_cond, self._cons_action, thread_id)

    def _run(self, choosen_cond: Condition, action: callable, thread_id):
        self.enter()
        if (not choosen_cond.can_do_action()):
            print(f"{choosen_cond} {thread_id}: zatrzymałem się")
            self.wait(choosen_cond)
            print(f"{choosen_cond} {thread_id}: ruszam ponownie")

        action()
        print(f"{choosen_cond} {thread_id}: ", self._buffer)

        for cond in self._all_cond:
            if (
                cond != choosen_cond
                and cond.waiting_count > 0
                and cond.can_do_action()
            ):
                self.signal(cond)
        self.leave()

    def _prod_even_action(self):
        self._buffer.append(self._iter_even)
        self._iter_even = (self._iter_even + 2) % 50

    def _prod_odd_action(self):
        self._buffer.append(self._iter_odd)
        self._iter_odd = (self._iter_odd + 2) % 50

    def _cons_action(self):
        self._buffer.popleft()


class prodEvenCond(Condition):

    def can_do_action(self):
        if len(self.monitor._buffer) >= MyMonitor.BUFFOR_MAX_LEN:
            return False
        even_sum = sum(1 for x in self.monitor._buffer if x % 2 == 0)
        return even_sum < 10

    def __str__(self):
        return "A1"


class prodOddCond(Condition):

    def can_do_action(self):
        if len(self.monitor._buffer) >= MyMonitor.BUFFOR_MAX_LEN:
            return False
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
