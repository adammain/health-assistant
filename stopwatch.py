import time


class Timer:

    def __init__(self, func=time.perf_counter):
        self.elapsed = 0.0
        self._func = func
        self._start = None
        # self._started_with = started_with

    def start(self, started_with):
        if self._start is not None:
            raise RuntimeError('Already started')
        if started_with is not None:
            self.elapsed = 0.0
            self.started_with = started_with
            self.start_time = self._func()
            self._start = self._func() - started_with
            started_with = None
        else:
            self._start = self._func()

    def stop(self):
        if self._start is None:
            raise RuntimeError('Not started')
        end = self._func()
        self.elapsed += end - self._start
        self._start = None

    def reset(self):
        self.elapsed = 0.0

    @property
    def running(self):
        return self._start is not None

    @property
    def runningElapsed(self):
        if self._start is None:
            raise RuntimeError('Not running')
        end = self._func()
        self.currentElapsed = end - self._start + self.elapsed
        return self.currentElapsed

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *args):
        self.stop()
