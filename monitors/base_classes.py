from abc import abstractmethod
from threading import Lock


class Semaphore:
    def __init__(self, initial_state=1):
        self._lock = Lock()
        if initial_state == 0:  # 1 - dostępny, 0 - zajęty
            self._lock.acquire()

    def P(self):
        self._lock.acquire()

    def V(self):
        self._lock.release()


class Condition:
    def __init__(self, monitor):
        self.monitor = monitor
        self._w = Semaphore(0)
        self.waiting_count = 0

    def wait(self):
        self._w.P()

    def signal(self):
        if self.waiting_count:
            self.waiting_count -= 1
            self._w.V()
            return True
        return False

    @abstractmethod
    def can_do_action(self):
        pass


class Monitor:
    def __init__(self):
        self._s = Semaphore(1)

    def enter(self):
        self._s.P()

    def leave(self):
        self._s.V()

    def wait(self, cond: Condition):
        cond.waiting_count += 1
        self.leave()
        cond.wait()

    def signal(self, cond: Condition):
        if (cond.signal()):
            self.enter()
