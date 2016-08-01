import levels
import formats
import events

class Diary(object):
    """ Diary is a low-dependency and easy to use logger """

    def __init__(self, path, event=events.Event, format=formats.standard, async=False, debug=True):
        """
        Initialization takes a file path meant to make startup simple
        :param path: str of a path pointing to -
            * An empty directory where Diary will initiate
            * A txt file where Diary will write
            * A database file where Diary will read and write
            * A directory with a database and txt file
            * A nonexistent path for assumed writing
        :param format: function to format logging info (see formats.py)
        :param async: boolean if logging should occur in own thread
        :param debug: boolean if logger supports debugging
        """
        self.path = path
        self.event = event
        self.format = format
        self.async = async
        self.debug_enabled = debug
        if async:
            from logthread import ElemThread
            self.thread = ElemThread(self)

    def set_timer(self, interval, func, *args, **kwargs):
        """Set a timer to log an event at every interval"""
        if self.async is False:
            raise Exception("In order to set a timer async must be enabled")

        from RepeatedTimer import RepeatedTimer
        self.timer = RepeatedTimer(interval, func, *args, **kwargs)
        self.timer.start()

    def write(self, event):
        print(self.format(event))

    def log(self, info, level=levels.info):
        """Log info to its relevant level (see levels.py)

        :param info: info for logging
        :param level: @level decorated function handle relevant behavior
        """
        event_to_log = self.event(info, level)
        if self.async:
            level(event_to_log, self.thread.add)
        else:
            level(event_to_log, self.write)

    def info(self, info):
        """Log general info

        :param info: info relevant to application processes
        """
        self.log(info, level=levels.info)

    def warn(self, info):
        """Log info that requires a warning

        :param info: info relevant to a warning
        """
        self.log(info, level=levels.warn)

    def error(self, info):
        """Log info that may cause an error

        :param info: info relevant to an error
        """
        self.log(info, level=levels.error)

    def debug(self, info):
        """Log info that may only be helpful to the developer
        Will only log if debugging is enabled

        :param info: info for the devs
        """
        if self.debug_enabled:
            self.log(info, level=levels.debug)


if __name__ == '__main__':
    # from Diary import Diary
    el = Diary
    example_el = el("", format=formats.easy_read, async=True)
    example_el.log("hello")
    example_el.warn("oh no")
    example_el.error("NOOOOO")
    def p():
        print("thread")
    example_el.set_timer(1, p)
    from time import sleep
    sleep(2)
    print("should exit")
