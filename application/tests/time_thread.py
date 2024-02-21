import threading
import time


class TimerThread(threading.Thread):
    def __init__(self, max_time):
        super(TimerThread, self).__init__()
        self._stop_event = threading.Event()
        self.elapsed_time = 1
        self.max_time = max_time
        self.test_passed = False

    def stop(self):
        self._stop_event.set()
        print(f"Time stopped at {self.elapsed_time} seconds")

    def run(self):
        while not self._stop_event.is_set() and self.elapsed_time != self.max_time:
            time.sleep(1)
            self.elapsed_time += 1

        self.test_passed = True
