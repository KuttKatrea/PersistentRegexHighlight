import threading
import time
from datetime import datetime, timedelta
#import sublime

class Timer(object):
    def __init__(self):
        self.function = None
        self.time_ = None

        self.thread_ = None
        self.event_ = threading.Event()

    def schedule(self, timeout, function):
        self.function_ = function

        self.time_ = datetime.now() + timedelta(milliseconds=timeout)

        if self.thread_ is None or not self.thread_.is_alive():
            self.thread_ = threading.Thread(target=self.worker_)
            self.thread_.start()
        else:
            self.event_.set()

    def worker_(self):
        tid = threading.current_thread().name
        #print("[%s] Worker start" % tid)
        while True:
            #print("[%s] Check" % tid)
            now = datetime.now()
            if now >= self.time_:
                print("[%s] Running" % tid)
                self.function_()
                print("[%s] Run complete" % tid)
                now = datetime.now()

            if now < self.time_:
                timeout = (self.time_ - now) / timedelta(seconds=1)
                #print("[%s] Waiting %s s" % (tid, timeout))
                time.sleep(timeout)
            else:
                #print("[%s] Waiting event" % tid)
                self.event_.wait(10)
                if not self.event_.is_set():
                    break
                self.event_.clear()

        #print("[%s] Worker completed" % tid)

    def run_async_(self):
        now = datetime.now()
        if now >= self.time_:
            self.function_()

