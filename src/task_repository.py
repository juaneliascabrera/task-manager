#Patrón "REPOSITORY"
import sqlite3
from datetime import datetime
from .task_manager import Task
class TaskRepository:
    TABLE_NAME = 'tasks'
    def __init__(self, db_name, clock):
        #Conexión
        self.conn = sqlite3.connect(db_name)
        #Cursor
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        #Inicializamos la tabla
        self._create_table()
        #Guardamos el reloj
        self.clock = clock

    def _create_table(self):   
        "Creamos la tabla si no existe"
        self.cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {self.TABLE_NAME} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT NOT NULL,
                completed BOOLEAN NOT NULL DEFAULT 0,
                due_date TEXT NULL
            )
        """)
        self.conn.commit()
    
    def close(self):
        self.conn.close()

    def create_task_by_row(self, row):
        return Task(
            id=row['id'],
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

    def add_task(self, description, due_date=None):
        #La fecha nos vino como un datetime, tenemos que transformarla a ISO
        due_date_iso = self._to_db_format(due_date)
        sql = f"INSERT INTO {self.TABLE_NAME} (description, completed, due_date) VALUES (?, ?, ?)"
        try:
            self.cursor.execute(sql, (description, 0, due_date_iso))
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
        sql = f"DELETE FROM {self.TABLE_NAME} WHERE id = ?"
        self.cursor.execute(sql, (task_id,))
        #Guardamos los cambios
        self.conn.commit()

    def get_task_by_id(self, task_id):
        sql = f"SELECT id, description, completed, due_date FROM {self.TABLE_NAME} WHERE id = ?"
        #Ejecutamos
        self.cursor.execute(sql, (task_id,))
        #Fetcheamos el resultado obtenido
        fetched_task = self.cursor.fetchone()
        #Construimos el objeto tarea a partir de esto
        task = self.create_task_by_row(fetched_task)
        return task
    def get_pending_tasks(self):
        sql = f"SELECT id, description, completed, due_date FROM {self.TABLE_NAME} WHERE completed = 0"
        #Ejecutamos
        self.cursor.execute(sql)
        #Conseguimos todos los resultados
        rows = self.cursor.fetchall()
        pending_tasks = self.create_tasks_by_rows(rows)
        return pending_tasks
    def complete_task(self, task_id):
        sql = f"UPDATE {self.TABLE_NAME} SET completed = 1 WHERE id = ?"
        self.cursor.execute(sql, (task_id,))
        #Guardamos los cambios
        self.conn.commit()

    def get_overdue_tasks(self):
        #Obtenemos el ahora y lo transformamos en db_format
        now_time = self.clock.now()
        now_str = self._to_db_format(now_time)

        #sql
        sql = f"""
        SELECT id, description, completed, due_date FROM {self.TABLE_NAME}
        WHERE completed = 0
        AND due_date IS NOT NULL
        AND due_date < ?
        """
        #Ejecutamos
        self.cursor.execute(sql, (now_str,))
        #Obtenemos el resultado
        rows = self.cursor.fetchall()
        overdue_tasks = self.create_tasks_by_rows(rows)
        return overdue_tasks

    def contains_task(self, task_id):
        sql = f"SELECT COUNT(id) FROM {self.TABLE_NAME} WHERE id = ?"
        #Ejecutamos la consulta
        self.cursor.execute(sql, (task_id,))
        #Recuperamos lo obtenido
        count = self.cursor.fetchone()[0]
        return count > 0
    def task_is_completed(self, task_id):
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