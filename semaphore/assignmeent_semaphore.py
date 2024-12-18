from semaphore import BinarySemaphore
from collections import deque
import threading


buffer = deque
mutex = BinarySemaphore(1)
prod_odd_mod_50_mutex = BinarySemaphore(0)
prod_even_mod_50_mutex = BinarySemaphore(0)
cons_even_mutex = BinarySemaphore(0)
cons_odd_mutex = BinarySemaphore(0)

num_of_prod_even_mod_50_waiting = 0
num_of_prod_odd_mod_50_waiting = 0
num_of_cons_even_waiting = 0
num_of_cons_odd_waiting = 0


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


def prod_even_mod_50():
    while (1):
        mutex.P()
        if not can_prod_even_mod_50():
            global num_of_prod_even_mod_50_waiting
            num_of_prod_even_mod_50_waiting += 1
            mutex.V()
            prod_even_mod_50_mutex.P()
            num_of_prod_even_mod_50_waiting -= 1

        #element produce()
        # buffer.append(element)

        if num_of_prod_odd_mod_50_waiting > 0 and can_prod_odd_mod_50():
            prod_odd_mod_50_mutex.V()
        elif num_of_cons_even_waiting > 0 and can_cons_even():
            cons_even_mutex.V()
        elif num_of_cons_odd_waiting > 0 and can_cons_odd():
            cons_odd_mutex.V()
        else:
            mutex.V()


def prod_odd_mod_50():
    i = 1
    while (1):
        mutex.P()
        if not can_prod_odd_mod_50():
            global num_of_prod_odd_mod_50_waiting
            num_of_prod_odd_mod_50_waiting += 1
            mutex.V()
            prod_odd_mod_50_mutex.P()
            num_of_prod_odd_mod_50_waiting -= 1

        # production/consumption:
        buffer.append(i)
        i += 2
        i = i % 50

        if num_of_cons_even_waiting > 0 and can_cons_even():
            cons_even_mutex.V()
        elif num_of_cons_odd_waiting > 0 and can_cons_odd():
            cons_odd_mutex.V()
        elif num_of_prod_even_mod_50_waiting > 0 and can_prod_even_mod_50():
            prod_even_mod_50_mutex.V()
        else:
            mutex.V()

# cond_mutex = [
#     prod_even_mod_50_mutex,
#     prod_odd_mod_50_mutex,
#     cons_even_mutex,
#     cons_odd_mutex
# ]

# conditions = [
#     can_prod_even_mod_50,
#     can_prod_odd_mod_50,
#     can_cons_even,
#     can_cons_odd
#     ]
# waiting_list = [
#     num_of_prod_even_mod_50_waiting,
#     num_of_prod_odd_mod_50_waiting,
#     num_of_cons_even_waiting,
#     num_of_cons_odd_waiting
#     ]

# def check_other_conditions(condition):
#     for wait, cond, mut in zip(waiting_list, conditions, cond_mutex):
#         if wait > 0 and cond != condition and cond:
#             mut.V()

# def run_function(condition, production)


def cons_even():
    while (1):
        mutex.P()
        if not can_cons_even():
            global num_of_cons_even_waiting
            num_of_cons_even_waiting += 1
            mutex.V()
            cons_even_mutex.P()
            num_of_cons_even_waiting -= 1

        #elemment produce()
        # buffer.append(element)

        elif num_of_cons_odd_waiting > 0 and can_cons_odd():
            cons_odd_mutex.V()
        elif num_of_prod_even_mod_50_waiting > 0 and can_prod_even_mod_50():
            prod_even_mod_50_mutex.V()
        if num_of_prod_odd_mod_50_waiting > 0 and can_prod_odd_mod_50():
            prod_odd_mod_50_mutex.V()
        else:
            mutex.V()



if __name__ == "__main__":
    pass