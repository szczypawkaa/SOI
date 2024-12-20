from threading import Lock


class BinarySemaphore:
    def __init__(self, initial_state=1):
        self._lock = Lock()
        if initial_state == 0:  # 1 - dostępny, 0 - zajęty
            self._lock.acquire()

    def P(self):
        self._lock.acquire()

    def V(self):
        self._lock.release()
