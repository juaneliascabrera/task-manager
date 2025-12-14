import unittest
from src.task_manager import TaskManager

class TestTaskManager(unittest.TestCase):
    def setUp(self):
        self.manager = TaskManager()

    def test_can_add_task(self):
        #Definimos un nombre para la tarea
        task_name = 'Leer capítulo 5 del libro Design Patterns'
        #Agregamos la tarea
        self.manager.add_task(task_name)
        #Conseguimos todas las tareas actuales
        pending_tasks = self.manager.get_tasks()
        #Asserts
        self.assertEqual(len(pending_tasks), 1, "Debe haber una tarea")
        self.assertEqual(pending_tasks[0], task_name, "Debe estar exactamente esta tarea")

if __name__ == '__main__':
    unittest.main()

