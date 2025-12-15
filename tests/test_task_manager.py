import unittest
import os
from src.task_manager import TaskManager, TaskNotFoundError, Task, AuthenticationError
from src.task_repository import TaskRepository
from src.clock_implementations import MockClock
from datetime import datetime, timedelta
class TestTaskManager(unittest.TestCase):
    DB_TEST_NAME = 'test_tasks.db'
    def setUp(self):
        #Creamos el repository
        self.mock_clock = MockClock(datetime(2025, 12, 14, 17, 00, 00))
        self.repository = TaskRepository(self.DB_TEST_NAME, self.mock_clock, True)
        #Creamos el task manager
        self.manager = TaskManager(self.repository)
        #Tareas genéricas
        self.generic_task_description_one = 'Leer capítulo 5 del libro Design Patterns'
        self.generic_task_description_two = 'Hacer ejercicio 5 minutos'
        self.generic_task_description_three = 'Correr 1 hora'
        #Usuarios
        self.generic_user_one = "jelias1203"
        self.generic_user_two = "martin195"
        #Creación
        #Creamos 2 usuarios
        self.user_id_one = self.manager.add_user(self.generic_user_one)
        self.user_id_two = self.manager.add_user(self.generic_user_two)
    
    def tearDown(self):
        self.repository.close()

    # 🚨 NUEVO MÉTODO: Ejecutado UNA VEZ al final de TODA la clase
    @classmethod
    def tearDownClass(cls):
        """Borra el archivo de base de datos después de todos los tests."""
        # Se asegura de que el archivo exista antes de intentar borrarlo
        if os.path.exists(cls.DB_TEST_NAME):
            os.remove(cls.DB_TEST_NAME)
    
    def test_can_list_only_pending_tasks(self):
        #Agregamos 3 tareas
        task_id_one = self.manager.add_task_by_user_id_global(self.generic_task_description_one, user_id=self.user_id_one)
        task_id_two = self.manager.add_task_by_user_id_global(self.generic_task_description_two, user_id=self.user_id_two)
        task_id_three = self.manager.add_task_by_user_id_global(self.generic_task_description_three, user_id=self.user_id_two)
        #Marcamos la segunda tarea como completada para ver si es excluida
        self.manager.complete_task_global(task_id_two)
        #Conseguimos las listas de las tareas pendientes
        pending_tasks_user_one = self.manager.get_pending_tasks_by_user_id_global(self.user_id_one)
        pending_tasks_user_two = self.manager.get_pending_tasks_by_user_id_global(self.user_id_two)
        #Vemos que tengan longitud correcta
        self.assertEqual(len(pending_tasks_user_one), 1, "The user one should have one pending task")
        self.assertEqual(len(pending_tasks_user_two), 1, "The user two should have one pending task")
        #Vemos que estén exactamente las tareas correctas
        for taskOne, taskTwo in zip(pending_tasks_user_one, pending_tasks_user_two):
            self.assertFalse(taskOne.is_completed(), "Todas las tareas están sin completar")
            self.assertFalse(taskTwo.is_completed(), "Todas las tareas están sin completar")
        

    def test_added_task_is_not_completed(self):
        #Agregamos la tarea
        created_task_id = self.manager.add_task_by_user_id_global(self.generic_task_description_one, user_id=self.user_id_one)
        #Asserts
        self.assertFalse(self.manager.task_is_completed(created_task_id))

    def test_can_mark_task_as_completed(self):
        #Agregamos la tarea
        created_task_id = self.manager.add_task_by_user_id_global(self.generic_task_description_one, user_id=self.user_id_one)
        self.manager.complete_task_global(created_task_id)
        #Asserts
        self.assertTrue(self.manager.task_is_completed(created_task_id))

    def test_mark_invalid_task_id_as_completed_raises_error(self):
        non_existent_id = 10
        #Asserts
        with self.assertRaises(TaskNotFoundError):
            self.manager.complete_task_global(non_existent_id)

    def test_check_is_completed_invalid_task_id_raises_error(self):
        non_existent_id = 10
        #Asserts
        with self.assertRaises(TaskNotFoundError):
            self.manager.task_is_completed(non_existent_id)

    def test_can_delete_added_task(self):
        #Agregamos una tarea
        created_task_id_one = self.manager.add_task_by_user_id_global(self.generic_task_description_one, user_id=self.user_id_one)
        created_task_id_two = self.manager.add_task_by_user_id_global(self.generic_task_description_two, user_id=self.user_id_one)
        #La borramos (por ejemplo, me equivoqué en la descripción)
        self.manager.delete_task_global(created_task_id_one)
        #Asertamos que no esté la tarea
        self.assertEqual(self.manager.tasks_count_by_user_id(self.user_id_one), 1, "Sólo debería haber una tarea")
        self.assertFalse(self.manager.contains_task_by_user_id(self.user_id_one, created_task_id_one), "En particular, esta tarea no debería estar")

    def test_can_not_delete_invalid_task(self):
        non_existent_id = 59151951        
        #Intentamos borrarla
        with self.assertRaises(TaskNotFoundError):
            self.manager.delete_task_global(non_existent_id)

    def test_can_get_task_by_id(self):
        #Agregamos la tarea
        created_task_id = self.manager.add_task_by_user_id_global(self.generic_task_description_one, user_id=self.user_id_one)
        #La conseguimos mediante id
        task = self.manager.get_task_by_id_global(created_task_id)
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
            self.manager.get_task_by_id_global(non_existent_id)

    def test_can_create_task_with_due_date(self):
        #Creamos la fecha
        due_date = datetime(2025, 12, 31, 23, 59, 59)
        #Creamos la tarea
        created_task_id = self.manager.add_task_by_user_id_global(self.generic_task_description_one, self.user_id_one, due_date)
        #Recuperamos la tarea
        task = self.manager.get_task_by_id_global(created_task_id)
        #Asertamos
        self.assertEqual(task.get_due_date(), due_date, "Deberían tener la misma fecha")
    
    def test_can_list_overdue_tasks(self):
        #Creamos una tarea que venza en hoy+3dias
        due_date_onetwo = self.mock_clock.now() + timedelta(days=3)
        due_date_three = self.mock_clock.now() + timedelta(days=10)
        created_task_id_one = self.manager.add_task_by_user_id_global(self.generic_task_description_one, self.user_id_one, due_date_onetwo)
        created_task_id_two = self.manager.add_task_by_user_id_global(self.generic_task_description_two, self.user_id_one, due_date_onetwo)
        created_task_id_three = self.manager.add_task_by_user_id_global(self.generic_task_description_three, self.user_id_one, due_date_three)
        #Avanzamos 4 días 
        self.mock_clock.advance_time(days=4)
        #Tendríamos que obtener las dos tareas vencidas
        overdue_tasks = self.manager.get_overdue_tasks_by_user_id_global(self.user_id_one)
        #Asertamos
        expected_ids = {created_task_id_one, created_task_id_two}
        actual_ids = {task.get_id() for task in overdue_tasks}
        self.assertEqual(len(overdue_tasks), 2, "Deberíamos tener 2 tareas vencidas")
        self.assertEqual(expected_ids, actual_ids)
        self.assertFalse(overdue_tasks[0].is_completed())
        self.assertFalse(overdue_tasks[1].is_completed())
        self.assertFalse(created_task_id_three in actual_ids)
        
    def test_can_update_task_due_date(self):
        #Creamos el due_date
        due_date = self.mock_clock.now() + timedelta(days=3)
        #Supongamos que ahora queremos cambiar a la siguiente fecha
        new_due_date = due_date + timedelta(days = 1)
        #Id
        created_task_id = self.manager.add_task_by_user_id_global(self.generic_task_description_one, self.user_id_one, due_date)
        #Modificamos la fecha
        self.manager.update_task_due_date_global(created_task_id, new_due_date)
        #Asertamos
        task = self.manager.get_task_by_id_global(created_task_id)
        self.assertEqual(task.get_due_date(), new_due_date, "Debería haberse actualizado la fecha")
        
    def test_can_not_update_task_due_date_by_invalid_id(self):
        #Invalid id
        non_existent_id = 10591
        #Creamos una tarea
        due_date = self.mock_clock.now() + timedelta(days = 3)
        created_task_id = self.manager.add_task_by_user_id_global(self.generic_task_description_one, self.user_id_one, due_date)
        #Intentamos modificar una tarea que no existe
        with self.assertRaises(TaskNotFoundError):
            self.manager.update_task_due_date_global(non_existent_id, due_date+timedelta(days=1))
    def test_can_update_task_description(self):
        #Id
        created_task_id = self.manager.add_task_by_user_id_global(self.generic_task_description_one, self.user_id_one)
        #Modificamos la fecha
        self.manager.update_task_description_global(created_task_id, self.generic_task_description_two)
        #Asertamos
        task = self.manager.get_task_by_id_global(created_task_id)
        self.assertEqual(task.get_description(), self.generic_task_description_two, "Debería haberse actualizado la descripción")
    def test_can_not_update_task_description_by_invalid_id(self):
        #Invalid id
        non_existent_id = 10591
        #Creamos la tarea
        created_task_id = self.manager.add_task_by_user_id_global(self.generic_task_description_one, self.user_id_one)
        #Intentamos modificar una tarea que no existe
        with self.assertRaises(TaskNotFoundError):
            self.manager.update_task_description_global(non_existent_id, self.generic_task_description_three)
        
    def test_can_remove_due_date(self):
        #Creamos el due_date
        due_date = self.mock_clock.now() + timedelta(days=3)
        #Id
        created_task_id = self.manager.add_task_by_user_id_global(self.generic_task_description_one, self.user_id_one, due_date)
        #Borramos la fecha
        self.manager.remove_task_due_date_global(created_task_id)
        #Asertamos
        task = self.manager.get_task_by_id_global(created_task_id)
        self.assertTrue(task.get_due_date() is None, "Debería haberse borrado la fecha")
        
    def test_can_not_remove_due_date_by_invalid_id(self):
        #Invalid id
        non_existent_id = 10591
        #Creamos la tarea
        created_task_id = self.manager.add_task_by_user_id_global(self.generic_task_description_one, self.user_id_one)
        #Intentamos modificar una tarea que no existe
        with self.assertRaises(TaskNotFoundError):
            self.manager.remove_task_due_date_global(non_existent_id)
    
    def test_completed_overdue_task_does_not_appear_in_overdue_tasks(self):
        #Creamos una tarea que venza en hoy+3dias
        due_date_onetwo = self.mock_clock.now() + timedelta(days=3)
        due_date_three = self.mock_clock.now() + timedelta(days=10)
        created_task_id_one = self.manager.add_task_by_user_id_global(self.generic_task_description_one, self.user_id_one, due_date_onetwo)
        created_task_id_two = self.manager.add_task_by_user_id_global(self.generic_task_description_two, self.user_id_one, due_date_onetwo)
        self.manager.add_task_by_user_id_global(self.generic_task_description_three, self.user_id_one, due_date_three)
        #Avanzamos 4 días 
        self.mock_clock.advance_time(days=4)
        #Completamos las tareas vencidas
        self.manager.complete_task_global(created_task_id_one)
        self.manager.complete_task_global(created_task_id_two)
        #No deberíamos obtener nada
        overdue_tasks = self.manager.get_overdue_tasks_by_user_id_global(self.user_id_one)
        #Asertamos
        self.assertFalse(overdue_tasks, "La lista debería estar vacía")

        """User tests"""
    def test_can_add_user(self):
        #Asserts
        self.assertEqual(self.manager.users_count(), 2, "Debería haber 2 usuario")
        self.assertTrue(self.manager.contains_user(self.user_id_one), "Debería ser estos usuarios")
        self.assertTrue(self.manager.contains_user(self.user_id_two), "Debería ser estos usuarios")
        
    def test_can_add_task_for_user_one(self):
        #Add task
        due_date = self.mock_clock.now() + timedelta(days=3)
        created_task_id = self.manager.add_task_by_user_id_global(self.generic_task_description_one, self.user_id_one, due_date)
        #Asserts
        self.assertEqual(self.manager.tasks_count_by_user_id(self.user_id_one), 1, "Debe haber una tarea")
        self.assertTrue(self.manager.contains_task_by_user_id(self.user_id_one, created_task_id), "Debe estar exactamente esta tarea")

    """def test_can_not_mark_other_user_task_as_completed(self):
        #Agregamos la tarea del usuario
        created_task_id = self.manager.add_task_by_user_id(self.generic_task_description_one, user_id=self.user_id_one)
        #Asserts (el usuario 2 no debería poder)
        with self.assertRaises(AuthenticationError):
            self.manager.user_wants_to_complete_task(self.user_id_two, created_task_id)
        #No debería estar marcada como completada
        self.assertFalse(self.manager.task_is_completed(created_task_id))

    def test_can_not_delete_other_user_task(self):
        #Agregamos la tarea del usuario
        created_task_id = self.manager.add_task_by_user_id(self.generic_task_description_one, user_id=self.user_id_one)
        #Asserts (el usuario 2 no debería poder)
        with self.assertRaises(AuthenticationError):
            self.manager.user_wants_to_delete_task(self.user_id_two, created_task_id)
        #No debería estar marcada como eliminada.
        self.assertTrue(self.manager.contains_task_by_user_id(self.user_id_one, created_task_id))"""
        
if __name__ == '__main__':
    unittest.main()

