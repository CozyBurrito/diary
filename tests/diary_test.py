from diary import Diary, DiaryDB, Event
import unittest
import shutil
import os


# Helper methods
def exists_with_ext(path, ext):
    if os.path.exists(path):
        return ext == os.path.splitext(path)[1]
    return False


def create_dir(path):
    if not os.path.exists(path):
        os.mkdir(path)


class TestDiary(unittest.TestCase):
    INFO = "event was logged"
    DB_PATH = os.path.join('testing_dir', 'perm.db')
    TXT_PATH = os.path.join('testing_dir', 'log.txt')
    INIT_DIR = os.path.join('testing_dir', 'dir_for_init')
    BAD_PATH = os.path.join('testing_dir', 'BAD.FILE')
    NO_EXIST_PATH = os.path.join('testing_dir', 'new.txt')
    MALFORMED_PATH = 'D://^&'

    @classmethod
    def setUpClass(cls):
        create_dir('testing_dir')
        with open(cls.DB_PATH, 'w'):
            pass  # Create a db file
        with open(cls.TXT_PATH, 'w'):
            pass  # Create a text file
        with open(cls.BAD_PATH, 'w'):
            pass # Create a bad file
        create_dir(cls.INIT_DIR)

    @classmethod
    def tearDownClass(cls):
        os.remove(cls.NO_EXIST_PATH)
        shutil.rmtree(cls.INIT_DIR)

    def test_init_dir(self):
        log = Diary(self.INIT_DIR, async=False)
        self.assertTrue(exists_with_ext(os.path.join(
            self.INIT_DIR,
            'diary.txt'
            ), '.txt')
        )

        self.assertTrue(exists_with_ext(os.path.join(
            self.INIT_DIR,
            'diary.db'
            ), '.db')
        )

    def test_init_file(self):
        log = Diary(self.TXT_PATH, async=False)
        log.info(self.INFO)
        log.close()
        with open(self.TXT_PATH) as f:
            line = f.readline()
            self.assertTrue(self.INFO in line)

    def test_init_db(self):
        log = Diary(self.DB_PATH, async=False)
        log.info(self.INFO)
        log.close()
        with DiaryDB(self.DB_PATH) as db:
            db.assert_event_logged(self.INFO, level="INFO")

    def test_init_bad_ext(self):
        with self.assertRaises(ValueError,
            msg="Could not resolve to database or text file {}".format(
                self.BAD_PATH)):
            log = Diary(self.BAD_PATH, async=False)

    def test_init_does_not_exist(self):
        log = Diary(self.NO_EXIST_PATH, async=False)
        log.info(self.INFO)
        log.close()
        with open(self.NO_EXIST_PATH) as f:
            line = f.readline()
            self.assertTrue(self.INFO in line)

    def test_init_malformed_path(self):
        with self.assertRaises(Exception):
            log = Diary(self.MALFORMED_PATH)

    def test_write(self):
        FILE_NAME = "test_write.txt"
        log = Diary(self.INIT_DIR, async=False, file_name=FILE_NAME)
        simple_event = Event(self.INFO, "LEVEL")

        self.assertTrue(exists_with_ext(os.path.join(
            self.INIT_DIR,
            FILE_NAME
            ), '.txt')
        )

        log.write(simple_event)
        log.logdb.assert_event_logged(self.INFO, level="LEVEL")
        log.close()

        self.assertEquals(os.path.split(log.log_file.name)[-1], FILE_NAME)
        self.assertIs(log.last_logged_event, simple_event)

        with open(os.path.join(self.INIT_DIR, FILE_NAME)) as f:
            self.assertTrue(self.INFO in f.readline())

    def test_log(self):
        FILE_NAME = "test_log.txt"
        log = Diary(self.INIT_DIR, async=False, file_name=FILE_NAME)
        self.assertTrue(exists_with_ext(os.path.join(
            self.INIT_DIR,
            FILE_NAME
            ), '.txt')
        )

        log.log(self.INFO)
        log.logdb.assert_event_logged(self.INFO, level="INFO")
        log.close()

        self.assertEquals(os.path.split(log.log_file.name)[-1], FILE_NAME)

        with open(os.path.join(self.INIT_DIR, FILE_NAME)) as f:
            self.assertTrue(self.INFO in f.readline())

    def test_info(self):
        DB_NAME = 'levels.db'
        log = Diary(os.path.join(self.INIT_DIR), async=False, db_name=DB_NAME)
        log.info(self.INFO)
        log.logdb.assert_event_logged(self.INFO, "INFO", 1)
        log.close()

    def test_warn(self):
        DB_NAME = 'levels.db'
        log = Diary(os.path.join(self.INIT_DIR), async=False, db_name=DB_NAME)
        log.warn(self.INFO)
        log.logdb.assert_event_logged(self.INFO, "WARN", 1)
        log.close()

    def test_error(self):
        DB_NAME = 'levels.db'
        log = Diary(os.path.join(self.INIT_DIR), async=False, db_name=DB_NAME)
        log.error(self.INFO)
        log.logdb.assert_event_logged(self.INFO, "ERROR", 1)
        log.close()

    def test_debug(self):
        DB_NAME = 'levels.db'
        log = Diary(os.path.join(self.INIT_DIR), async=False, db_name=DB_NAME)
        log.debug(self.INFO)
        log.logdb.assert_event_logged(self.INFO, "DEBUG", 1)
        log.close()


if __name__ == '__main__':
    unittest.main()