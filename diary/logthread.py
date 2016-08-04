from threading import Thread

try:
    from queue import Queue
except ImportError:  # python 2
    from Queue import Queue


class DiaryThread(Thread):
    """A thread for logging as to not disrupt the logged application"""

    def __init__(self, diary, sets_db=False, name="Diary Logger"):
        """Construct a thread for logging

        :param diary: An Diary instance to handle logging
        :param sets_db: determine if self.run should call self.diary.set_db
        :param name: A string to represent this thread
        """
        Thread.__init__(self, name=name)
        self.daemon = True  # py2 constructor requires explicit
        self.diary = diary
        self.sets_db = sets_db
        self.queue = Queue()
        self.start()


    def add(self, event):
        """Add a logged event to queue for logging"""
        self.queue.put(event)

    def run(self):
        """Main for thread to run"""
        if self.sets_db:
            self.diary.set_db()
        while True:
            self.diary.write(self.queue.get())
