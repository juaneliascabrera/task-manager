import unittest
import os
from src.task_manager import TaskManager, TaskNotFoundError, Task
from src.task_repository import TaskRepository
class TestTaskManager(unittest.TestCase):
    DB_TEST_NAME = 'test_tasks.db'
    def setUp(self):
        #Creamos el repository
        self.repository = TaskRepository(self.DB_TEST_NAME)
        #Creamos el task manager
        self.manager = TaskManager(self.repository)
        #Tareas genéricas
        self.generic_task_description_one = 'Leer capítulo 5 del libro Design Patterns'
        self.generic_task_description_two = 'Hacer ejercicio 5 minutos'
        self.generic_task_description_three = 'Correr 1 hora'
        #Limpiamos
        self.repository.cursor.execute("DELETE FROM tasks")
        self.repository.conn.commit()
    
    def tearDown(self):
        self.repository.close()

    # 🚨 NUEVO MÉTODO: Ejecutado UNA VEZ al final de TODA la clase
    @classmethod
    def tearDownClass(cls):
        """Borra el archivo de base de datos después de todos los tests."""
        # Se asegura de que el archivo exista antes de intentar borrarlo
        if os.path.exists(cls.DB_TEST_NAME):
            os.remove(cls.DB_TEST_NAME)

    def test_can_add_task(self):
        #Agregamos la tarea
        created_task_id = self.manager.add_task(self.generic_task_description_one)
        #Asserts
        self.assertEqual(self.manager.tasks_count(), 1, "Debe haber una tarea")
        self.assertTrue(self.manager.contains_task(created_task_id), "Debe estar exactamente esta tarea")

    def test_can_list_only_pending_tasks(self):
        #Agregamos 3 tareas
        task_id_one = self.manager.add_task(self.generic_task_description_one)
        task_id_two = self.manager.add_task(self.generic_task_description_two)
        task_id_three = self.manager.add_task(self.generic_task_description_three)
        #Marcamos la segunda tarea como completada para ver si es excluida
        self.manager.complete_task(task_id_two)
        #Conseguimos las listas de las tareas pendientes
        pending_tasks = self.manager.get_pending_tasks()
        #Vemos que tenga longitud 2
        self.assertEqual(len(pending_tasks), 2, "Debe haber exactamente 2 tareas pendientes")
        #Vemos que estén exactamente las tareas correctas
        for task in pending_tasks:
            self.assertFalse(task.is_completed(), "Todas las tareas están sin completar")
        

    def test_added_task_is_not_completed(self):
        #Agregamos la tarea
        created_task_id = self.manager.add_task(self.generic_task_description_one)
        #Asserts
        self.assertFalse(self.manager.task_is_completed(created_task_id))

    def test_can_mark_task_as_completed(self):
        #Agregamos la tarea
        created_task_id = self.manager.add_task(self.generic_task_description_one)
        self.manager.complete_task(created_task_id)
        #Asserts
        self.assertTrue(self.manager.task_is_completed(created_task_id))

    def test_mark_invalid_task_id_as_completed_raises_error(self):
        non_existent_id = 10
        #Asserts
        with self.assertRaises(TaskNotFoundError):
            self.manager.complete_task(non_existent_id)

    def test_check_is_completed_invalid_task_id_raises_error(self):
        non_existent_id = 10
        #Asserts
        with self.assertRaises(TaskNotFoundError):
            self.manager.task_is_completed(non_existent_id)

    def test_can_delete_added_task(self):
        #Agregamos una tarea
        created_task_id_one = self.manager.add_task(self.generic_task_description_one)
        created_task_id_two = self.manager.add_task(self.generic_task_description_two)
        #La borramos (por ejemplo, me equivoqué en la descripción)
        self.manager.delete_task(created_task_id_one)
        #Asertamos que no esté la tarea
        self.assertEqual(self.manager.tasks_count(), 1, "Sólo debería haber una tarea")
        self.assertFalse(self.manager.contains_task(created_task_id_one), "En particular, esta tarea no debería estar")

    def test_can_not_delete_invalid_task(self):
        non_existent_id = 59151951        
        #Intentamos borrarla
        with self.assertRaises(TaskNotFoundError):
            self.manager.delete_task(non_existent_id)

    def test_can_get_task_by_id(self):
        #Agregamos la tarea
        created_task_id = self.manager.add_task(self.generic_task_description_one)
        #La conseguimos mediante id
        task = self.manager.get_task_by_id(created_task_id)
        #Asertamos que sea una instancia de Task
        self.assertIsInstance(task, Task, "El objeto task debería tener clase Task")
        #Asertamos que tenga los valores adecuados
        self.assertFalse(task.is_completed(), "La tarea no debería estar completada")
        self.assertEqual(task.get_description(), self.generic_task_description_one, "La tarea debería tener la primera descripción genérica")
        self.assertEqual(task.get_id(), created_task_id, "El id obtenido debería ser el que nos devolvió el add_task")

    def test_can_not_get_task_by_invalid_id(self):
        non_existent_id = 19519
        #Intentamos conseguirla
        with self.assertRaises(TaskNotFoundError):
            self.manager.get_task_by_id(non_existent_id)

if __name__ == '__main__':
    unittest.main()

