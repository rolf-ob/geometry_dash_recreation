import time

class FpsCounter:
    def __init__(self):
        self.frame_times = []

    def tick(self):
        now = time.perf_counter()
        self.frame_times.append(now)
        if len(self.frame_times) > 2:
            self.frame_times.pop(0)

    def get_fps(self):
        return round(1 / (self.frame_times[1] - self.frame_times[0]))