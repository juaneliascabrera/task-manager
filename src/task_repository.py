#Patrón "REPOSITORY"
import sqlite3
from datetime import datetime
from .task_manager import Task
from src.repository_interface import AbstractRepository
class TaskRepository(AbstractRepository):
    # -- CONSTANTS -- 
    TABLE_NAME = 'tasks'
    USERS_TABLE_NAME = 'users'
    # Constructor
    def __init__(self, db_name, clock, memory = False):
        #Conexión
        if memory:
            self.conn = sqlite3.connect(':memory:')
        else:
            self.conn = sqlite3.connect(db_name)
        #Cursor
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        #Inicializamos la tabla
        self._create_table()
        #Guardamos el reloj
        self.clock = clock

    #Create table method
    def _create_table(self):   
        "Creamos la tabla si no existe"
        self.cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {self.TABLE_NAME} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER not NULL,
                description TEXT NOT NULL,
                completed BOOLEAN NOT NULL DEFAULT 0,
                due_date TEXT NULL
            )
        """)
        self.cursor.execute(f"""
           CREATE TABLE IF NOT EXISTS {self.USERS_TABLE_NAME} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE                
            )                 
        """)
        self.conn.commit()
    #CLose connection
    def close(self):
        self.conn.close()
    #Auxiliar methods to avoid repeated code
    def create_task_by_row(self, row):
        return Task(
            id=row['id'],
            user_id = row['user_id'],
            description=row['description'],
            #Convertimos el 0/1 a True/False
            completed=(row['completed'] == 1),
            due_date = self._from_db_format(row['due_date'])
        )

    def create_tasks_by_rows(self, rows):
        tasks = []
        for row in rows:
            #Recordemos que usamos Row
            task = self.create_task_by_row(row)
            tasks.append(task)
        return tasks

    def _to_db_format(self, due_date_python):
        if due_date_python is None:
            return None
        return due_date_python.isoformat(' ')
    
    def _from_db_format(self, due_date_db):
        if due_date_db is None:
            return None
        return datetime.fromisoformat(due_date_db)

    def _get_count_by_id(self, table_name, id):
        #Contamos las f{self.USERS_TABLE_NAME} totales
        sql = f"SELECT COUNT(*) FROM {table_name} WHERE id = ?"
        #Ejecutamos
        self.cursor.execute(sql, (id,))
        count = self.cursor.fetchone()[0]
        return count

    # USER CRUD
    def add_user(self, user_str):
        #SQL
        sql = f"INSERT INTO {self.USERS_TABLE_NAME} (username) VALUES (?)"
        try:
            self.cursor.execute(sql, (user_str,))
        except sqlite3.Error as e:
            #Handleamos
            print(f"Error al insertar el usuario {e}")
            raise
        #Guardamos
        self.conn.commit()
        #Conseguimos el ID y lo devolvemos
        generated_id = self.cursor.lastrowid
        return generated_id
    
    def users_count(self):
        #Contamos las f{self.USERS_TABLE_NAME} totales
        sql = f"SELECT COUNT(*) FROM {self.USERS_TABLE_NAME}"
        #Ejecutamos
        self.cursor.execute(sql)
        count = self.cursor.fetchone()[0]
        return count
    
    def contains_user(self, user_id):
        sql = f"SELECT COUNT(id) FROM {self.USERS_TABLE_NAME} WHERE id = ?"
        #Ejecutamos la consulta
        self.cursor.execute(sql, (user_id,))
        #Recuperamos lo obtenido
        count = self.cursor.fetchone()[0]
        return count > 0
    
    #CRUD DE TAREAS
    #1. Create
    def add_task_by_user_id_global(self, description, user_id, due_date=None):
        #La fecha nos vino como un datetime, tenemos que transformarla a ISO
        due_date_iso = self._to_db_format(due_date)
        sql = f"INSERT INTO {self.TABLE_NAME} (user_id, description, completed, due_date) VALUES (?, ?, ?, ?)"
        try:
            self.cursor.execute(sql, (user_id, description, 0, due_date_iso))
        except sqlite3.Error as e:
            #Handleamos
            print(f"Error al insertar la tarea {e}")
            raise
        #Guardamos los cambios
        self.conn.commit()
        #Handleamos el id
        generated_id = self.cursor.lastrowid

        return generated_id
    #2. Read
    def get_task_by_id_global(self, task_id):
        sql = f"SELECT id, user_id, description, completed, due_date FROM {self.TABLE_NAME} WHERE id = ?"
        #Ejecutamos
        self.cursor.execute(sql, (task_id,))
        #Fetcheamos el resultado obtenido
        fetched_task = self.cursor.fetchone()
        #Construimos el objeto tarea a partir de esto
        task = self.create_task_by_row(fetched_task)
        return task
    
    def get_pending_tasks_by_user_id_global(self, user_id=None):
        if user_id == None:
            sql = f"SELECT id, description, completed, due_date FROM {self.TABLE_NAME} WHERE completed = 0"    
            self.cursor.execute(sql)
        else:
            sql = f"SELECT id, user_id, description, completed, due_date FROM {self.TABLE_NAME} WHERE completed = 0 AND user_id = ?"
            self.cursor.execute(sql, (user_id,))
        #Conseguimos todos los resultados
        rows = self.cursor.fetchall()
        pending_tasks = self.create_tasks_by_rows(rows)
        return pending_tasks
    
    def get_overdue_tasks_by_user_id_global(self, user_id):
        #Obtenemos el ahora y lo transformamos en db_format
        now_time = self.clock.now()
        now_str = self._to_db_format(now_time)

        #sql
        sql = f"""
        SELECT id, user_id, description, completed, due_date FROM {self.TABLE_NAME}
        WHERE completed = 0
        AND user_id = ?
        AND due_date IS NOT NULL
        AND due_date < ?
        """
        #Ejecutamos
        self.cursor.execute(sql, (user_id, now_str))
        #Obtenemos el resultado
        rows = self.cursor.fetchall()
        overdue_tasks = self.create_tasks_by_rows(rows)
        return overdue_tasks

    #3. Update
    def complete_task_global(self, task_id):
        sql = f"UPDATE {self.TABLE_NAME} SET completed = 1 WHERE id = ?"
        self.cursor.execute(sql, (task_id,))
        #Guardamos los cambios
        self.conn.commit()
        
    def update_task_due_date_global(self, task_id, new_due_date):
        #SQL
        sql = f"UPDATE {self.TABLE_NAME} SET due_date = ? WHERE id = ?"
        #Conseguimos la fecha según formato correcto
        new_due_date_db = self._to_db_format(new_due_date)
        self.cursor.execute(sql, (new_due_date_db, task_id))
        #Guardamos los cambios
        self.conn.commit()

    def update_task_description_global(self, task_id, new_description):
        #SQL
        sql = f"UPDATE {self.TABLE_NAME} SET description = ? WHERE id = ?"
        self.cursor.execute(sql, (new_description, task_id))
        #Guardamos los cambios
        self.conn.commit()

    #4. Delete
    def delete_task_global(self, task_id):
        sql = f"DELETE FROM {self.TABLE_NAME} WHERE id = ?"
        self.cursor.execute(sql, (task_id,))
        #Guardamos los cambios
        self.conn.commit()
    
    #State
    def contains_task_by_user_id(self, task_id, user_id=None):
        if user_id == None:
            sql = sql = f"SELECT COUNT(id) FROM {self.TABLE_NAME} WHERE id = ?"
            self.cursor.execute(sql, (task_id,))
        else:
            sql = f"SELECT COUNT(id) FROM {self.TABLE_NAME} WHERE id = ? AND user_id = ?"
            self.cursor.execute(sql, (task_id, user_id))
        #Recuperamos lo obtenido
        count = self.cursor.fetchone()[0]
        return count > 0

    def task_is_completed(self, task_id):
        sql = f"SELECT completed FROM {self.TABLE_NAME} WHERE id = ?"
        self.cursor.execute(sql, (task_id,))
        #Obtenemos el resultado (recordemos que el False se guarda como un 0)
        completed_int  = self.cursor.fetchone()[0]
        return completed_int == 1

    def tasks_count_by_user_id(self, user_id):
        #Contamos las f{self.USERS_TABLE_NAME} totales
        sql = f"SELECT COUNT(*) FROM {self.TABLE_NAME} WHERE user_id = ?"
        #Ejecutamos
        self.cursor.execute(sql, (user_id,))
        count = self.cursor.fetchone()[0]
        return count
