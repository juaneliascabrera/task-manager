import unittest
from src.task_manager import TaskManager

class TestTaskManager(unittest.TestCase):
    def setUp(self):
        self.generic_task_description = 'Leer capítulo 5 del libro Design Patterns'
    def test_can_add_task(self):
        manager = TaskManager()
        #Agregamos la tarea
        created_task_id = manager.add_task(self.generic_task_description)
        #Asserts
        self.assertEqual(manager.tasks_count(), 1, "Debe haber una tarea")
        self.assertTrue(manager.contains_task(created_task_id), "Debe estar exactamente esta tarea")

    def test_added_task_is_not_completed(self):
        manager = TaskManager()
        #Agregamos la tarea
        created_task_id = manager.add_task(self.generic_task_description)
        self.assertFalse(manager.is_completed(created_task_id))
if __name__ == '__main__':
    unittest.main()

