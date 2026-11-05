import time

class FpsHandler:
    def __init__(self):
        self.frame_times = []

    def limit_fps(self, target_fps, last_frame_time):
        frame_duration = 1 / target_fps

        remaining = frame_duration - (time.perf_counter() - last_frame_time)
        if remaining > 0.001:
            time.sleep(remaining - 0.0005)
        
        while time.perf_counter() - last_frame_time < frame_duration:
            pass
        
        return time.perf_counter()

    def tick(self):
        now = time.perf_counter()
        self.frame_times.append(now)
        if len(self.frame_times) > 2:
            self.frame_times.pop(0)

    def get_fps(self):
        if len(self.frame_times) < 2: return 0
        return round(1 / (self.frame_times[1] - self.frame_times[0]))