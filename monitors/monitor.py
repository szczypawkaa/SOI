from m_and_conditions import MyMonitor
import threading
import time


def prod_even_mod_50(monitor, thread_id):
    while (1):
        monitor.put_even(thread_id)
        time.sleep(1)


def prod_odd_mod_50(monitor, thread_id):
    while (1):
        monitor.put_odd(thread_id)
        time.sleep(1)


def cons_even(monitor, thread_id):
    while (1):
        monitor.get_even(thread_id)
        time.sleep(1)


def cons_odd(monitor, thread_id):
    while (1):
        monitor.get_odd(thread_id)
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

    monitor.register_thread(prod_a1_thread, 1)
    monitor.register_thread(prod_a2_thread, 2)

    prod_a1_thread.start()
    prod_a1_thread_v2.start()
    prod_a2_thread.start()
    prod_a2_thread_v2.start()
    cons_b1_thread.start()
    cons_b1_thread_v2.start()
    cons_b2_thread.start()
    cons_b2_thread_v2.start()

    prod_a1_thread.join()
    # prod_a1_thread_v2.join()
    # prod_a2_thread.join()
    # prod_a2_thread_v2.join()
    # cons_b1_thread.join()
    # cons_b1_thread_v2.join()
    # cons_b2_thread.join()
    # cons_b2_thread_v2.join()

