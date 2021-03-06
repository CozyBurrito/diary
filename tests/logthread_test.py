from diary import Diary, DiaryDB
import unittest
import time
import os


class TestDiaryThread(unittest.TestCase):
    TEST_DIR_PATH = os.path.join(os.path.dirname(__file__),
                                 'testing_dir')
    INFO = "event was logged"
    TEMP_DB = os.path.join(TEST_DIR_PATH, "db_test.db")
    TEMP_FILE = os.path.join(TEST_DIR_PATH, "thread_test.txt")
    TRIALS = 3
    count = 0

    def setUp(self):
        self.log = Diary(self.TEST_DIR_PATH, file_name=self.TEMP_FILE,
                         db_name=self.TEMP_DB, async=True)

    def tearDown(self):
        self.log.close()
        os.remove(self.TEMP_FILE)

    @classmethod
    def tearDownClass(cls):
        os.remove(cls.TEMP_DB)

    def test_constructor(self):
        self.assertIsNotNone(self.log.thread)
        self.assertTrue(self.log.thread.isDaemon())
        self.assertTrue(self.log.thread.sets_db)
        self.assertIs(self.log.thread.diary, self.log)

    def test_join(self):
        returned = self.log.thread.join()
        self.assertIsNone(returned)

    def test_logs(self):
        self.log.log(self.INFO)
        self.log.close()

        with open(self.log.log_file.name) as f:
            self.assertTrue(self.INFO in f.readline())

        with DiaryDB(self.log.db_file.name) as db:
            db.assert_event_logged(self.INFO)

    def test_timer_no_async(self):
        log = Diary(self.TEST_DIR_PATH, async=False)
        with self.assertRaises(RuntimeError,
            msg="In order to set a timer async must be enabled"):
            log.set_timer(100, lambda: None)

    def test_timer(self):
        def log_counter():
            self.count += 1
            self.log.log(self.INFO + str(self.count))

        self.log.set_timer(1, log_counter)

        time.sleep(self.TRIALS + .1)

        self.log.close()

        with DiaryDB(self.log.db_file.name) as db:
            db.assert_event_logged(self.INFO + str(self.count))

        with open(self.log.log_file.name) as f:
            for i in range(1, self.TRIALS + 1):
                self.assertTrue(self.INFO + str(i) in f.readline())

    def test_timer_with_args(self):
        def log_arg(arg):
            self.log.log(arg)

        self.log.set_timer(1, log_arg, self.INFO)

        time.sleep(self.TRIALS + .1)

        self.log.close()

        with DiaryDB(self.log.db_file.name) as db:
            entries = db.cursor.execute(
                '''SELECT * FROM logs WHERE log=(?)
                AND level LIKE (?) ORDER BY
                inputDT ASC LIMIT (?)''',
                (self.INFO, '%', self.TRIALS))

            for i in range(self.TRIALS):
                self.assertTrue(entries.fetchone())

        with open(self.log.log_file.name) as f:
            self.assertTrue(self.INFO in f.readline())

    def test_timer_with_kwargs(self):
        repeats = 10

        def log_kwarg(s, repeats=2):
            self.log.log(s * repeats)

        self.log.set_timer(1, log_kwarg, self.INFO, repeats=repeats)

        time.sleep(self.TRIALS + .1)

        self.log.close()

        with DiaryDB(self.log.db_file.name) as db:
            entries = db.cursor.execute(
                '''SELECT * FROM logs WHERE log=(?)
                AND level LIKE (?) ORDER BY
                inputDT ASC LIMIT (?)''',
                (self.INFO * repeats, '%', self.TRIALS))

            for i in range(self.TRIALS):
                self.assertTrue(entries.fetchone())

        with open(self.log.log_file.name) as f:
            self.assertTrue(self.INFO * repeats in f.readline())

    def test_timer_all_args(self):
        params = (self.INFO, "abc", "def", "123")

        def log_joined(*args):
            self.log.log(' '.join(args))

        self.log.set_timer(1, log_joined, *params)

        time.sleep(self.TRIALS + .1)

        self.log.close()

        with DiaryDB(self.log.db_file.name) as db:
            entries = db.cursor.execute(
                '''SELECT * FROM logs WHERE log=(?)
                AND level LIKE (?) ORDER BY
                inputDT ASC LIMIT (?)''',
                (' '.join(params), '%', self.TRIALS))

            for i in range(self.TRIALS):
                self.assertTrue(entries.fetchone())

        with open(self.log.log_file.name) as f:
            self.assertTrue(' '.join(params) in f.readline())


if __name__ == '__main__':
    unittest.main()
