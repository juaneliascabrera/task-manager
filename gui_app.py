import tkinter as tk
from tkinter import messagebox, simpledialog
from datetime import datetime
from typing import Optional

# Importamos las clases clave de tu proyecto
# Asegúrate de que este path sea correcto
from src.task_manager import (
    TaskManager, AuthenticationError, UsernameAlreadyExistsError, 
    TaskNotFoundError, UserIdNotFoundError, UsernameNotFoundError, Task
)
from src.task_repository import TaskRepository
from src.clock_implementations import SystemClock 
from src.cli_facade import TaskManagerCliFacade 

# --- CONFIGURACIÓN GLOBAL ---
DB_NAME = 'elias_taskmanager_v2.db'
DATE_FORMAT = '%Y-%m-%d'

def setup_application():
    """Configura e inyecta todas las dependencias."""
    clock = SystemClock()
    repository = TaskRepository(DB_NAME, clock, memory=False) 
    manager = TaskManager(repository)
    facade = TaskManagerCliFacade(manager) 
    return facade, repository

class TaskManagerGUI(tk.Tk):
    def __init__(self, facade: TaskManagerCliFacade, repository: TaskRepository):
        super().__init__()
        self.title("Sistema de Gestión de Tareas v2")
        self.geometry("800x600")
        
        self.facade = facade
        self.repository = repository
        self.current_user = None # Guarda el nombre del usuario logueado
        
        self.frames = {}
        for F in (LoginPage, TaskPage):
            page_name = F.__name__
            frame = F(parent=self, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.show_frame("LoginPage")

    def show_frame(self, page_name: str):
        frame = self.frames[page_name]
        frame.tkraise()
        if page_name == "TaskPage":
            frame.load_tasks()

    def login(self, username: str):
        try:
            # Intenta obtener el ID; si falla, el usuario no existe.
            self.facade.manager.get_user_id_by_username(username)
            self.current_user = username
            self.show_frame("TaskPage")
        except UsernameNotFoundError:
            if messagebox.askyesno("Usuario no encontrado", f"El usuario '{username}' no existe. ¿Desea crearlo?"):
                try:
                    self.facade.create_user(username)
                    self.current_user = username
                    messagebox.showinfo("Éxito", f"Usuario '{username}' creado exitosamente.")
                    self.show_frame("TaskPage")
                except UsernameAlreadyExistsError as e:
                    messagebox.showerror("Error", str(e))
                except Exception as e:
                    messagebox.showerror("Error", f"Error al crear usuario: {e}")
            
    def logout(self):
        self.current_user = None
        self.show_frame("LoginPage")

# --- LOGIN PAGE ---
class LoginPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Centrar el contenido
        container = tk.Frame(self)
        container.place(relx=0.5, rely=0.5, anchor='center')
        
        tk.Label(container, text="INICIAR SESIÓN / REGISTRAR", font=('Arial', 16, 'bold')).pack(pady=20)
        
        tk.Label(container, text="Usuario:", font=('Arial', 12)).pack(pady=5)
        self.username_entry = tk.Entry(container, width=30)
        self.username_entry.pack(pady=5)
        
        tk.Button(container, text="Entrar", command=self.attempt_login, width=20).pack(pady=10)

    def attempt_login(self):
        username = self.username_entry.get().strip()
        if username:
            self.controller.login(username)
        else:
            messagebox.showwarning("Advertencia", "Por favor, introduce tu nombre de usuario.")


# --- TASK PAGE ---
class TaskPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.task_map = {} # {id: Task object} para mapear la lista
        
        tk.Label(self, text="MIS TAREAS PENDIENTES", font=('Arial', 14, 'bold')).pack(pady=10)
        self.user_label = tk.Label(self, text="", font=('Arial', 10))
        self.user_label.pack()

        # Frame de la lista de tareas
        list_frame = tk.Frame(self)
        list_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.task_list = tk.Listbox(list_frame, height=10, width=80, font=('Courier', 10))
        self.task_list.pack(side="left", fill="both", expand=True)
        
        scrollbar = tk.Scrollbar(list_frame, orient="vertical")
        scrollbar.config(command=self.task_list.yview)
        scrollbar.pack(side="right", fill="y")
        self.task_list.config(yscrollcommand=scrollbar.set)
        
        # Frame para botones de acción
        action_frame = tk.Frame(self)
        action_frame.pack(pady=10)
        
        # BOTONES DE ACCIÓN PARA TOGGLE
        tk.Button(action_frame, text="Crear", command=self.open_create_dialog).pack(side="left", padx=5)
        tk.Button(action_frame, text="Completar", command=self.complete_task).pack(side="left", padx=5)
        tk.Button(action_frame, text="Alternar Prioridad", command=lambda: self.toggle_flag('priority')).pack(side="left", padx=5)
        tk.Button(action_frame, text="Alternar Recurrencia", command=lambda: self.toggle_flag('recurrency')).pack(side="left", padx=5)
        tk.Button(action_frame, text="Listar Prioritarias", command=self.list_priority_tasks).pack(side="left", padx=5)
        tk.Button(action_frame, text="Cerrar Sesión", command=self.controller.logout).pack(side="left", padx=5)
        tk.Button(action_frame, text="Recargar", command=self.load_tasks).pack(side="left", padx=5)


    def load_tasks(self, priority_mode: bool = False):
        """Carga y muestra las tareas pendientes del usuario actual."""
        username = self.controller.current_user
        self.user_label.config(text=f"Sesión: {username} {'(MODO PRIORIDAD)' if priority_mode else ''}")
        self.task_list.delete(0, tk.END)
        
        try:
            if priority_mode:
                tasks = self.controller.facade.list_priority_tasks(username)
            else:
                tasks = self.controller.facade.list_pending_tasks(username)

            self.task_map = {} 
            
            for task in tasks:
                task_id = task.get_id()
                due_date_str = task.get_due_date().strftime(DATE_FORMAT) if task.get_due_date() else 'N/A'
                
                # AÑADIMOS INDICADORES VISUALES
                priority_flag = "⭐" if task.is_priority() else " "
                # CORREGIDO para usar el método is_recurrency()
                recurrent_flag = "🔁" if task.is_recurrency() else " " 
                recurrency_days = 0
                if task.is_recurrency():
                    recurrency_days = task.recurrency_days
                else:
                    recurrency_days = 0
                display_text = f"[{task_id:4}] {priority_flag} {recurrent_flag} {recurrency_days} | VENCE: {due_date_str:10} | {task.get_description()}"
                self.task_list.insert(tk.END, display_text)
                self.task_map[task_id] = task
                
        except Exception as e:
            messagebox.showerror("Error de Carga", f"No se pudieron cargar las tareas: {e}")

    def list_priority_tasks(self):
        """Muestra solo las tareas prioritarias pendientes."""
        self.load_tasks(priority_mode=True)
        
    def get_selected_task_id(self) -> Optional[int]:
        selection = self.task_list.curselection()
        if not selection:
            messagebox.showwarning("Advertencia", "Selecciona una tarea de la lista.")
            return None
        
        # El ID está en los primeros caracteres: [ID: XXXX]
        selected_text = self.task_list.get(selection[0])
        # Intentamos obtener el número entre corchetes
        try:
            task_id_str = selected_text.split('[')[1].split(']')[0].strip()
            task_id = int(task_id_str)
            return task_id
        except IndexError:
            messagebox.showerror("Error", "No se pudo parsear el ID de la tarea seleccionada.")
            return None
        except ValueError:
            messagebox.showerror("Error", "ID de tarea no válido.")
            return None
        
    def complete_task(self):
        task_id = self.get_selected_task_id()
        if task_id is None: return

        username = self.controller.current_user
        if messagebox.askyesno("Confirmar", f"¿Completar tarea {task_id}?"):
            try:
                self.controller.facade.complete_task(username, task_id)
                messagebox.showinfo("Éxito", f"Tarea {task_id} marcada como completada.")
                self.load_tasks() 
            except (AuthenticationError, TaskNotFoundError) as e:
                messagebox.showerror("Error de Acción", str(e))
                
    def toggle_flag(self, flag_name: str):
        """Método unificado para alternar el estado de prioridad o recurrencia."""
        task_id = self.get_selected_task_id()
        if task_id is None: return

        username = self.controller.current_user
        
        try:
            if flag_name == 'priority':
                self.controller.facade.update_task_priority(username, task_id)
                action = "Prioridad"
            elif flag_name == 'recurrency':
                self.controller.facade.update_task_recurrency(username, task_id)
                action = "Recurrencia"
            else:
                return

            messagebox.showinfo("Éxito", f"{action} de tarea {task_id} alternada.")
            self.load_tasks() # Recargar la lista para ver el cambio
            
        except (AuthenticationError, TaskNotFoundError, UserIdNotFoundError) as e:
            messagebox.showerror("Error de Seguridad", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Error al alternar {flag_name}: {e}")

    def open_create_dialog(self):
        CreateTaskDialog(self, self.controller)


# --- DIÁLOGO DE CREACIÓN DE TAREA (Actualizado) ---
class CreateTaskDialog(simpledialog.Dialog):
    def __init__(self, parent, controller):
        self.controller = controller
        super().__init__(parent, "Crear Nueva Tarea")

    def body(self, master):
        tk.Label(master, text="Descripción:").grid(row=0, sticky="w", pady=5)
        self.description_entry = tk.Entry(master, width=40)
        self.description_entry.grid(row=0, column=1)

        tk.Label(master, text="Fecha de Vencimiento (YYYY-MM-DD):").grid(row=1, sticky="w", pady=5)
        self.due_date_entry = tk.Entry(master, width=40)
        self.due_date_entry.grid(row=1, column=1)
        
        # CAMPO DE PRIORIDAD
        self.priority_var = tk.BooleanVar()
        tk.Checkbutton(master, text="Marcar como Prioritaria", variable=self.priority_var).grid(row=2, columnspan=2, sticky="w")
        
        # NUEVOS CAMPOS DE RECURRENCIA
        self.recurrency_var = tk.BooleanVar()
        tk.Checkbutton(master, text="Tarea Recurrente", variable=self.recurrency_var).grid(row=3, columnspan=2, sticky="w")

        tk.Label(master, text="Días de Recurrencia (>0):").grid(row=4, sticky="w", pady=5)
        self.recurrency_days_entry = tk.Entry(master, width=10)
        self.recurrency_days_entry.grid(row=4, column=1, sticky="w")
        self.recurrency_days_entry.insert(0, "0") # Valor por defecto 0
        
        return self.description_entry # Foco inicial

    def apply(self):
        description = self.description_entry.get().strip()
        due_date_str = self.due_date_entry.get().strip()
        priority = self.priority_var.get()
        recurrency = self.recurrency_var.get()
        recurrency_days_str = self.recurrency_days_entry.get().strip()
        
        due_date = None
        recurrency_days = None

        if not description:
            messagebox.showerror("Error", "La descripción de la tarea no puede estar vacía.")
            return

        if due_date_str:
            try:
                due_date = datetime.strptime(due_date_str, DATE_FORMAT)
            except ValueError:
                messagebox.showerror("Error", f"Formato de fecha inválido. Usa {DATE_FORMAT}.")
                return
        
        # LÓGICA DE VALIDACIÓN DE RECURRENCIA
        if recurrency:
            try:
                days = int(recurrency_days_str)
                if days <= 0:
                    messagebox.showerror("Error", "Los Días de Recurrencia deben ser un número entero mayor a 0.")
                    return
                recurrency_days = days
            except ValueError:
                messagebox.showerror("Error", "Días de Recurrencia debe ser un número entero válido.")
                return
        
        # Si no es recurrente, aseguramos que recurrency_days sea None o 0
        elif not recurrency:
            recurrency_days = 0 


        try:
            # NOTA: Asumimos que cli_facade.create_task ahora acepta los argumentos recurrency y recurrency_days
            self.controller.facade.create_task(
                username=self.controller.current_user,
                description=description,
                due_date=due_date,
                priority=priority,
                recurrency=recurrency,
                recurrency_days=recurrency_days # Pasamos la cantidad de días al Manager
            )
            messagebox.showinfo("Éxito", "Tarea creada exitosamente.")
            self.controller.frames["TaskPage"].load_tasks()
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear la tarea: {e}")


# --- EJECUCIÓN ---
if __name__ == '__main__':
    facade, repo = setup_application()
    try:
        app = TaskManagerGUI(facade, repo)
        app.mainloop()
    finally:
        print(f"Cerrando conexión a la base de datos: {DB_NAME}")
        repo.close()