from semaphore import BinarySemaphore
from collections import deque
import threading
import time


def can_prod_even_mod_50():
    even_count = sum(1 for x in buffer if x % 2 == 0)
    return even_count < 10


def can_prod_odd_mod_50():
    even_count = sum(1 for x in buffer if x % 2 == 0)
    odd_count = sum(1 for x in buffer if x % 2 != 0)
    return even_count > odd_count


def can_cons_even():
    return len(buffer) >= 3


def can_cons_odd():
    return len(buffer) >= 7


def prod_even_mod_50(name, id):
    i = 0
    while (1):
        mutex.P()
        print(f"{name} {id}: Wchodzę do main mutex,", buffer, f"Mutex state: {mutex._state}")
        if not can_prod_even_mod_50():
            global num_of_prod_even_mod_50_waiting
            num_of_prod_even_mod_50_waiting += 1
            mutex.V()
            print(f"{name} {id}: Zatrzymałem się, ponieważ nie spełniam warunku")
            print(f"{name} {id}: Zwalniam main mutex, Mutex state: {mutex._state}")
            prod_even_mod_50_mutex.P()
            print(f"{name} {id}: Ruszam dalej - już spełniam warunek, Mutex state: {mutex._state}")
            num_of_prod_even_mod_50_waiting -= 1

        buffer.append(i)
        i += 2
        i = i % 50

        print(f"{name} {id} Wykonane ,", buffer)

        if num_of_prod_odd_mod_50_waiting > 0 and can_prod_odd_mod_50():
            prod_odd_mod_50_mutex.V()
        elif num_of_cons_even_waiting > 0 and can_cons_even():
            cons_even_mutex.V()
        elif num_of_cons_odd_waiting > 0 and can_cons_odd():
            cons_odd_mutex.V()
        else:
            print(f"{name} {id}: Zwalniam main mutex, Mutex state: {mutex._state}")
            mutex.V()
            print(f"{name} {id}: Zwalniam main mutex, Mutex state: {mutex._state}")
        time.sleep(3)


def prod_odd_mod_50(name, id):
    i = 1
    while (1):
        mutex.P()
        print(f"{name} {id}: Wchodzę do main mutex,", buffer, f"Mutex state: {mutex._state}")
        if not can_prod_odd_mod_50():
            global num_of_prod_odd_mod_50_waiting
            num_of_prod_odd_mod_50_waiting += 1
            mutex.V()
            print(f"{name} {id}: Zatrzymałem się, ponieważ nie spełniam warunku")
            print(f"{name} {id}: Zwalniam main mutex, Mutex state: {mutex._state}")
            prod_odd_mod_50_mutex.P()
            print(f"{name} {id}: Ruszam dalej - już spełniam warunek, Mutex state: {mutex._state}")
            num_of_prod_odd_mod_50_waiting -= 1

        # production/consumption:
        buffer.append(i)
        i += 2
        i = i % 50
        print(f"{name} {id} Wykonane ,", buffer)

        if num_of_cons_even_waiting > 0 and can_cons_even():
            cons_even_mutex.V()
        elif num_of_cons_odd_waiting > 0 and can_cons_odd():
            cons_odd_mutex.V()
        elif num_of_prod_even_mod_50_waiting > 0 and can_prod_even_mod_50():
            prod_even_mod_50_mutex.V()
        else:
            print(f"{name} {id}: Zwalniam main mutex, Mutex state: {mutex._state}")
            mutex.V()
            print(f"{name} {id}: Zwalniam main mutex, Mutex state: {mutex._state}")
        time.sleep(3)


