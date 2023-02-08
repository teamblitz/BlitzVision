import time


class TimeManager:
    _time_delta_ns: int = -1
    _time_delta_set: bool = False

    def set_robot_time(self, robot_time_microseconds):
        self._time_delta_ns = robot_time_microseconds * 1000 - time.perf_counter_ns()
        self._time_delta_set = True

    def get_timestamp(self):
        return int((self._time_delta_ns + time.perf_counter_ns()) / 1000)
