from my_monitor import MyMonitor
import threading
import time


def prod_even(monitor, thread_id):
    while (1):
        monitor.put_even(thread_id)
        time.sleep(1)


def prod_odd(monitor, thread_id):
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


def create_and_start_threads(monitor, thread_configs):
    threads = []
    for func, thread_id in thread_configs:
        thread = threading.Thread(target=func, args=(monitor, thread_id))
        thread.start()
        threads.append(thread)
    return threads


if __name__ == "__main__":
    monitor = MyMonitor()
    monitor.set_buffer_as_full()
    print("Buffer: ", monitor.buffer())

    thread_configs = [
        (prod_even, 1), (prod_even, 2),
        (cons_even, 1), (cons_even, 2),
        (prod_odd, 1), (prod_odd, 2),
        (cons_odd, 1), (cons_odd, 2),
    ]

    threads = create_and_start_threads(monitor, thread_configs)

    for thread in threads:
        thread.join()

