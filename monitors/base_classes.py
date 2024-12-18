from abc import abstractmethod


class Semaphore:
    def __init__(self, state=1):
        self._state = state

    def P(self):
        while self._state <= 0:
            pass
        self._state -= 1

    def V(self):
        self._state += 1


class Condition:
    def __init__(self):
        self._w = Semaphore(0)
        self.waiting_count = 0

    def wait(self):
        self._w.P()

    def signal(self):
        if self.waiting_count:
            self.waiting_count -= 1
            self._w.V()
            return True
        else:
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
        cond._waiting_count += 1
        self.leave()
        cond.wait()

    def signal(self, cond: Condition):
        if (cond.signal()):
            self.enter()