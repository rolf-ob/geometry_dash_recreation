import time

class FpsCounter:
    def __init__(self):
        self.frame_times = []

    def tick(self):
        now = time.perf_counter()
        self.frame_times.append(now)
        cutoff = now - 1
        while self.frame_times and self.frame_times[0] < cutoff:
            self.frame_times.pop(0)

    def get_fps(self):
        return len(self.frame_times)