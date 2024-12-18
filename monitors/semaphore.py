
class BinarySemaphore:
    def __init__(self, state=1):
        self._state = state  # 1 - dostępny, 0 - zajęty

    def P(self):
        while self._state == 0:
            pass
        self._state = 0

    def V(self):
        self._state = 1
