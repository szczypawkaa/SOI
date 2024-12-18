from __future__ import annotations
from semaphore import BinarySemaphore
from collections import deque
from abc import ABC, abstractmethod
import threading
import time


class Process(ABC):
    num_of_waiting = 0

    @classmethod
    def mutex_V(cls):
        cls.mutex.V()

    @classmethod
    def mutex_P(cls):
        # print(f"{cls.__name__}: Czekam")
        cls.mutex.P()

    @classmethod
    def get_num_of_waiting(cls):
        return cls.num_of_waiting

    @classmethod
    def increase_num_of_waiting(cls):
        cls.num_of_waiting += 1

    @classmethod
    def decrease_num_of_waiting(cls):
        cls.num_of_waiting -= 1

    @abstractmethod
    def condition(self):
        """Warunek uruchomienia"""
        pass

    @abstractmethod
    def action(self):
        pass


class ProdEvenModulo50(Process):
    i = 0
    mutex = BinarySemaphore(1)  # Semafor wspólny dla wszystkich instancji tej klasy

    def condition(self):
        even_count = sum(1 for x in buffer if x % 2 == 0)
        return even_count < 10

    def action(self):
        buffer.append(self.__class__.i)
        self.__class__.i += 2
        self.__class__.i %= 50

    def __str__(self):
        return 'A1'


class ProdOddModulo50(Process):
    i = 1
    mutex = BinarySemaphore(1)  # Semafor wspólny dla wszystkich instancji tej klasy

    def __init__(self):
        super().__init__()

    def condition(self):
        even_count = sum(1 for x in buffer if x % 2 == 0)
        odd_count = sum(1 for x in buffer if x % 2 != 0)
        return even_count > odd_count

    def action(self):
        buffer.append(self.__class__.i)
        self.__class__.i += 2
        self.__class__.i %= 50

    def __str__(self):
        return 'A2'


class ConsEven(Process):
    mutex = BinarySemaphore(1)  # Semafor wspólny dla wszystkich instancji tej klasy

    def condition(self):
        return len(buffer) >= 3

    def action(self):
        global buffer
        consumed_buffer = deque(x for x in buffer if x % 2 != 0)
        buffer = consumed_buffer

    def __str__(self):
        return 'B1'


class ConsOdd(Process):
    mutex = BinarySemaphore(1)  # Semafor wspólny dla wszystkich instancji tej klasy

    def condition(self):
        return len(buffer) >= 7

    def action(self):
        global buffer
        consumed_buffer = deque(x for x in buffer if x % 2 == 0)
        buffer = consumed_buffer

    def __str__(self):
        return 'B2'


def run(given_process: Process, all_processes):
    process: Process = given_process
    other_processes = [
        x for x in all_processes if x != given_process
    ]

    while True:
        mutex.P()
        if not process.condition():
            process.increase_num_of_waiting()
            print(f"{str(process)}: Zatrzymałem się, ponieważ nie spełniam warunku")
            mutex.V()
            process.mutex_P()
            print(f"{str(process)}: Ruszam dalej - już spełniam warunek")
            process.decrease_num_of_waiting()

        process.action()
        print(f"{str(process)}: Wykonane,", buffer)
        for other in other_processes:
            if other.get_num_of_waiting() > 0 and other.condition():
                other.mutex_V()
                break
        else:
            mutex.V()

        time.sleep(1)


if __name__ == "__main__":
    buffer = deque()
    mutex = BinarySemaphore(1)  # Główny semafor, używany w procesach

    prod_a1 = ProdEvenModulo50()
    prod_a1_v2 = ProdEvenModulo50()
    cons_b1 = ConsEven()
    cons_b1_v2 = ConsEven()
    prod_a2 = ProdOddModulo50()
    prod_a2_v2 = ProdOddModulo50()
    cons_b2 = ConsOdd()
    cons_b2_v2 = ConsOdd()

    all_processes = [
        prod_a1, prod_a1_v2, cons_b1, cons_b1_v2,
        prod_a2, prod_a2_v2, cons_b2, cons_b2_v2
    ]

    # Tworzenie i uruchamianie wątków
    prod_a1_thread = threading.Thread(target=run, args=(prod_a1, all_processes))
    prod_a1_thread_v2 = threading.Thread(target=run, args=(prod_a1_v2, all_processes))
    prod_a2_thread = threading.Thread(target=run, args=(prod_a2, all_processes))
    prod_a2_thread_v2 = threading.Thread(target=run, args=(prod_a2_v2, all_processes))
    cons_b1_thread = threading.Thread(target=run, args=(cons_b1, all_processes))
    cons_b1_thread_v2 = threading.Thread(target=run, args=(cons_b1_v2, all_processes))
    cons_b2_thread = threading.Thread(target=run, args=(cons_b2, all_processes))
    cons_b2_thread_v2 = threading.Thread(target=run, args=(cons_b2_v2, all_processes))

    # Startowanie wątków
    prod_a1_thread.start()
    prod_a1_thread_v2.start()
    cons_b1_thread.start()
    cons_b1_thread_v2.start()
    prod_a2_thread.start()
    prod_a2_thread_v2.start()
    cons_b2_thread.start()
    cons_b2_thread_v2.start()

    # Czekanie na zakończenie wątków
    prod_a1_thread.join()
    prod_a1_thread_v2.join()
    cons_b1_thread.join()
    cons_b1_thread_v2.join()
    prod_a2_thread.join()
    prod_a2_thread_v2.join()
    cons_b2_thread.join()
    cons_b2_thread_v2.join()
