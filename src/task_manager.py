import sqlite3

class TaskErrorManager(Exception):
    pass

class TaskNotFoundError(TaskErrorManager):
    """Error. Tarea no existe."""
    def __init__(self, task_id):
        self.task_id = task_id
        super().__init__(f"Error. Tarea con ID '{task_id}' no encontrada.")
    
class Task:
    def __init__(self, id, description):
        self.id = id
        self.description = description
        self.completed = False
    
    def is_completed(self):
        return self.completed
    
class TaskManager:
    def __init__(self, db_name):
        #self.tasks = {}
        #self.next_id = 0
        #Creamos las base de datos
        self.conn = sqlite3.connect(db_name)
    
        #Configuramos el cursor
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

        #Inicializamos la tabla
        self._create_table()

    def _create_table(self):   
        "Creamos la tabla si no existe"
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS tareas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                descripcion TEXT NOT NULL,
                completada BOOLEAN NOT NULL DEFAULT 0
            )
        """)
        self.conn.commit()
    
    def close(self):
        self.conn.close()

    def add_task(self, description):

        sql = "INSERT INTO tareas (descripcion, completada) VALUES (?, ?)"
        try:
            self.cursor.execute(sql, (description, 0))
        except sqlite3.Error as e:
            #Handleamos
            print(f"Error al insertar la tarea {e}")
            raise
        #Guardamos los cambios
        self.conn.commit()
        #Handleamos el id
        generated_id = self.cursor.lastrowid

        return generated_id
    
    def get_pending_tasks(self):
        pending_tasks = []
        for task in self.tasks.values():
            if not task.is_completed():
                pending_tasks.append(task)
        return pending_tasks

    def complete_task(self, task_id):
        self.assert_is_valid_task_id(task_id)
        task = self.tasks.get(task_id)
        task.completed = True

    def contains_task(self, task_id):
        return task_id in self.tasks
    
    def is_completed(self, task_id):
        self.assert_is_valid_task_id(task_id)
        task = self.tasks.get(task_id)
        return task.is_completed()
    
    def tasks_count(self):
        #Contamos las tareas totales
        sql = "SELECT COUNT(*) FROM tareas"
        #Ejecutamos
        self.cursor.execute(sql)
        
        count = self.cursor.fetchone()[0]
        return count
    
    #Assert methods
    def assert_is_valid_task_id(self, task_id):
        if(task_id not in self.tasks):
            raise TaskNotFoundError(task_id)