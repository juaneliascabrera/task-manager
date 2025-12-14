import sqlite3

class TaskErrorManager(Exception):
    pass

class TaskNotFoundError(TaskErrorManager):
    """Error. Tarea no existe."""
    def __init__(self, task_id):
        self.task_id = task_id
        super().__init__(f"Error. Tarea con ID '{task_id}' no encontrada.")
    
class Task:
    def __init__(self, id, description, completed=False):
        self.id = id
        self.description = description
        self.completed = False
    
    def is_completed(self):
        return self.completed
    
    def get_description(self):
        return self.description

    def get_id(self):
        return self.id
    
class TaskManager:
    TABLE_NAME = 'tasks'
    def __init__(self, db_name):
        #Creamos las base de datos
        self.conn = sqlite3.connect(db_name)
    
        #Configuramos el cursor
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

        #Inicializamos la tabla
        self._create_table()

    def _create_table(self):   
        "Creamos la tabla si no existe"
        self.cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {self.TABLE_NAME} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT NOT NULL,
                completed BOOLEAN NOT NULL DEFAULT 0
            )
        """)
        self.conn.commit()
    
    def close(self):
        self.conn.close()

    def add_task(self, description):

        sql = f"INSERT INTO {self.TABLE_NAME} (description, completed) VALUES (?, ?)"
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
    
    def delete_task(self, task_id):
        self.assert_is_valid_task_id(task_id)
        sql = f"DELETE FROM {self.TABLE_NAME} WHERE id = ?"
        self.cursor.execute(sql, (task_id,))
        #Guardamos los cambios
        self.conn.commit()

    def get_task_by_id(self, task_id):
        self.assert_is_valid_task_id(task_id)
        sql = f"SELECT id, description, completed FROM {self.TABLE_NAME} WHERE id = ?"
        #Ejecutamos
        self.cursor.execute(sql, (task_id,))
        #Fetcheamos el resultado obtenido
        fetched_task = self.cursor.fetchone()
        #Construimos el objeto tarea a partir de esto
        task = Task(
            id=fetched_task['id'],
            description=fetched_task['description'],
            completed = (fetched_task['completed'] == 1)
        )
        return task

    def get_pending_tasks(self):
        pending_tasks = []
        sql = f"SELECT id, description, completed FROM {self.TABLE_NAME} WHERE completed = 0"
        #Ejecutamos
        self.cursor.execute(sql)
        #Conseguimos todos los resultados
        rows = self.cursor.fetchall()
        for row in rows:
            #Recordemos que usamos Row
            task = Task(
                id=row['id'],
                description=row['description'],
                #Convertimos el 0/1 a True/False
                completed=(row['completed'] == 1)
            )
            pending_tasks.append(task)

        return pending_tasks
    def complete_task(self, task_id):
        self.assert_is_valid_task_id(task_id)

        sql = f"UPDATE {self.TABLE_NAME} SET completed = 1 WHERE id = ?"
        self.cursor.execute(sql, (task_id,))
        #Guardamos los cambios
        self.conn.commit()


    def contains_task(self, task_id):
        sql = f"SELECT COUNT(id) FROM {self.TABLE_NAME} WHERE id = ?"
        #Ejecutamos la consulta
        self.cursor.execute(sql, (task_id,))
        #Recuperamos lo obtenido
        count = self.cursor.fetchone()[0]
        return count > 0
        
    
    def is_completed(self, task_id):
        self.assert_is_valid_task_id(task_id)
        sql = f"SELECT completed FROM {self.TABLE_NAME} WHERE id = ?"
        self.cursor.execute(sql, (task_id,))
        #Obtenemos el resultado (recordemos que el False se guarda como un 0)
        completed_int  = self.cursor.fetchone()[0]
        return completed_int == 1
    
    def tasks_count(self):
        #Contamos las f{self.TABLE_NAME} totales
        sql = f"SELECT COUNT(*) FROM {self.TABLE_NAME}"
        #Ejecutamos
        self.cursor.execute(sql)
        
        count = self.cursor.fetchone()[0]
        return count
    
    #Assert methods
    def assert_is_valid_task_id(self, task_id):
        if not self.contains_task(task_id):
            raise TaskNotFoundError(task_id)