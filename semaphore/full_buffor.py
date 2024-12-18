from __future__ import annotations
from semaphore import BinarySemaphore
from collections import deque
from abc import ABC, abstractmethod
import threading
import time


class Process(ABC):
    def __init__(self):
        self.mutex = BinarySemaphore(0)
        self._num_of_waiting = 0

    def mutex_V(self):
        self.mutex.V()

    def mutex_P(self):
        self.mutex.P()

    def num_of_waiting(self):
        return self._num_of_waiting

    def increase_num_of_waiting(self):
        self._num_of_waiting += 1

    def decrease_num_of_waiting(self):
        self._num_of_waiting -= 1

    @abstractmethod
    def condition(self):
        """Warunek uruchomienia"""
        pass

    @abstractmethod
    def action(self):
        pass


class ProdEvenModulo50(Process):
    def __init__(self):
        super().__init__()
        self._i = 0

    def condition(self):
        if len(buffer) >= BUFFOR_MAX_LEN:
            return False
        even_count = sum(1 for x in buffer if x % 2 == 0)
        return even_count < 10

    def action(self):
        buffer.append(self._i)
        self._i += 2
        self._i %= 50

    def __str__(self):
        return 'A1'


class ProdOddModulo50(Process):
    def __init__(self):
        super().__init__()
        self._i = 1

    def condition(self):
        if len(buffer) >= BUFFOR_MAX_LEN:
            return False
        even_count = sum(1 for x in buffer if x % 2 == 0)
        odd_count = sum(1 for x in buffer if x % 2 != 0)
        return even_count > odd_count

    def action(self):
        buffer.append(self._i)
        self._i += 2
        self._i %= 50

    def __str__(self):
        return 'A2'


class ConsEven(Process):
    def condition(self):
        return len(buffer) >= 3

    def action(self):
        global buffer
        consumed_buffer = deque(x for x in buffer if x % 2 != 0)
        buffer = consumed_buffer

    def __str__(self):
        return 'B1'


class ConsOdd(Process):
    def condition(self):
        return len(buffer) >= 7

    def action(self):
        global buffer
        consumed_buffer = deque(x for x in buffer if x % 2 == 0)
        buffer = consumed_buffer

    def __str__(self):
        return 'B2'


def run(given_process: Process, all_processes, thread_id: int):
    process: Process = given_process
    other_processes = [
        x for x in all_processes if x != given_process
    ]

    while True:
        mutex.P()
        # print(f"{str(process)} {thread_id}: Wchodzę do main mutex,", buffer, f"Mutex state: {mutex._state}")
        # print(f"{str(process)} {thread_id}: Wchodzę do main mutex,", buffer)
        if not process.condition():
            process.increase_num_of_waiting()
            mutex.V()
            print(f"{str(process)} {thread_id}: Zatrzymałem się, ponieważ nie spełniam warunku")
            # print(f"{str(process)} {thread_id}: Zwalniam main mutex, Mutex state: {mutex._state}")
            process.mutex_P()
            # print(f"{str(process)} {thread_id}: Ruszam dalej - już spełniam warunek, Mutex state: {mutex._state}")
            print(f"{str(process)} {thread_id}: Ruszam dalej - już spełniam warunek")
            process.decrease_num_of_waiting()

        process.action()
        print(f"{str(process)} {thread_id}: Wykonane,", buffer)

        for other in other_processes:
            if other.num_of_waiting() > 0 and other.condition():
                other.mutex_V()
                # print(f"Ruszam: Mutex state: {mutex._state}")
                # print(f"{str(process)} {thread_id}: Zostałem wybudzony")
                break
        else:
            mutex.V()
            # print(f"{str(process)} {thread_id}: Wychodzę z main mutex, Mutex state: {mutex._state}")
        time.sleep(3)


if __name__ == "__main__":
    BUFFOR_MAX_LEN = 30
    buffer = deque([i for i in range(BUFFOR_MAX_LEN)], maxlen=BUFFOR_MAX_LEN)
    # buffer = deque()
    mutex = BinarySemaphore(1)

    prod_a1 = ProdEvenModulo50()
    cons_b1 = ConsEven()
    prod_a2 = ProdOddModulo50()
    cons_b2 = ConsOdd()

    all = [prod_a1, cons_b1, prod_a2, cons_b2]

    prod_a1_thread = threading.Thread(target=run, args=(prod_a1, all, 1))
    prod_a1_thread_v2 = threading.Thread(target=run, args=(prod_a1, all, 2))
    prod_a2_thread = threading.Thread(target=run, args=(prod_a2, all, 1))
    prod_a2_thread_v2 = threading.Thread(target=run, args=(prod_a2, all, 2))
    cons_b1_thread = threading.Thread(target=run, args=(cons_b1, all, 1))
    cons_b1_thread_v2 = threading.Thread(target=run, args=(cons_b1, all, 2))
    cons_b2_thread = threading.Thread(target=run, args=(cons_b2, all, 1))
    cons_b2_thread_v2 = threading.Thread(target=run, args=(cons_b2, all, 2))

    prod_a1_thread.start()
    prod_a1_thread_v2.start()
    cons_b1_thread.start()
    cons_b1_thread_v2.start()
    prod_a2_thread.start()
    prod_a2_thread_v2.start()
    cons_b2_thread.start()
    cons_b2_thread_v2.start()

    prod_a1_thread.join()
    prod_a1_thread_v2.join()
    cons_b1_thread.join()
    cons_b1_thread_v2.join()
    prod_a2_thread.join()
    prod_a2_thread_v2.join()
    cons_b2_thread.join()
    cons_b2_thread_v2.join()


    prod_a1 = ProdEvenModulo50()
    cons_b1 = ConsEven()
    prod_a2 = ProdOddModulo50()
    cons_b2 = ConsOdd()

    all = [prod_a1, cons_b1, prod_a2, cons_b2]

    prod_a1_thread = threading.Thread(target=run, args=(prod_a1, all, 1))
    prod_a2_thread = threading.Thread(target=run, args=(prod_a2, all, 1))
    cons_b1_thread = threading.Thread(target=run, args=(cons_b1, all, 1))
    cons_b2_thread = threading.Thread(target=run, args=(cons_b2, all, 1))

    prod_a1_thread.start()
    cons_b1_thread.start()
    prod_a2_thread.start()
    cons_b2_thread.start()

    prod_a1_thread.join()
    cons_b1_thread.join()
    prod_a2_thread.join()
    cons_b2_thread.join()