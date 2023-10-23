import unittest
import os
from tasks import new_task, load_tasks, delete_task, update_status
from unittest.mock import patch


TEST_FILE_NAME = "tasks_test.json"


class TestTasks(unittest.TestCase):

    def setUp(self):
        if os.path.exists(TEST_FILE_NAME):
            os.remove(TEST_FILE_NAME)

    @patch('tasks.FILE_NAME', TEST_FILE_NAME)
    def test_new_task_creation(self):
        new_task("Test title", "This is a test desc.", ["test_tag"])

        tasks = load_tasks()

        self.assertEqual(len(tasks), 1)

        self.assertEqual(tasks[0].title, "Test title")
        self.assertEqual(tasks[0].desc, "This is a test desc.")
        self.assertEqual(tasks[0].tags, ["test_tag"])
        self.assertEqual(tasks[0].status, "todo")

    @patch('tasks.FILE_NAME', TEST_FILE_NAME)
    def test_task_deletion(self):
        new_task("Task to delete id 2", "desc.", ["tag_1"])
        tasks_before_deletion = load_tasks()
        self.assertEqual(len(tasks_before_deletion), 1)
        delete_task(1)
        tasks_after_deletion = load_tasks()
        self.assertEqual(len(tasks_after_deletion), 0)

    @patch('tasks.FILE_NAME', TEST_FILE_NAME)
    def test_update_task_status(self):
        new_task("Test update status", "desc.", ["tag_1"])

        tasks_before_update = load_tasks()
        self.assertEqual(len(tasks_before_update), 1)
        self.assertEqual(tasks_before_update[0].status, "todo")

        update_status(1, "start")

        tasks_after_update = load_tasks()
        self.assertEqual(len(tasks_after_update), 1)
        self.assertEqual(tasks_after_update[0].status, "in_progress")

    def tearDown(self):
        if os.path.exists(TEST_FILE_NAME):
            os.remove(TEST_FILE_NAME)


if __name__ == "__main__":
    unittest.main()
