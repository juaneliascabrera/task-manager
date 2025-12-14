import unittest
from src.task_manager import TaskManager, TaskNotFoundError

class TestTaskManager(unittest.TestCase):
    def setUp(self):
        #Creamos el task manager
        self.manager = TaskManager(db_name='test_tasks.db')
        #Tareas genéricas
        self.generic_task_description_one = 'Leer capítulo 5 del libro Design Patterns'
        self.generic_task_description_two = 'Hacer ejercicio 5 minutos'
        self.generic_task_description_three = 'Correr 1 hora'
        #Limpiamos
        self.manager.cursor.execute("DELETE FROM tareas")
        self.manager.conn.commit()
    
    def tearDown(self):
        self.manager.close()

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
        self.assertFalse(self.manager.is_completed(created_task_id))

    def test_can_mark_task_as_completed(self):
        
        #Agregamos la tarea
        created_task_id = self.manager.add_task(self.generic_task_description_one)
        self.manager.complete_task(created_task_id)
        #Asserts
        self.assertTrue(self.manager.is_completed(created_task_id))

    def test_mark_invalid_task_id_as_completed_raises_error(self):
        
        non_existent_id = 10
        #Asserts
        with self.assertRaises(TaskNotFoundError):
            self.manager.complete_task(non_existent_id)

    def test_check_is_completed_invalid_task_id_raises_error(self):
        
        non_existent_id = 10
        #Asserts
        with self.assertRaises(TaskNotFoundError):
            self.manager.is_completed(non_existent_id)

if __name__ == '__main__':
    unittest.main()