def cons_even(name, id):
    global buffer
    while (1):
        mutex.P()
        print(f"{name} {id}: Wchodzę do main mutex,", buffer, f"Mutex state: {mutex._state}")
        if not can_cons_even():
            global num_of_cons_even_waiting
            num_of_cons_even_waiting += 1
            mutex.V()
            print(f"{name} {id}: Zatrzymałem się, ponieważ nie spełniam warunku")
            print(f"{name} {id}: Zwalniam main mutex, Mutex state: {mutex._state}")
            cons_even_mutex.P()
            print(f"{name} {id}: Ruszam dalej - już spełniam warunek, Mutex state: {mutex._state}")
            num_of_cons_even_waiting -= 1

        consumed_buffer = deque(x for x in buffer if x % 2 != 0)
        buffer = consumed_buffer
        print(f"{name} {id} Wykonane ,", buffer)

        if num_of_prod_even_mod_50_waiting > 0 and can_prod_even_mod_50():
            prod_even_mod_50_mutex.V()
        elif num_of_prod_odd_mod_50_waiting > 0 and can_prod_odd_mod_50():
            prod_odd_mod_50_mutex.V()
        elif num_of_cons_odd_waiting > 0 and can_cons_odd():
            cons_odd_mutex.V()
        else:
            print(f"{name} {id}: Zwalniam main mutex, Mutex state: {mutex._state}")
            mutex.V()
            print(f"{name} {id}: Zwalniam main mutex, Mutex state: {mutex._state}")
        time.sleep(3)


def cons_odd(name, id):
    global buffer
    while (1):
        mutex.P()
        print(f"{name} {id}: Wchodzę do main mutex,", buffer, f"Mutex state: {mutex._state}")
        if not can_cons_even():
            global num_of_cons_even_waiting
            num_of_cons_even_waiting += 1
            mutex.V()
            cons_even_mutex.P()
            print(f"{name} {id}: Zatrzymałem się, ponieważ nie spełniam warunku, Mutex state: {mutex._state}")
            num_of_cons_even_waiting -= 1

        consumed_buffer = deque(x for x in buffer if x % 2 == 0)
        buffer = consumed_buffer
        print(f"{name} {id} Wykonane ,", buffer)

        if num_of_prod_even_mod_50_waiting > 0 and can_prod_even_mod_50():
            prod_even_mod_50_mutex.V()
        elif num_of_prod_odd_mod_50_waiting > 0 and can_prod_odd_mod_50():
            prod_odd_mod_50_mutex.V()
        elif num_of_cons_even_waiting > 0 and can_cons_even():
            cons_even_mutex.V()
        else:
            print(f"{name} {id}: Zwalniam main mutex, Mutex state: {mutex._state}")
            mutex.V()
            print(f"{name} {id}: Zwalniam main mutex, Mutex state: {mutex._state}")
        time.sleep(3)

# def run(given_p, all_processes)
#     process = given_process
#     other_processes = [
#         x for x in all_processes if x != given_process
#     ]


if __name__ == "__main__":
    buffer = deque()  # Dodano początkowe wartości
    mutex = BinarySemaphore(1)

    prod_odd_mod_50_mutex = BinarySemaphore(0)
    prod_even_mod_50_mutex = BinarySemaphore(0)
    cons_even_mutex = BinarySemaphore(0)
    cons_odd_mutex = BinarySemaphore(0)

    num_of_prod_even_mod_50_waiting = 0
    num_of_prod_odd_mod_50_waiting = 0
    num_of_cons_even_waiting = 0
    num_of_cons_odd_waiting = 0

    # Podniesienie semaforów na start
    # prod_even_mod_50_mutex.V()
    # prod_odd_mod_50_mutex.V()
    # cons_even_mutex.V()
    # cons_odd_mutex.V()

    prod_a1_thread = threading.Thread(target=prod_even_mod_50, args=("A1", 1))
    prod_a1_thread_v2 = threading.Thread(target=prod_even_mod_50, args=("A1", 2))
    prod_a2_thread = threading.Thread(target=prod_odd_mod_50, args=("A2", 1))
    prod_a2_thread_v2 = threading.Thread(target=prod_odd_mod_50, args=("A2", 2))
    cons_b1_thread = threading.Thread(target=cons_even, args=("B1", 1))
    cons_b1_thread_v2 = threading.Thread(target=cons_even, args=("B1", 2))
    cons_b2_thread = threading.Thread(target=cons_odd, args=("B2", 1))
    cons_b2_thread_v2 = threading.Thread(target=cons_odd, args=("B2", 2))

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
